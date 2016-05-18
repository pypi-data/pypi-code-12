""" standard """
import csv
import json
import urllib
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

""" custom """

import ApiProperties
from Config.ResourceType import ResourceType
from ErrorCodes import ErrorCodes
from RequestObject import RequestObject
import OwnerMetricsObject


def parse_owner(owner_dict, resource_obj=None, api_filter=None, request_uri=None):
    """ """
    # group object
    owner = OwnerObject()

    #
    # standard values
    #
    owner.set_id(owner_dict['id'], False)
    owner.set_name(owner_dict['name'], False)
    owner.set_type(owner_dict['type'])

    #
    # handle both resource containers and individual objects
    #
    if resource_obj is not None:
        # store the resource object in the master resource object list
        roi = resource_obj.add_master_resource_obj(owner, owner_dict['id'])

        # retrieve the resource object and update data
        # must be submitted after parameters are set for indexing to work
        owner = resource_obj.get_resource_by_identity(roi)

    #
    # filter (set after retrieving stored object)
    #
    if api_filter is not None:
        owner.add_matched_filter(api_filter)

    #
    # request_uri (set after retrieving stored object)
    #
    if request_uri is not None:
        owner.add_request_uri(request_uri)

    return owner


class OwnerObject(object):
    __slots__ = (
        '_id',
        '_matched_filters',
        '_name',
        '_phase',  # 0 - new; 1 - add; 2 - update
        '_request_uris',
        '_resource_type',
        '_type',
    )

    def __init__(self):
        self._id = None
        self._matched_filters = []
        self._name = None
        self._phase = 0
        self._request_uris = []
        self._resource_type = ResourceType.OWNERS
        self._type = None

    #
    # unicode
    #
    @staticmethod
    def _uni(data):
        """ """
        if data is None or isinstance(data, (int, list, dict)):
            return data
        elif isinstance(data, unicode):
            return unicode(data.encode('utf-8').strip(), errors='ignore')  # re-encode poorly encoded unicode
        elif not isinstance(data, unicode):
            return unicode(data, 'utf-8', errors='ignore')
        else:
            return data

    #
    # urlsafe
    #
    @staticmethod
    def _urlsafe(data):
        """ url encode value for safe request """
        return urllib.quote(data, safe='~')

    """ group object methods """

    #
    # id
    #
    @property
    def id(self):
        """ """
        return self._id

    def set_id(self, data, update=True):
        """Read-Only group metadata"""
        if isinstance(data, (int, long)):
            self._id = data

            if update:
                self._phase = 2
        else:
            raise AttributeError(ErrorCodes.e10020.value.format(data))

    #
    # matched filters
    #
    @property
    def matched_filters(self):
        """ """
        return self._matched_filters

    def add_matched_filter(self, data):
        """ """
        if data is not None:
            self._matched_filters.append(data)

    #
    # name
    #
    @property
    def name(self):
        """ """
        return self._name

    def set_name(self, data, update=True):
        """Read-Write group metadata"""
        self._name = self._uni(data)
        if update and self._phase == 0:
            self._phase = 2

    #
    # type
    #
    @property
    def type(self):
        """ """
        return self._type

    def set_type(self, data):
        """ """
        self._type = self._uni(data)

    #
    # request uris
    #
    @property
    def request_uris(self):
        return self._request_uris

    def add_request_uri(self, data):
        """ """
        if data not in self._request_uris:
            self._request_uris.append(data)

    #
    # phase
    #
    @property
    def phase(self):
        """ """
        return self._phase

    def set_phase(self, data):
        """ """
        self._phase = data

    #
    # resource_type
    #
    @property
    def resource_type(self):
        """ """
        return self._resource_type

    #
    # add print method
    #
    def __str__(self):
        """allow object to be displayed with print"""

        printable_string = '\n{0!s:_^80}\n'.format('Owner Resource Object Properties')

        #
        # retrievable methods
        #
        printable_string += '{0!s:40}\n'.format('Retrievable Methods')
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('id', self.id))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('name', self.name))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('type', self.type))

        #
        # object information
        #
        printable_string += '\n{0!s:40}\n'.format('Object Information')
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('phase', self.phase))

        #
        # request uri's
        #
        if len(self.request_uris) > 0:
            printable_string += '\n{0!s:40}\n'.format('Request URI\'s')
            for item in sorted(self.request_uris):
                printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('', item))

        return printable_string


class OwnerObjectAdvanced(OwnerObject):
    """ Temporary Object with extended functionality. """
    __slots__ = (
        '_resource_container',
        '_resource_obj',
        '_resource_properties',
        '_basic_structure',
        '_structure',
        '_tc',
        'tcl',
    )

    def __init__(self, tc_obj, resource_container, resource_obj):
        """ add methods to resource object """
        super(OwnerObject, self).__init__()

        self._resource_properties = ApiProperties.api_properties[resource_obj.resource_type.name]['properties']
        self._resource_container = resource_container
        self._resource_obj = resource_obj
        self._basic_structure = {
            'id': 'id',
            'name': 'name',
            'type': 'type',
        }
        self._structure = self._basic_structure.copy()
        self._tc = tc_obj
        self.tcl = tc_obj.tcl

        # load data from resource_obj
        self.load_data(self._resource_obj)

    @property
    def csv(self):
        """ return the object in json format """

        csv_dict = {}
        for k, v in self._basic_structure.items():
            csv_dict[k] = getattr(self, v)

        outfile = StringIO()
        writer = csv.DictWriter(outfile, fieldnames=sorted(csv_dict.keys()))

        writer.writerow(csv_dict)

        return outfile.getvalue().rstrip()

    @property
    def csv_header(self):
        """ return the object in json format """

        csv_dict = {}
        for k, v in self._basic_structure.items():
            csv_dict[k] = v

        outfile = StringIO()
        # not supported in python 2.6
        # writer = csv.DictWriter(outfile, fieldnames=sorted(csv_dict.keys()))
        # writer.writeheader()

        csv_header = ','.join(sorted(csv_dict.keys()))
        outfile.write(csv_header)

        return outfile.getvalue().rstrip()

    @property
    def json(self):
        """ return the object in json format """
        json_dict = {}
        for k, v in self._structure.items():
            json_dict[k] = getattr(self, v)

        return json.dumps(json_dict, indent=4, sort_keys=True)

    @property
    def keyval(self):
        """ return the object in json format """
        keyval_str = ''
        for k, v in sorted(self._structure.items()):
            # handle file indicators
            keyval_str += '{0}="{1}" '.format(k, getattr(self, v))

        return keyval_str

    def load_data(self, resource_obj):
        """ load data from resource object to self """
        for key in resource_obj.__slots__:
            setattr(self, key, getattr(resource_obj, key))

    @property
    def metrics(self):
        """ retrieve owner metrics for this owner """
        prop = self._resource_properties['individual_metrics']
        ro = RequestObject()
        ro.set_description('load owner metrics {0}'.format(self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_resource_pagination(prop['pagination'])
        ro.set_request_uri(prop['uri'].format(self._id))
        ro.set_resource_type(ResourceType.OWNER_METRICS)
        api_response = self._tc.api_request(ro)
        
        if api_response.headers['content-type'] == 'application/json':
            api_response_dict = api_response.json()
            if api_response_dict['status'] == 'Success':
                data = api_response_dict['data']['ownerMetric']
                for item in data:
                    yield OwnerMetricsObject.parse_metrics(item)