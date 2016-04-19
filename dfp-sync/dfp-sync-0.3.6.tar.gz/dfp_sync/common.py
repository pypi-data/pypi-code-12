import re
import time
from datetime import datetime
from functools import partial
from traceback import format_exc 
import json

# Import appropriate modules from the client library.
import pytz
from googleads import dfp
from suds import MethodNotFound, WebFault
from suds.sax.text import Text
import transpose

from dfp_sync import utils


class DFPService:
  """
  An abstract wrapper for connecting to a DFP Service via API.
  """

  VERSION = 'v201511'

  # the list of services that downloadable from DFP.
  SERVICES = [
    'AdUnit',
    # 'AdUnitSize',
    'ActivityGroup', 
    'Activity',
    'AdExclusionRule',
    'AdRule', 
    'AudienceSegment', 
    'BaseRate',
    'Company', 
    'Contact', 
    'ContentBundle',
    'ContentMetadataKeyHierarchy',
    'Content',
    'Creative',
    'CreativeSet',
    'CreativeTemplate',
    'CreativeWrapper',
    'CustomField',
    # 'CustomTargeting',
    # 'ExchangeRate',
    # 'Forecast',
    # 'Inventory',
    'Label',
    'LineItemCreativeAssociation',
    'LineItem',
    'LineItemTemplate',
    # 'LiveStreamEvent',
    'Network',
    'Order',
    # 'Package',
    'Placement',
    'PremiumRate',
    'Product',
    # 'ProductPackage',
    # 'ProductPackageItem',
    # 'ProductTemplate',
    'ProposalLineItem',
    'Proposal',
    # 'PublisherQueryLanguage',
    'RateCard',
    # 'ReconciliationOrderReport',
    # 'ReconciliationReportRow',
    # 'ReconciliationLineItemReport',
    # 'ReconciliationReport',
    # 'Report',
    'SharedAdUnit',
    'SuggestedAdUnit',
    'Team',
    'User',
    'UserTeamAssociation'
    # 'WorkflowRequest'
  ]

  NULL_DICT_FIELDS = [
  'targeting', 'technology_targeting'
  ]

  def __init__(self, name, config, **kw):
    self.client = dfp.DfpClient.LoadFromStorage(config)
    self.version = kw.get('version', self.VERSION)
    self.table_name = utils.no_camel(name)
    self._set_method_and_service(name)
    self.service = self.client.GetService(
      self.name, version=self.version)
    self.schema = transpose.new(title=self.table_name)
    self.field_types = {}

  def get_records(self, **kw):
    """
    Query statement with a filter, parsing response into a stream of simple, flat python dictionaries,
    and optionally paginating through resultset
    """
    kw.setdefault('where', None)
    kw.setdefault('max_retries', 3)
    kw.setdefault('backoff', 4.2) # factor by which to increment sleep between retries.
    kw.setdefault('page', True)
    kw.setdefault('limit', None)
    kw.setdefault('offset', 0)
    

    # Create statement object to select all items
    if not kw['where']:
      statement = dfp.FilterStatement()
    else:
      statement = dfp.FilterStatement(kw['where'])

    # setoffset 
    statement.offset = kw['offset']

    # set limit 
    if kw['limit'] and kw['limit'] < dfp.SUGGESTED_PAGE_LIMIT:
      statement.limit = dfp.SUGGESTED_PAGE_LIMIT

    # Get method for fetching items by ststement
    try:
      method = getattr(self.service, self.q_method)
    
    except MethodNotFound as e:
      sys.stderr.write("ERROR:\n{0} \nTRACEBACK:\n{1}\n"\
                       .format(e.message, format_exc()))
      return []
    
    except WebFault as e:
      sys.stderr.write("ERROR:\n{0} \nTRACEBACK:\n{1}\n"\
                       .format(e.message, format_exc()))
      return []
    
    return self._exec_statement(method, statement, **kw)

  def get_n_records(self):
      """
      get the number of records available.
      """

      # Get method for fetching items by ststement
      try:
        method = getattr(self.service, self.q_method)
      
      except MethodNotFound as e:
        sys.stderr.write("ERROR:\n{0} \nTRACEBACK:\n{1}\n"\
                         .format(e.message, format_exc()))
        raise e
      
      except WebFault as e:
        sys.stderr.write("ERROR:\n{0} \nTRACEBACK:\n{1}\n"\
                         .format(e.message, format_exc()))
        raise e

      if not self.accepts_statment:
        response = method()

      else:
        response = method(dfp.FilterStatement().ToStatement())

      if response and 'totalResultSetSize' in response:
        return response['totalResultSetSize']
      return None

  def _exec_statement(self, method, statement, **kw):
      """
      fetch a dfp statement, optionally paginating through resultset
      """
      
      def _exec(statement):    
        
        if not self.accepts_statment:
          response = method()
        else:
          response = method(statement.ToStatement())
        return self._parse_response(response, **kw)
      
      # fetch first result set
      if not kw['page']:
        for result in self._retry_statement(_exec, statement, **kw):
          yield result

      # paginate
      else:    
        total_results = 0

        while True:

          # check for requsted limit
          if kw['limit'] & total_results >= kw['limit']:
            break

          results = self._retry_statement(_exec, statement, **kw)

          # check for end of results
          if not len(results):
            break

          # yield results and count
          n_results = 0
          for result in results:
            n_results += 1
            yield result
          
          # generate next statement
          total_results += n_results
          statement.offset += n_results

  def _retry_statement(self, fn, statement, **kw):
    """
    Retry a function with backoff and err raising.
    """
    tries = 0
    
    # fetch results with retries
    while True:
      tries += 1
      
      try:
        return fn(statement)
      
      except Exception as e:
        
        if tries > kw['max_retries']:
          msg = "ERROR after {max_retries} tries:\n{0}\n{1}\n"\
                .format(format_exc(), e.message, **kw)
          sys.stderr.write(msg)
          raise RuntimeError(msg)
      
        print("WARNING on try {0} of {max_retries}: {1}"\
              .format(tries, format_exc(), **kw))
        
        time.sleep(tries * kw['backoff'])

  def _parse_response(self, response, **kw):
    """
    Parse a response into individual records.
    """

    if not response:
      return []
    if 'results' not in response and isinstance(response, list):
      results = response
    else:
      results = getattr(response, 'results', [])
    records = []
    for r in results:
      r = self._parse_record(r)
      self.schema.update(r)
      records.append(r)
    return records

  def _parse_record(self, record, parent_key=""):
    """
    Recursively parse a Suds record into a simple dictionary.
    """
    nu = {}
    for key in dir(record):
      
      # ignore internal methods
      if key.startswith('_'): 
        continue 
              
      # get an attribute.
      attr = getattr(record, key, None)

      # standardize and flatten key
      key = utils.no_camel(key)

      # check nulls and determine default
      if not attr:
        if key in self.NULL_DICT_FIELDS:
          nu[key] = {}
        else:
          nu[key] = None

      # parse datetime fields  -- this is ugly.
      elif hasattr(attr, '__class__') and 'DateTime' in attr.__class__.__name__:
        nu[key] = self._parse_date_time(attr)

      elif hasattr(attr, '__class__') and 'Text' in attr.__class__.__name__:
        nu[key] = unicode(attr)

      # recurse on suds models -- this is ugobly.
      elif hasattr(attr, '__module__') and attr.__module__ and 'sudsobject' in attr.__module__:
        val = self._parse_record(attr, parent_key=key)
        if not val:
          val = {}
        nu[key] = val

      # parse lists
      elif isinstance(attr, list):
        nu[key] = []
        for r in attr:
          val = self._parse_record(r)
          if not val:
            val = {}
          if len(val.keys()):
            nu[key].append(val)

      # passthrough simple/null fields    
      elif not attr or isinstance(attr, (int, float, bool, long, str, unicode)):
        nu[key] = attr

      # final check for errant nulls:
      if key in nu and str(nu[key]).upper() == 'NONE': 
        nu[key] = None
    return nu

  def _parse_date_time(self, obj):
    """
    Parse a suds.sudsobject.DateTime object into an isoformat string.
    """
    return datetime(
        year = obj.date.year,
        month = obj.date.month,
        day = obj.date.day,
        hour = obj.hour,
        minute = obj.minute,
        second = obj.second,
        tzinfo=pytz.timezone(obj.timeZoneID)
      ).isoformat()

  def _set_method_and_service(self, name):
    """
    bespoke hacks for auto-generating correct 
    service name and query method
    """ 

    self.name = "{0}Service".format(name)
    self.q_method = 'get{0}sByStatement'.format(name)
    self.accepts_statment = True
    
    if 'ys' in self.q_method:
      self.q_method = self.q_method.replace('ys', 'ies')
    
    if 'Contents' in self.q_method:
      self.q_method = self.q_method.replace('Contents', 'Content')
    
    if 'Network' in self.name:
      self.q_method = 'getAllNetworks'
      self.accepts_statment = False

    if name.startswith('AdUnit'):
      self.name = "InventoryService"
