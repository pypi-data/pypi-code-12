""" standard """
import csv
import json
import urllib
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

""" custom """
from AttributeObject import parse_attribute, AttributeObject
import GroupObject
from SecurityLabelObject import parse_security_label
from VictimAssetObject import parse_victim_asset
from TagObject import parse_tag

import ApiProperties
from Config.ResourceType import ResourceType
from ErrorCodes import ErrorCodes
from RequestObject import RequestObject


def parse_victim(victim_dict, resource_obj=None, api_filter=None, request_uri=None):
    """ """
    # group object
    victim = VictimObject()

    #
    # standard values
    #
    victim.set_id(victim_dict['id'], False)
    victim.set_name(victim_dict['name'], False)
    victim.set_weblink(victim_dict['webLink'])

    #
    # optional values
    #
    if 'description' in victim_dict:
        victim.set_description(victim_dict['description'], False)
    if 'nationality' in victim_dict:
        victim.set_nationality(victim_dict['nationality'], False)
    if 'org' in victim_dict:
        victim.set_org(victim_dict['org'], False)
    if 'owner' in victim_dict:
        victim.set_owner_name(victim_dict['owner'])
    if 'suborg' in victim_dict:
        victim.set_suborg(victim_dict['suborg'], False)
    if 'workLocation' in victim_dict:
        victim.set_work_location(victim_dict['workLocation'], False)

    # #
    # # automatically load victim assets (special case for Victims)
    # #
    #
    # """ retrieve assets for this indicator """
    # prop = ApiProperties.api_properties['VICTIMS']['properties']['assets']
    # ro = RequestObject()
    # ro.set_description('load assets for {0}'.format(victim_dict['name']))
    # ro.set_http_method(prop['http_method'])
    # ro.set_owner(victim_dict['owner'])
    # ro.set_owner_allowed(prop['owner_allowed'])
    # ro.set_request_uri(prop['uri'].format(victim_dict['id']))
    # ro.set_resource_pagination(prop['pagination'])
    # ro.set_resource_type(ResourceType.VICTIMS)
    # api_response = tc.api_request(ro)
    #
    # if api_response.headers['content-type'] == 'application/json':
    #     api_response_dict = api_response.json()
    #     if api_response_dict['status'] == 'Success':
    #         data = api_response_dict['data']['victimAsset']
    #         for item in data:
    #             victim.add_asset(parse_victim_asset(item))

    #
    # handle both resource containers and individual objects
    #
    if resource_obj is not None:
        # store the resource object in the master resource object list
        roi = resource_obj.add_master_resource_obj(victim, victim_dict['id'])

        # retrieve the resource object and update data
        # must be submitted after parameters are set for indexing to work
        victim = resource_obj.get_resource_by_identity(roi)

    #
    # filter (set after retrieving stored object)
    #
    if api_filter is not None:
        victim.add_matched_filter(api_filter)

    #
    # request_uri (set after retrieving stored object)
    #
    if request_uri is not None:
        victim.add_request_uri(request_uri)

    return victim


