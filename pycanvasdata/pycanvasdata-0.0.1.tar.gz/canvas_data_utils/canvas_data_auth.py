#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib, dateutil.parser, base64, hmac
import requests, os, sys, json
import csv, gzip, re,  glob

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, Boolean, DATE, DATETIME, FLOAT, BigInteger, BIGINT, TIMESTAMP, TEXT, ForeignKey
from sqlalchemy.dialects import postgresql, mysql, sqlite
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
from datetime import datetime
from tabulate import tabulate

try:
  import ConfigParser
except ImportError:
  import configparser as ConfigParser

try:
  from urllib import urlencode
except:
  # For Python 3
  from urllib.parse import urlencode

from canvas_data_utils.logger import logger

# This pattern is used to recognize table names in the downloaded files
tablename_pattern = re.compile('([a-z_]+)')

# This dictionary represents the required configuration options
required_sections = {
    'security':('API_SECRET','API_KEY'),
    'folders':('base_folder','data_folder')
}

CANVAS_DATA_AUTH_SCHEME_TMPL = '''GET
api.inshosteddata.com


{0[resource_path]}
{0[args]}
{0[date]}
{0[API_secret]}'''

odd_table_mapping = {
    'account_dim':'account',
    'course_dim':'course',
    'course_section_dim':'course_section',
    'enrollment_rollup_dim':'enrollment_rollup',
    'enrollment_term_dim':'enrollment_term',
    'user_dim':'user',
    'conversation_dim':'conversation',
    'conversation_message_dim':'conversation_message',
    'conversation_message_participant_fact':'conversation_message_participant',
    }

# These tables don't have a field called "id"
DIM_TABLES_WITHOUT_ID = ('assignment_rule_dim','assignment_group_rule_dim','conversation_message_participant')

# These tables need a composite key
DIM_TABLES_WITH_COMPOSITE_KEY = {
    'quiz_question_answer_dim':{'keys':('id','quiz_question_id')},
    'submission_dim':{'keys':('id','canvas_id')}
}

# Maps the column type from the CanvasData type to an SQLAlchemy type
COLUMN_TYPE_MAPPING = {
  u'bigint': BIGINT,
  u'boolean': Boolean,
  u'date': DATE,
  u'datetime': DATETIME,
  u'double precision': FLOAT,
  u'int': Integer,
  u'integer': Integer,
  u'text': TEXT(convert_unicode=True),
  u'timestamp': TIMESTAMP,
  u'varchar': String(256, convert_unicode=True),
  u'guid': String(256, convert_unicode=True),
  u'enum': String(256, convert_unicode=True)
}

# Used to map a dialect string to an SQLAlchemy dialect object
DIALECT_MAP = {
    'postgresql':postgresql,
    'mysql':mysql,
    'sqlite':sqlite
    }

