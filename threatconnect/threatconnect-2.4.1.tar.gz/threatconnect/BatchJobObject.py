""" standard """
import json

""" custom """

import ApiProperties
from Config.ResourceType import ResourceType
from RequestObject import RequestObject


class BatchJobObject(object):
    __slots__ = (
        '_id',
        '_halt_on_error',
        '_attribute_write_type',
        '_action',
        '_owner',
        '_phase',
        '_properties',
        '_request_uris',
        '_resource_type',
        '_errors',
        '_status',
        '_error_count',
        '_success_count',
        '_unprocess_count',
        '_matched_filters',
        '_request_uris'
    )

    def __init__(self):
        self._id = None
        self._halt_on_error = None
        self._attribute_write_type = None
        self._action = None
        self._owner = None
        self._errors = None
        self._status = None
        self._error_count = None
        self._success_count = None
        self._unprocess_count = None
        self._matched_filters = []
        self._request_uris = []
        self._properties = {
            '_halt_on_error': {
                'api_field': 'haltOnError',
                'method': 'set_halt_on_error',
                'required': True,
            },
            '_attribute_write_type': {
                'api_field': 'attributeWriteType',
                'method': 'set_attribute_write_type',
                'required': True,
            },
            '_action': {
                'api_field': 'action',
                'method': 'set_action',
                'required': True,
            },
            '_owner': {
                'api_field': 'owner',
                'method': 'set_owner',
                'required': True,
            },
        }
        self._phase = 0
        self._request_uris = []
        self._resource_type = ResourceType.BATCH_JOBS

    #
    # resource_type
    #
    @property
    def resource_type(self):
        """ """
        return self._resource_type

    #
    # id
    #
    @property
    def id(self):
        """ """
        return self._id

    def set_id(self, data, update=True):
        """Read-Only group metadata"""
        self._id = data

        if update:
            self._phase = 2

    #
    # halt_on_error
    #
    @property
    def halt_on_error(self):
        return self._halt_on_error

    def set_halt_on_error(self, halt_on_error):
        self._halt_on_error = halt_on_error
            
    #
    # attribute_write_type
    #
    @property
    def attribute_write_type(self):
        return self._attribute_write_type

    def set_attribute_write_type(self, attribute_write_type):
        self._attribute_write_type = attribute_write_type
            
    #
    # action
    #
    @property
    def action(self):
        return self._action

    def set_action(self, action):
        self._action = action

    #
    # owner
    #
    @property
    def owner(self):
        return self._owner

    def set_owner(self, owner):
        self._owner = owner

    #
    # validate
    #
    @property
    def validate(self):
        """ validate all required fields """
        for prop, values in self._properties.items():
            if values['required']:
                if getattr(self, prop) is None:
                    return False

        return True

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
    # Errors
    #
    @property
    def errors(self):
        return self._errors

    def set_errors(self, data):
        self._errors = data
        
    #
    # status
    #
    @property
    def status(self):
        return self._status

    def set_status(self, data):
        self._status = data
        
    #
    # error_count
    #
    @property
    def error_count(self):
        return self._error_count

    def set_error_count(self, data):
        self._error_count = data

    #
    # success_count
    #
    @property
    def success_count(self):
        return self._success_count

    def set_success_count(self, data):
        self._success_count = data

    #
    # unprocess_count
    #
    @property
    def unprocess_count(self):
        return self._unprocess_count

    def set_unprocess_count(self, data):
        self._unprocess_count = data

    #
    # matched filters
    #
    @property
    def matched_filters(self):
        """ """
        return self._matched_filters

    def add_matched_filter(self, data):
        """ """
        if data not in self._matched_filters and data is not None:
            self._matched_filters.append(data)

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


class BatchJobObjectAdvanced(BatchJobObject):
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
        super(BatchJobObject, self).__init__()

        self._resource_properties = ApiProperties.api_properties[resource_obj.resource_type.name]['properties']
        self._resource_container = resource_container
        self._resource_obj = resource_obj
        self._basic_structure = {
            'id': 'id',
            'haltOnError': 'haltOnError',
            'attributeWriteType': 'attribute_write_type',
            'action': 'action'
        }
        self._structure = self._basic_structure.copy()
        self._tc = tc_obj
        self._tc.tcl = tc_obj.tcl

        # load data from resource_obj
        self.load_data(self._resource_obj)

    def load_data(self, resource_obj):
        """ load data from resource object to self """
        for key in resource_obj.__slots__:
            setattr(self, key, getattr(resource_obj, key))

    @property
    def gen_body(self):
        """ generate json body for POST and PUT API requests """
        body_dict = {}
        for prop, values in self._properties.items():
            if getattr(self, prop) is not None:
                body_dict[values['api_field']] = getattr(self, prop)
        return json.dumps(body_dict)
    
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

    def commit(self):
        """ commit victim and related assets, associations """
        r_id = self.id
        ro = RequestObject()
        ro.set_body(self.gen_body)
        ro.set_resource_type(self.resource_type)
        prop = self._resource_properties['add']
        ro.set_description('adding batchjob')
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(self._id))
        ro.empty_payload()
        if self._phase == 1:
            # validate all required fields are present
            if self.validate:
                api_response = self._tc.api_request(ro)
                if api_response.headers['content-type'] == 'application/json':
                    api_response_dict = api_response.json()
                    if api_response_dict['status'] == 'Success':
                        r_id = api_response_dict['data']['batchId']
            else:
                self._tc.tcl.debug('Resource Object'.format(self))
                raise RuntimeError('Cannot commit incomplete resource object')

        for ro in self._resource_container.commit_queue(self.id):
            # if self.owner_name is not None:
            #     ro.set_owner(self.owner_name)

            # replace the id
            if self.id != r_id:
                request_uri = str(ro.request_uri.replace(str(self.id), str(r_id)))
                ro.set_request_uri(request_uri)
            self._tc.tcl.debug('Replacing {0} with {1}'.format(self.id, str(r_id)))
            self._tc.tcl.debug('RO {0}'.format(ro))

            api_response2 = self._tc.api_request(ro)
            if api_response2.headers['content-type'] == 'application/json':
                api_response_dict2 = api_response2.json()
                if api_response_dict2['status'] != 'Success':
                    self._tc.tcl.error('API Request Failure: [{0}]'.format(ro.description))

        self.set_id(r_id)

        self.set_phase(0)

        # return object
        return self

    def upload(self, body):
        """ upload batch job  """
        prop = self._resource_properties['batch_job_upload']

        ro = RequestObject()
        ro.set_body(body)
        ro.set_content_type('application/octet-stream')
        ro.set_description('upload batch job for "{0}"'.format(self._id))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(self._id))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        ro.empty_payload()
        self._resource_container.add_commit_queue(self.id, ro)

    def download_errors(self):
        prop = self._resource_properties['batch_error_download']

        ro = RequestObject()
        ro.set_description('download errors for batchjob {0}'.format(self._id))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(self._id))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        api_response = self._tc.api_request(ro)

        if api_response.headers['content-type'] in ['application/octet-stream', 'text/plain']:
            self.set_errors(api_response.content)