class VictimObject(object):
    __slots__ = (
        '_assets',
        '_attributes',
        '_description',
        '_id',
        '_matched_filters',
        '_nationality',
        '_name',
        '_org',
        '_owner_name',
        '_phase',
        '_properties',
        '_request_uris',
        '_resource_type',
        '_security_label',
        '_suborg',
        '_tags',
        '_weblink',
        '_work_location',
        '_reload_attributes'
    )

    def __init__(self):
        self._assets = []
        self._attributes = []
        self._description = None
        self._id = None
        self._matched_filters = []
        self._name = None
        self._nationality = None
        self._org = None
        self._owner_name = None
        self._phase = 0
        self._properties = {
            '_name': {
                'api_field': 'name',
                'method': 'set_name',
                'required': True,
            },
            '_nationality': {
                'api_field': 'nationality',
                'method': 'set_nationality',
                'required': False,
            },
            '_org': {
                'api_field': 'org',
                'method': 'set_org',
                'required': False,
            },
            '_suborg': {
                'api_field': 'suborg',
                'method': 'set_suborg',
                'required': False,
            },
            '_work_location': {
                'api_field': 'workLocation',
                'method': 'set_work_location',
                'required': False,
            },
        }
        self._reload_attributes = False
        self._request_uris = []
        self._resource_type = ResourceType.VICTIMS
        self._security_label = None
        self._suborg = None
        self._tags = []
        self._weblink = None
        self._work_location = None

    #
    # unicode
    #
    @staticmethod
    def _uni(data):
        """ """
        if data is None or isinstance(data, (int, list, long, dict)):
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

    """ victim object methods """

    #
    # assets
    #
    @property
    def assets(self):
        """ """
        return self._assets

    def add_asset(self, data_obj):
        """Read-Only group metadata"""
        self._assets.append(data_obj)
        
    #
    # attributes
    #
    @property
    def attributes(self):
        """ """
        return self._attributes

    def add_attribute(self, data_obj, displayed=True):
        """collection of attributes objects"""
        self._attributes.append(data_obj)

    #
    # description
    #
    @property
    def description(self):
        """ """
        return self._description

    def set_description(self, data, update=True):
        """Read-Only group metadata"""
        self._description = self._uni(data)

        if update and self._phase == 0:
            self._phase = 2

    #
    # id
    #
    @property
    def id(self):
        """ """
        return self._id

    def set_id(self, data, update=True):
        """Read-Only group metadata"""
        self._id = self._uni(data)

        if update:
            self._phase = 2

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
    # nationality
    #
    @property
    def nationality(self):
        """ """
        return self._nationality

    def set_nationality(self, data, update=True):
        """Read-Only group metadata"""
        self._nationality = self._uni(data)

        if update and self._phase == 0:
            self._phase = 2

    #
    # org
    #
    @property
    def org(self):
        """ """
        return self._org

    def set_org(self, data, update=True):
        """Read-Only group metadata"""
        self._org = self._uni(data)

        if update and self._phase == 0:
            self._phase = 2

    #
    # owner_name
    #
    @property
    def owner_name(self):
        """ """
        return self._owner_name

    def set_owner_name(self, data):
        """Read-Only group metadata"""
        self._owner_name = self._uni(data)

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
    # resource_type
    #
    @property
    def resource_type(self):
        """ """
        return self._resource_type

    #
    # security label
    #
    @property
    def security_label(self):
        """ """
        return self._security_label

    def set_security_label(self, data_obj):
        self.add_security_label(data_obj)

    def add_security_label(self, data_obj):
        """security label"""
        self._security_label = data_obj

    #
    # suborg
    #
    @property
    def suborg(self):
        """ """
        return self._suborg

    def set_suborg(self, data, update=True):
        """Read-Only group metadata"""
        self._suborg = self._uni(data)

        if update and self._phase == 0:
            self._phase = 2

    #
    # tags
    #
    @property
    def tags(self):
        """ """
        return self._tags

    def add_tag(self, data_obj):
        """collection of tag objects"""
        self._tags.append(data_obj)

    #
    # weblink
    #
    @property
    def weblink(self):
        """ """
        return self._weblink

    def set_weblink(self, data):
        """Read-Only group metadata"""
        self._weblink = self._uni(data)

    #
    # work_location
    #
    @property
    def work_location(self):
        """ """
        return self._work_location

    def set_work_location(self, data, update=True):
        """Read-Only group metadata"""
        self._work_location = self._uni(data)

        if update and self._phase == 0:
            self._phase = 2

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
    # add print method
    #
    def __str__(self):
        """allow object to be displayed with print"""

        printable_string = '\n{0!s:_^80}\n'.format('Resource Object Properties')

        #
        # retrievable methods
        #
        printable_string += '{0!s:40}\n'.format('Retrievable Methods')
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('id', self.id))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('name', self.name))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('owner_name', self.owner_name))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('resource_type', self.resource_type))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('description', self.description))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('org', self.org))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('nationality', self.nationality))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('suborg', self.suborg))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('work_location', self.work_location))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('weblink', self.weblink))

        #
        # writable properties
        #
        printable_string += '\n{0!s:40}\n'.format('Writable Properties')
        for prop, values in sorted(self._properties.items()):
            printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format(
                values['api_field'], '{0!s} (Required: {1!s})'.format(values['method'], str(values['required']))))

        #
        # object information
        #
        printable_string += '\n{0!s:40}\n'.format('Object Information')
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('phase', self.phase))

        #
        # matched filter
        #
        if len(self.matched_filters) > 0:
            printable_string += '\n{0!s:40}\n'.format('Matched Filters')
            for item in sorted(self.matched_filters):
                printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('matched filter', item))

        #
        # request uri's
        #
        if len(self.request_uris) > 0:
            printable_string += '\n{0!s:40}\n'.format('Request URI\'s')
            for item in sorted(self.request_uris):
                printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('', item))

        return printable_string