class CanvasData(object):

  def __init__(self, *args, **kwargs):

    self._schema = None

    self.base = None
    self.metadata = MetaData()
    self._md_run = False
    self._files_downloaded = False
    self._imported_files = None
    self.offline = kwargs.get('offline', False)
    config_defaults = {
        'security':{
          'API_SECRET':kwargs.get('API_SECRET',''), 
          'API_KEY':kwargs.get('API_KEY','')
        },
        'folders':{
          'base_folder':kwargs.get('base_folder'),
          'data_folder':kwargs.get('data_folder')
        }
    }
    self._config = ConfigParser.SafeConfigParser(os.environ)
    if kwargs.get('config_filename'):
      self.parse_config_file(kwargs.get('config_filename'))
      if self._config.get('database','connection_string'):
        self.set_connection(self._config.get('database','connection_string'))
    else:
      self.set_config_defaults(config_defaults)

  def set_config_defaults(self, defaults):
    for k in defaults.keys():
      self._config.add_section(k)
      for o in defaults[k].keys():
        self._config.set(k, o, defaults[k][o])

  def config_valid(self, config_filename):
    problems = []
    config = ConfigParser.ConfigParser(os.environ)
    if not os.path.exists(config_filename):
      problems.append('conf file {} does not exist'.format(config_filename))
    else:
      config.read(config_filename)
      for rs in required_sections:
        if not config.has_section(rs):
          problems.append('missing section {}'.format(rs))
        for option in required_sections[rs]:
          if not config.has_option(rs,option):
            problems.append('missing option {} in section {}'.format(option, rs))
      #self._config = config
    return config, len(problems)<1, problems

  def parse_config_file(self, config_filename):
    config, is_valid, problems = self.config_valid(config_filename)
    if is_valid:
      self._config = config
    return self._config

  @property
  def API_SECRET(self):
    return self._config.get('security', 'API_SECRET')

  @property
  def API_KEY(self):
    return self._config.get('security', 'API_KEY')

  @property
  def base_folder(self):
    return self._config.get('folders', 'base_folder')

  @property
  def data_folder(self):
    return self._config.get('folders', 'data_folder')

  def buildRequest(self,path,**kwargs):
    _date = datetime.utcnow().strftime('%a, %d %b %y %H:%M:%S GMT')
    print('_date', _date)
    return self._buildRequest(path, _date, **kwargs)

  def build_schema_header(self, path, _date, **kwargs):
    return CANVAS_DATA_AUTH_SCHEME_TMPL.format({
      'resource_path':path,
      'API_secret':self.API_SECRET,
      'args':urlencode(kwargs),
      'date':_date})

  def _buildRequest(self, path, _date, **kwargs):
    s = self.build_schema_header(path, _date)
    signature = base64.b64encode( 
        hmac.new(
          self.API_SECRET, 
          msg=s, 
          digestmod=hashlib.sha256).digest())
    headers = {
      'Authorization':'HMACAuth {}:{}'.format(self.API_KEY,signature),
      'Date':_date
      }
    return signature,_date,headers
    

  def fetch_schema(self):
    path = '/api/schema/latest'
    signature,_date,headers = self.buildRequest(path)
    url = 'https://api.inshosteddata.com{}'.format(path)
    schema = requests.get(url,headers=headers).json()
    return schema

  @property
  def schema(self):
    if not self._schema:
      schema_filename = os.path.join(self.base_folder, 'schema.json')
      if os.path.exists(schema_filename) and self.time_diff(os.path.getmtime(schema_filename)) < 24:
        self._schema = json.load(open(schema_filename,'rb'))
      else:
        self._schema = self.fetch_schema()
        json.dump(self._schema, open(schema_filename,'w+'), indent=2, separators=(',', ': '))
    return self._schema


  def time_diff(self,last_updated):
    last_updated = datetime.fromtimestamp(last_updated)
    day_period = last_updated.replace(day=last_updated.day+1, hour=1,
                                       minute=0, second=0,
                                       microsecond=0)
    delta_time = day_period - last_updated
    hours = delta_time.seconds // 3600
    # make sure a period of 24hrs have passed before shuffling
    return hours

  def get_schema_columns(self, schema):
    columns = []
    for c in self.schema['schema'][schema]['columns']:
      columns.append((c['name'], c['type']))
    return columns

  def get_schema_name(self, tsv):
    filename = tsv.split('/')[-1]
    schema_name = tablename_pattern.match(filename).group()

    schema_name = odd_table_mapping.get(schema_name, schema_name)

    return schema_name


  def convert_tsv_to_csv(self, tsv):
    
    logger.debug('converting {} to CSV'.format(tsv))
    schema_name = self.get_schema_name(tsv)

    cols = self.get_schema_columns(schema_name)
    headers = []
    for c in cols:
      headers.append(c[0])

    outfile = '{}.csv'.format(tsv)
    if os.path.exists(outfile):
      logger.debug('not converting {}, it is already done'.format(tsv))
    else:
      logger.debug('converting {} to CSV'.format(tsv))
      of = csv.writer(open(outfile, 'w+'))
      of.writerow(headers)
      with gzip.open(tsv) as f:
        gz_csv = csv.reader(f,delimiter='\t')
        for v in gz_csv:
          of.writerow(v)
      logger.debug('{} converted to'.format(tsv, outfile))
    return outfile

  def print_schema(self, schema=None, print_output = True):
    output = []
    if sys.version_info.major == 2:
      _iter = self.schema['schema'].iteritems()
    else:
      _iter = iter(self.schema['schema'].items())
    for key, schema_element in _iter:
      if not schema or key==schema:
        output.append('='*50)
        output.append('table: {0}, incremental:{1[incremental]}'.format(key,schema_element))
        headers = ['name','type', 'dim','description']
        rows = []
        for col in schema_element['columns']:
          desc = col.get('description','')[:30]
          rows.append([col['name'], col['type'], col.get('dimension'), desc])
        tabs = tabulate(rows, headers)
        output.append(tabs)
    if print_output:
      print('\n'.join(output))
    return '\n'.join(output)

  def query_to_table_str(self, table_name, query, headers=None):

    output = []
    output.append('\n')
    output.append('='*50)
    output.append(table_name)
    if not headers:
      headers = []
      try:
        for h in query.column_descriptions:
          headers.append(h['name'])
      except Exception as err:
        # Must be a raw ResultProxy
        headers = query.keys()

    try:
      rows = query.all()
    except Exception as err:
      # Must be a raw ResultProxy
      rows = query.fetchall()

    output.append(tabulate(rows, headers))
    return '\n'.join(output)

  def table_list(self):
    table_names = []
    if sys.version_info.major == 2:
      _iter = self.schema['schema'].iteritems()
    else:
      _iter = iter(self.schema['schema'].items())

    for key, schema_element in _iter:
      if key != 'course_ui_canvas_navigation_dim':
        table_names.append(key)
    return table_names

  def table_columns(self, schema_table, **kwargs):
    return self.schema['schema'][schema_table]['columns']

  def list_all_column_types(self):
    col_types = set()
    if sys.version_info.major == 2:
      _iter = self.schema['schema'].iteritems()
    else:
      _iter = iter(self.schema['schema'].items())

    for key, schema_element in _iter:
      for col in schema_element['columns']:
        #desc = col.get('description','')[:30]
        #rows.append([col['name'], col['type'], col.get('dimension'), desc])
        col_types.add(col['type'])
    return col_types

  def table_creation_statement(self, dialect='sqlite'):
    outputs = []
    metadata = MetaData()
    self.tables_md(metadata, force=True)

    def dump(sql, *multiparams, **params):
      outputs.append( str(sql.compile(dialect=engine.dialect)) )
    engine = create_engine('{}://'.format(dialect), strategy='mock', executor=dump)
    metadata.create_all(engine, checkfirst=False)
    return ';'.join(outputs)

  def tables_md(self, metadata=None, force=False):
    if not metadata:
      metadata = self.metadata

    if not self._md_run or force:
        

      for schema_table in self.table_list(): 
        table = Table(schema_table, metadata)
        last_f = schema_table[-4:]
        if last_f == 'fact' or schema_table in DIM_TABLES_WITHOUT_ID:
          # Add pseudoprimary_key
          column = Column('{}_rowid'.format(schema_table), 
              #BIGINT, 
              BigInteger().with_variant(sqlite.INTEGER(), 'sqlite'),
              primary_key=True, 
              autoincrement=True)
          table.append_column(column)

        col_num = 0
        for col in self.table_columns(schema_table):
          col_num+=1
          col_type = COLUMN_TYPE_MAPPING[col['type']]
          column = Column(col['name'], col_type)
          

          do_primary_key = False
          autoincrement = True
            
          comp_key = DIM_TABLES_WITH_COMPOSITE_KEY.get(schema_table, None)
          if comp_key and col['name'] in comp_key['keys']:
            do_primary_key = True
          elif col_num == 1 and col['name'] == 'id':
            do_primary_key = True
            if schema_table == 'requests':
              autoincrement=False

          if col.get('dimension') and col['dimension'].has_key('role'):
            if col['dimension']['role'] in self.table_list():
              foreign_key = '{role}.{id}'.format(**col['dimension'])
              column = Column(col['name'], col_type, ForeignKey(foreign_key), nullable=True)

          column.primary_key = do_primary_key
          if do_primary_key:
            column.autoincrement = autoincrement

          table.append_column(column)

      self.base = automap_base(metadata=metadata)
      self.base.prepare()
      self._md_run = True

  
  def create_tables(self, db_connect_string=None):
    '''creates all of the tables in the database'''
    if db_connect_string:
      self.set_connection(db_connect_string)
    self.tables_md()
    self.metadata.create_all(self.engine)

  def reset_database(self, db_connect_string=None):
    '''resets the database by dropping all known tables then recreating them.
    This method does _not_ import data.'''
    if db_connect_string:
      self.set_connection(db_connect_string)
    self.tables_md()
    self.metadata.drop_all(self.engine)

    # Re-create the tables
    self.create_tables()

    # Reset the imported files cache
    self._imported_files = set()
    self.save_imported_files()
    

  def set_connection(self, db_connect_string):
    self.metadata = MetaData()
    self.base = automap_base(metadata=self.metadata)
    self.engine = create_engine(db_connect_string)
    #self.engine.raw_connection().connection.text_factory = str

    self.session = sessionmaker(bind=self.engine)() 
    self.tables_md()

  def clear_table(self, schema_table):
    '''Delete all records from the table `schema_table`'''
    con = self.engine.connect()
    trans = con.begin()
    con.execute(self.metadata.tables[schema_table].delete())
    trans.commit()

  def normalize_values_for_db(self, obj, schema_table):
    '''normalizes some of the data for the database. For example, many fields
    come across with \\N representing a null value. This method changes that to
    `None` so it imports correctly into the database. 
    
    This method also ensures that floats are floats, integers are integers, 
    date fields have proper dates or are blank, etc. '''

    date_fields = ('submitted_at','created_at', 'updated_at','graded_at')
   
    cols = self.table_columns(schema_table)
    for c in cols:
      if c['type'] in ('date', 'datetime', 'timestamp'):
        field_value = getattr(obj, c['name'], None)
        if field_value:
          try:
            new_date = dateutil.parser.parse(field_value)
            setattr(obj, c['name'], new_date)
          except ValueError:
            setattr(obj, c['name'], None)
      elif c['type'] == 'boolean':
        field_value = getattr(obj, c['name'], None)
        if field_value != None:
          setattr(obj, c['name'], field_value == 'true')
      elif c['type'] == 'text' or c['type'] == 'varchar':
        field_value = getattr(obj, c['name'], None)
        if field_value == '\\\\N':
          field_value = None 

        if field_value != None and self.engine.name=='sqlite':
          setattr(obj, c['name'], field_value.decode('utf8'))
      elif c['type'] in ('bigint', 'int'):
        # Convert to proper integer value
        field_value = getattr(obj, c['name'], None)
        try:
          f = int(field_value)
        except:
          f = None
        setattr(obj, c['name'], f)
      elif c['type'] == 'double precision':
        # COnvert to proper float
        field_value = getattr(obj, c['name'], None)
        if field_value == '\\N':
          field_value = None 
        try:
          f = float(field_value)
        except:
          f = None
        setattr(obj, c['name'], f)

  def convert_all_to_csv(self):
    '''converts all files (downloading them first if necessary) to CSV '''
    self.download_all_files()
    for table in self.table_list():
      filename = self.get_latest_download(table)
      csv_filename = self.convert_tsv_to_csv(filename)

  def list_all_files(self, schema_table):
    '''Lists all files for a table'''
    files_list = []
    path = '/api/account/self/file/byTable/{}'.format(schema_table)
    url = 'https://api.inshosteddata.com{}'.format(path)

    last_full = None
    last_full_sequence = None
    last_full_dump_id = None
    params = {'limit':0}#,'after':1}
    while not last_full:
      params['limit'] += 5
      signature,_date,headers = self.buildRequest(path, **params)
      results = requests.get(url, params=params,headers=headers)
      results = results.json()
      for res in results.get('history',[]):
        dumpId = res['dumpId']
        if res['partial'] == False:
          last_full = True
          last_full_sequence = res['sequence']
          last_full_dump_id = res['dumpId']
          break
        for fileinfo in res['files']:
          fileinfo['filename'] = os.path.join(self.data_folder,fileinfo['filename'])
          files_list.append(fileinfo)
        if res['sequence'] <=1:
          last_full = True
        
    return files_list


  # Requests files are incremental
  def import_all_requests(self):
    '''imports all requests files. requests files are incremental. To get a
    full picture of web traffic in a given time period, you must import the
    requests file individually'''
    # Get list of requests files
    # Download each request file
    # Import the file
    for fileinfo in self.list_all_files('requests'):
      self.download_single_file(fileinfo['url'], fileinfo['filename'])
      csv_filename = self.convert_tsv_to_csv(fileinfo['filename'])
      self.import_file('requests', csv_filename)

  def import_file(self,schema_table, csv_filename):
    '''imports the table specified by schema_table with the data from
    csv_filename.'''
    if self.file_imported(csv_filename):
      logger.debug('{} not imported because it already in there'.format(schema_table))
      return

    records = []
    for i, data in enumerate(csv.DictReader(open(csv_filename,'rb'))):
        
      obj = self.get_orm_obj(schema_table)

      rec = obj(**data)
      self.normalize_values_for_db(rec, schema_table)
      records.append(rec)
    self.session.add_all(records)
    logger.debug('{} records to import into {}'.format(len(records),schema_table))
    try:
      self.session.commit()
      self.imported_files.add(os.path.basename(csv_filename))
      logger.debug('{} records successfully imported into {}'.format(len(records),schema_table))
      self.save_imported_files()
    except sqlalchemy.exc.IntegrityError as err:
      pass

    
  def import_data(self, schema_table=None, with_download=True):
    '''downloads and imports all tables unless schema_table is defined, in
    which case it only imports that table'''
    self.download_all_files()
    self.create_tables()
    for table in self.table_list():
      if not schema_table or table==schema_table:
        # Do the import
        if self.schema['schema'][table]['incremental']:
          # Clear the table because it is not an incremental data set
          logger.debug('Clear table {} because it is not an incremental data set'.format(table))
          self.clear_table(table)
        logger.debug('get latest download for {} because it is not an incremental data set'.format(table))
        f = self.get_latest_download(table)
        csv_filename = self.convert_tsv_to_csv(f)
        self.import_file(table, csv_filename)

  # This method will check whether a given file has been imported
  # into the database.
  def file_imported(self, filename):
    '''returns true if the file has been imported into the database. otherwise
    returns false'''

    return os.path.basename(filename) in self.imported_files

  @property
  def imported_files(self):
    if self._imported_files == None:
      filename = os.path.join(self.base_folder,'imported_files.json')
      if os.path.exists(filename):
        self._imported_files = json.load(open(filename,'rb'))
      else:
        self._imported_files = []
      self._imported_files = set(self._imported_files)
    return self._imported_files

  def remove_caches(self):
    '''removes all cached data (schema, imported_files, etc) from the base
    folder'''
    files_to_remove = ( 'imported_files.json', 'schema.json')
    for filename in files_to_remove:
      filename = os.path.join(self.base_folder,filename)
      if os.path.exists(filename):
        os.unlink(filename)

  def save_imported_files(self):
    files_imported = set(self.imported_files) 
    filename = os.path.join(self.base_folder,'imported_files.json')
    with open(filename, 'w+') as _f:
      json.dump(list(files_imported),_f, indent=2, separators=(',', ': '))
    logger.debug('imported_files.json saved')
  

  def get_orm_obj(self, schema_table, metadata = None):

    if not getattr(self.base, 'classes', None) or not getattr(self.base.classes, schema_table, None):
      self.tables_md(metadata)
    #return table
    return getattr(self.base.classes,schema_table)

  def get_latest_download(self,table):
    '''returns the latest downloaded file for a table'''
    file_list = self.latest_files()
    if sys.version_info.major == 2:
      _iter = file_list['artifactsByTable'].iteritems()
    else:
      _iter = iter(file_list['artifactsByTable'].items())

    for key,artifact in _iter:
      filename = os.path.join(self.data_folder,artifact['files'][0]['filename'])
      if self.get_schema_name(filename) == table and os.path.exists(filename):
        return filename

  def latest_files(self):
    '''returns the latest downloadable file for a table'''
    path = '/api/account/self/file/latest'
    signature,_date,headers = self.buildRequest(path)
    res = requests.get('https://api.inshosteddata.com{}'.format(path),headers=headers).json()
    return res


  def download_single_file(self, file_url, filename):
    '''Download a single file given the file_url and the filename to give the
    file.'''
    r = requests.get(file_url,stream=True)
    with open(filename, 'wb') as f:
      for chunk in r.iter_content(chunk_size=1024): 
        if chunk: # filter out keep-alive new chunks
          f.write(chunk)


  def download_all_files(self, table=None):
    '''Download all of the files for a given table or, if no table is
    specified, download all files for all tables.'''
    if not self._files_downloaded:
      file_list = self.latest_files()
      if sys.version_info.major == 2:
        _iter = file_list['artifactsByTable'].iteritems()
      else:
        _iter = iter(file_list['artifactsByTable'].items())

      for key,artifact in _iter:
        filename = os.path.join(self.data_folder,artifact['files'][0]['filename'])
        if not table or table in filename:
          if not os.path.exists(filename):
            # Download and save the file
            file_url = artifact['files'][0]['url']
            self.download_single_file(file_url, filename)
      if not table:
        self._files_downloaded = True

  def sql_query(self, query_string):
    return self.engine.execute(query_string)

  @property
  def query(self):
    return self.session.query