class VictimObjectAdvanced(VictimObject):
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
        super(VictimObject, self).__init__()

        self._resource_properties = ApiProperties.api_properties[resource_obj.resource_type.name]['properties']
        self._resource_container = resource_container
        self._resource_obj = resource_obj
        self._basic_structure = {
            'id': 'id',
            'name': 'name',
            'nationality': 'nationality',
            'org': 'org',
            'suborg': 'suborg',
            'workLocation': 'work_location',
            'weblink': 'weblink',
        }
        self._structure = self._basic_structure.copy()
        self._tc = tc_obj
        self._tc.tcl = tc_obj.tcl

        # load data from resource_obj
        self.load_data(self._resource_obj)

    def add_asset(self, asset_obj):
        """ add a asset to a victim """
        prop = self._resource_properties['asset_add']
        ro = RequestObject()
        ro.set_body(asset_obj.gen_body)
        ro.set_description('add asset type {0} with to {1}'.format(asset_obj.resource_type, self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(self._id, asset_obj.uri_attribute))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        self._resource_container.add_commit_queue(self.id, ro)
        
    def add_attribute(self, attr_type, attr_value, attr_displayed='true'):
        """ add an attribute to a victim """
        prop = self._resource_properties['attribute_add']
        ro = RequestObject()
        ro.set_body(json.dumps({
            'type': attr_type,
            'value': attr_value,
            'displayed': attr_displayed}))
        ro.set_description('add attribute type "{0}" with value "{1}" to "{2}"'.format(
            attr_type, attr_value, self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(self._id))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        callback = lambda status: self.__add_attribute_failure(attr_type, attr_value)
        ro.set_failure_callback(callback)
        self._resource_container.add_commit_queue(self.id, ro)
        attribute = AttributeObject(self)
        attribute.set_type(attr_type)
        attribute.set_value(attr_value)
        attribute.set_displayed(attr_displayed)
        self._resource_obj.add_attribute(attribute)
        
    def __add_attribute_failure(self, attr_type, attr_value):
        for attribute in self._attributes:
            if attribute.type == attr_type and attribute.value == attr_value:
                self._attributes.remove(attribute)
                break
            
    def add_security_label(self, label):
        """ set the security label for this victim """
        prop = self._resource_properties['security_label_add']
        ro = RequestObject()
        ro.set_description('add security label "{0}" to "{1}"'.format(label, self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_resource_pagination(prop['pagination'])
        ro.set_request_uri(prop['uri'].format(
            self._id, self._urlsafe(label)))
        ro.set_resource_type(self._resource_type)

        self._resource_container.add_commit_queue(self.id, ro)

    def add_tag(self, tag):
        """ add a tag to an victim """
        prop = self._resource_properties['tag_add']
        ro = RequestObject()
        ro.set_description('add tag "{0}" to "{1}"'.format(tag, self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(self._id, self._urlsafe(tag)))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        self._resource_container.add_commit_queue(self.id, ro)

    def associate_group(self, resource_type, resource_id):
        """ associate a group to indicator by id """
        prop = self._resource_properties['association_group_add']
        ro = RequestObject()
        ro.set_description('associate group type "{0}" id {1} to "{2}"'.format(
            resource_type.name, resource_id, self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_resource_pagination(prop['pagination'])
        group_uri_attribute = ApiProperties.api_properties[resource_type.name]['uri_attribute']
        ro.set_request_uri(prop['uri'].format(self._id, group_uri_attribute, resource_id))
        ro.set_resource_type(self._resource_type)

        self._resource_container.add_commit_queue(self.id, ro)

    @property
    def gen_body(self):
        """ generate json body for POST and PUT API requests """
        body_dict = {}
        for prop, values in self._properties.items():
            if getattr(self, prop) is not None:
                body_dict[values['api_field']] = getattr(self, prop)
        return json.dumps(body_dict)

    def commit(self):
        """ commit victim and related assets, associations """
        r_id = self.id
        ro = RequestObject()
        ro.set_body(self.gen_body)
        if self.owner_name is not None:
            ro.set_owner(self.owner_name)
        ro.set_resource_type(self.resource_type)
        if self.phase == 1:
            prop = self._resource_properties['add']
            ro.set_description('adding group "{0}".'.format(self._name))
            ro.set_http_method(prop['http_method'])
            ro.set_owner_allowed(prop['owner_allowed'])
            ro.set_request_uri(prop['uri'].format(self._id))
            ro.set_resource_pagination(prop['pagination'])
            # validate all required fields are present
            if self.validate:
                api_response = self._tc.api_request(ro)
                if api_response.headers['content-type'] == 'application/json':
                    api_response_dict = api_response.json()
                    if api_response_dict['status'] == 'Success':
                        resource_key = ApiProperties.api_properties[self.resource_type.name]['resource_key']
                        r_id = api_response_dict['data'][resource_key]['id']
            else:
                self._tc.tcl.debug('Resource Object'.format(self))
                raise AttributeError(ErrorCodes.e10040.value)
        elif self.phase == 2:
            prop = self._resource_properties['update']
            ro.set_description('update indicator "{0}".'.format(self._name))
            ro.set_http_method(prop['http_method'])
            ro.set_owner_allowed(prop['owner_allowed'])
            ro.set_request_uri(prop['uri'].format(self._id))
            ro.set_resource_pagination(prop['pagination'])
            api_response = self._tc.api_request(ro)
            if api_response.headers['content-type'] == 'application/json':
                api_response_dict = api_response.json()
                if api_response_dict['status'] != 'Success':
                    self._tc.tcl.error('API Request Failure: [{0}]'.format(ro.description))

        # submit all attributes, tags or associations
        for ro in self._resource_container.commit_queue(self.id):
            # if self.owner_name is not None:
            #     ro.set_owner(self.owner_name)

            # replace the id
            if self.phase == 1 and self.id != r_id:
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

        self._resource_container.clear_commit_queue_id(self.id)
        
        self.set_phase(0)
        
        if self._reload_attributes:
            self.load_attributes(automatically_reload=True)

        # return object
        return self

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
        # not support in python 2.6
        # writer = csv.DictWriter(outfile, fieldnames=sorted(csv_dict.keys()))
        # writer.writeheader()

        csv_header = ','.join(sorted(csv_dict.keys()))
        outfile.write(csv_header)

        return outfile.getvalue().rstrip()

    def delete(self):
        """ delete indicator """
        prop = self._resource_properties['delete']
        ro = RequestObject()
        ro.set_description('delete victim "{0}".'.format(self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        # if self.owner_name is not None:
        #     ro.set_owner(self.owner_name)
        ro.set_request_uri(prop['uri'].format(self._id))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self.resource_type)
        self._tc.api_request(ro)
        self.set_phase(3)

    def delete_asset(self, asset_id, asset_obj):
        """ add a asset to a victim """
        prop = self._resource_properties['asset_delete']
        ro = RequestObject()
        ro.set_description('delete asset type {0} with to {1}'.format(asset_obj.resource_type, self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner(self.owner_name)
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(self._id, asset_obj.uri_attribute, asset_id))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        self._resource_container.add_commit_queue(self.id, ro)
        
    def delete_attribute(self, attr_id):
        """ delete attribute from victim by id """
        prop = self._resource_properties['attribute_delete']
        ro = RequestObject()
        ro.set_description('delete attribute id {0} from "{1}"'.format(attr_id, self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(
            self._id, attr_id))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        self._resource_container.add_commit_queue(self.id, ro)

    def delete_security_label(self, label):
        """ delete the security label for this indicator """
        prop = self._resource_properties['security_label_delete']
        ro = RequestObject()
        ro.set_description('delete security label "{0}" from {1}'.format(label, self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(
            self._id, self._urlsafe(label)))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        self._resource_container.add_commit_queue(self.id, ro)
        
    def delete_tag(self, tag):
        """ delete tag from victim """
        prop = self._resource_properties['tag_delete']
        ro = RequestObject()
        ro.set_description('delete tag "{0}" from "{1}"'.format(tag, self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(
            self._id, self._urlsafe(tag)))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        self._resource_container.add_commit_queue(self.id, ro)

    def disassociate_group(self, resource_type, resource_id):
        """ disassociate group from victim """
        prop = self._resource_properties['association_group_delete']
        ro = RequestObject()
        ro.set_description('disassociate group type {0} id {1} from "{2}"'.format(
            resource_type.name, resource_id, self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        group_uri_attribute = ApiProperties.api_properties[resource_type.name]['uri_attribute']
        ro.set_request_uri(prop['uri'].format(
            self._id, group_uri_attribute, resource_id))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        self._resource_container.add_commit_queue(self.id, ro)

    @property
    def group_associations(self):
        """ retrieve associations for this group. associations are not stored within the object """
        prop = self._resource_properties['association_groups']
        ro = RequestObject()
        ro.set_description('retrieve group associations for {0}'.format(self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(self._id))
        # ro.set_owner(self.owner_name)
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)

        for item in self._tc.result_pagination(ro, 'group'):
            yield threatconnect.GroupObject.parse_group(item, api_filter=ro.description, request_uri=ro.request_uri)

    @property
    def indicator_associations(self):
        """ retrieve associations for this victim. associations are not stored within the object """
        prop = self._resource_properties['association_indicators']
        ro = RequestObject()
        ro.set_description('retrieve indicator associations for {0}'.format(self._name))
        ro.set_http_method(prop['http_method'])
        # ro.set_owner(self.owner_name)
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(self._id))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)

        for item in self._tc.result_pagination(ro, 'indicator'):
            yield threatconnect.IndicatorObject.parse_indicator(
                item, api_filter=ro.description, request_uri=ro.request_uri)

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

    def load_assets(self):
        """ retrieve assets for this indicator """
        prop = self._resource_properties['assets']
        ro = RequestObject()
        ro.set_description('load assets for {0}'.format(self._name))
        ro.set_http_method(prop['http_method'])
        # ro.set_owner(self.owner_name)
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(self._id))
        ro.set_resource_pagination(prop['pagination'])
        # ro.set_request_uri(self._resource_properties.asset_path.format(self._id))
        ro.set_resource_type(self._resource_type)
        api_response = self._tc.api_request(ro)

        if api_response.headers['content-type'] == 'application/json':
            api_response_dict = api_response.json()
            if api_response_dict['status'] == 'Success':
                data = api_response_dict['data']['victimAsset']
                for item in data:
                    self._resource_obj.add_asset(parse_victim_asset(item))  # add to main resource object
                    
    def load_attributes(self, automatically_reload=False):
        self._reload_attributes = automatically_reload
        """ retrieve attributes for this group """
        prop = self._resource_properties['attributes']
        ro = RequestObject()
        ro.set_description('load attributes for {0}'.format(self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner(self.owner_name)
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(self._id))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        api_response = self._tc.api_request(ro)

        if api_response.headers['content-type'] == 'application/json':
            api_response_dict = api_response.json()
            if api_response_dict['status'] == 'Success':
                data = api_response_dict['data']['attribute']
                self._resource_obj._attributes = []
                for item in data:
                    self._resource_obj.add_attribute(parse_attribute(item, self))  # add to main resource object
                    
    def load_security_label(self):
        """ retrieve security label for this victim """
        prop = self._resource_properties['security_label_load']
        ro = RequestObject()
        ro.set_description('load security labels for {0}'.format(self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner(self.owner_name)
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(self._id))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        api_response = self._tc.api_request(ro)

        if api_response.headers['content-type'] == 'application/json':
            api_response_dict = api_response.json()
            if api_response_dict['status'] == 'Success':
                data = api_response_dict['data']['securityLabel']
                for item in data:
                    self._security_label = parse_security_label(item)  # add to main resource object
                    
    def load_tags(self):
        """ retrieve tags for this victim """
        prop = self._resource_properties['tags_load']
        ro = RequestObject()
        ro.set_description('load tags for {0}'.format(self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner(self.owner_name)
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(self._id))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        api_response = self._tc.api_request(ro)

        if api_response.headers['content-type'] == 'application/json':
            api_response_dict = api_response.json()
            if api_response_dict['status'] == 'Success':
                data = api_response_dict['data']['tag']
                for item in data:
                    self._resource_obj.add_tag(parse_tag(item))  # add to main resource object

    def set_security_label(self, label):
        self.add_security_label(label)

    def update_asset(self, asset_id, asset_obj):
        """ add a asset to a victim """
        prop = self._resource_properties['asset_update']
        ro = RequestObject()
        ro.set_body(asset_obj.gen_body)
        ro.set_description('update asset type {0} with to {1}'.format(asset_obj.resource_type, self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(self._id, asset_obj.uri_attribute, asset_id))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        self._resource_container.add_commit_queue(self.id, ro)

    def update_attribute(self, attr_id, attr_value):
        """ update victim attribute by id """
        prop = self._resource_properties['attribute_update']
        ro = RequestObject()
        ro.set_body(json.dumps({'value': attr_value}))
        ro.set_description('update attribute id {0} with value "{1}" on "{2}"'.format(
            attr_id, attr_value, self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(self._id, attr_id))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)

        self._resource_container.add_commit_queue(self.id, ro)
        
    #
    # attributes
    #
    @property
    def attributes(self):
        """ """
        return self._resource_obj._attributes