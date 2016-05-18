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
from GroupObject import parse_group
# import IndicatorObject  #Causes circular import
from SecurityLabelObject import parse_security_label
from TagObject import parse_tag
from VictimObject import parse_victim
# import VictimObject

import ApiProperties
from Config.ResourceType import ResourceType
from ErrorCodes import ErrorCodes

from RequestObject import RequestObject
from SharedMethods import get_resource_group_type


def parse_task(task_dict, resource_type=ResourceType.TASKS, resource_obj=None, api_filter=None, request_uri=None):
    """ """
    # task object
    task = TaskObject()
    
    #
    # standard values
    #
    task.set_date_added(task_dict['dateAdded'])
    task.set_id(task_dict['id'], False)
    task.set_escalated(task_dict['escalated'], False)
    task.set_name(task_dict['name'], False)
    task.set_overdue(task_dict['overdue'], False)
    task.set_reminded(task_dict['reminded'], False)
    task.set_status(task_dict['status'], False)
    task.set_weblink(task_dict['webLink'])

    #
    # optional values
    #
    if 'dueDate' in task_dict:
        task.set_due_date(task_dict['dueDate'], False)
    if 'escalationDate' in task_dict:
        task.set_escalation_date(task_dict['escalationDate'], False)
    if 'reminderDate' in task_dict:
        task.set_reminder_date(task_dict['reminderDate'], False)
    if 'owner' in task_dict:  # nested owner for single indicator result
        task.set_owner_name(task_dict['owner']['name'])
    if 'ownerName' in task_dict:
        task.set_owner_name(task_dict['ownerName'])

    #
    # handle both resource containers and individual objects
    #
    if resource_obj is not None:
        # store the resource object in the master resource object list
        roi = resource_obj.add_master_resource_obj(task, task_dict['id'])

        # retrieve the resource object and update data
        # must be submitted after parameters are set for indexing to work
        task = resource_obj.get_resource_by_identity(roi)

    #
    # filter (set after retrieving stored object)
    #
    if api_filter is not None:
        task.add_matched_filter(api_filter)

    #
    # request_uri (set after retrieving stored object)
    #
    if request_uri is not None:
        task.add_request_uri(request_uri)

    return task


class TaskObject(object):
    __slots__ = (
        '_attributes',
        '_assignee',
        '_date_added',
        '_due_date',
        '_escalated',
        '_escalation_date',
        '_id',
        '_matched_filters',
        '_name',
        '_overdue',
        '_owner_name',
        '_phase',  # 0 - new; 1 - add; 2 - update
        '_properties',
        '_reload_attributes',
        '_reminded',
        '_reminder_date',
        '_request_uris',
        '_resource_type',
        '_security_label',
        '_status',
        '_tags',
        '_weblink',
    )

    # def __init__(self, resource_type_enum=None):
    def __init__(self):
        self._attributes = []
        self._assignee = []
        self._date_added = None
        self._due_date = None
        self._escalated = None
        self._escalation_date = None
        self._id = None
        self._matched_filters = []
        self._name = None
        self._overdue = None
        self._owner_name = None
        self._phase = 0
        self._properties = {
            '_name': {
                'api_field': 'name',
                'method': 'set_name',
                'required': True,
            },
            'due_date': {
                'api_field': 'dueDate',
                'method': 'set_due_date',
                'required': False,
            },
            'escalated': {
                'api_field': 'escalated',
                'method': 'set_escalated',
                'required': False,
            },
            'escalation_date': {
                'api_field': 'escalationDate',
                'method': 'set_escalation_date',
                'required': False,
            },
            'overdue': {
                'api_field': 'overdue',
                'method': 'set_overdue',
                'required': False,
            },
            'reminded': {
                'api_field': 'reminded',
                'method': 'set_reminded',
                'required': False,
            },
            'reminder_date': {
                'api_field': 'reminderDate',
                'method': 'set_reminder_date',
                'required': False,
            },
            'status': {
                'api_field': 'status',
                'method': 'set_status',
                'required': False,
            },
        }
        self._reload_attributes = False
        self._reminded = None
        self._reminder_date = None
        self._request_uris = []
        self._resource_type = ResourceType.TASKS
        self._security_label = None
        self._status = None
        self._tags = []
        self._weblink = None

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

    """ tasks object methods """

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
    # assignee
    #
    @property
    def assignee(self):
        """ """
        return self._assignee

    def set_assignee(self, data, update=True):
        """Read-Write task metadata"""
        self._assignee = self._uni(data)
        
        if update and self._phase == 0:
            self._phase = 2

    #
    # date_added
    #
    @property
    def date_added(self):
        """ """
        return self._date_added

    def set_date_added(self, data):
        """Read-Only task metadata"""
        self._date_added = data

    #
    # due_date
    #
    @property
    def due_date(self):
        """ """
        return self._due_date

    def set_due_date(self, data, update=True):
        """Read-Write task metadata"""
        self._due_date = data
        
        if update and self._phase == 0:
            self._phase = 2

    #
    # escalated
    #
    @property
    def escalated(self):
        """ """
        return self._escalated

    def set_escalated(self, data, update=True):
        """Read-Write task metadata"""
        self._escalated = data
        
        if update and self._phase == 0:
            self._phase = 2
            
    #
    # escalation_date
    #
    @property
    def escalation_date(self):
        """ """
        return self._escalation_date

    def set_escalation_date(self, data, update=True):
        """Read-Write task metadata"""
        self._escalation_date = data
        
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
        """Read-Only task metadata"""
        if isinstance(data, (int, long)):
            self._id = data

            if update:
                self._phase = 2
        else:
            raise RuntimeError(ErrorCodes.e10020.value.format(data))

    #
    # matched filters
    #
    @property
    def matched_filters(self):
        """ """
        return self._matched_filters

    def add_matched_filter(self, data):
        """ """
        if data is not None and data not in self._matched_filters:
            self._matched_filters.append(data)

    #
    # name
    #
    @property
    def name(self):
        """ """
        return self._uni(self._name)

    def set_name(self, data, update=True):
        """Read-Write task metadata"""
        self._name = self._uni(data)
        if update and self._phase == 0:
            self._phase = 2
            
    #
    # overdue
    #
    @property
    def overdue(self):
        """ """
        return self._overdue

    def set_overdue(self, data, update=True):
        """Read-Write task metadata"""
        self._overdue = data
        
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
        """Read-Only task metadata"""
        self._owner_name = self._uni(data)

    #
    # reminded
    #
    @property
    def reminded(self):
        """ """
        return self._reminded

    def set_reminded(self, data, update=True):
        """Read-Write task metadata"""
        self._reminded = data
        
        if update and self._phase == 0:
            self._phase = 2

    #
    # reminder_date
    #
    @property
    def reminder_date(self):
        """ """
        return self._reminder_date

    def set_reminder_date(self, data, update=True):
        """Read-Write task metadata"""
        self._reminder_date = data
        
        if update and self._phase == 0:
            self._phase = 2

    #
    # status
    #
    @property
    def status(self):
        """ """
        return self._status

    def set_status(self, data, update=True):
        """Read-Write task metadata"""
        self._status = data
        
        if update and self._phase == 0:
            self._phase = 2
            
    #
    # weblink
    #
    @property
    def weblink(self):
        """ """
        return self._weblink

    def set_weblink(self, data):
        """ """
        self._weblink = self._uni(data)

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

        printable_string = '\n{0!s:_^80}\n'.format('Task Resource Object Properties')

        #
        # retrievable methods
        #
        printable_string += '{0!s:40}\n'.format('Retrievable Methods')
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('id', self.id))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('name', self.name))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('resource_type', self.resource_type))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('owner_name', self.owner_name))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('date_added', self.date_added))
        
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('escalated', self.escalated))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('escalation_date', self.escalation_date))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('overdue', self.overdue))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('reminded', self.reminded))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('reminder_date', self.reminder_date))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('status', self.status))
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


class TaskObjectAdvanced(TaskObject):
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
        super(TaskObject, self).__init__()
        
        self._resource_properties = ApiProperties.api_properties[resource_obj.resource_type.name]['properties']
        
        self._resource_container = resource_container
        self._resource_obj = resource_obj
        self._basic_structure = {
            'dateAdded': 'date_added',
            'dueDate': 'due_date',
            'escalated': 'escalated',
            'escalation_date': 'escalation_date',
            'id': 'id',
            'name': 'name',
            'overdue': 'overdue',
            'ownerName': 'owner_name',
            'reminded': 'reminded',
            'reminderDate': 'reminder_date',
            'status': 'status',
            'weblink': 'weblink',
        }
        self._structure = self._basic_structure.copy()
        self._tc = tc_obj
        self._tc.tcl = tc_obj.tcl

        # load data from resource_obj
        self.load_data(self._resource_obj)

    def add_assignee(self, assignee):
        """ add assignee to task by id """
        prop = self._resource_properties['assignee_add']
        ro = RequestObject()
        ro.set_description('add assignee {0} from "{1}"'.format(assignee, self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(
            self._id, assignee))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        self._resource_container.add_commit_queue(self.id, ro)

    def add_attribute(self, attr_type, attr_value, attr_displayed='true'):
        """ add an attribute to a task """
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
            
    def add_escalatee(self, escalatee):
        """ add escalatee to task by id """
        prop = self._resource_properties['escalatee_add']
        ro = RequestObject()
        ro.set_description('add escalatee {0} from "{1}"'.format(escalatee, self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(
            self._id, escalatee))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        self._resource_container.add_commit_queue(self.id, ro)

    def add_security_label(self, label):
        """ set the security label for this task """
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
        """ add a tag to an task """
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
        """ associate a group to task by id """
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

    def associate_indicator(self, indicator_type, indicator):
        """ associate a indicator to task by id """
        prop = self._resource_properties['association_indicator_add']
        ro = RequestObject()
        ro.set_description('associate indicator {0} to "{1}"'.format(
            indicator, self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_resource_pagination(prop['pagination'])
        indicator_uri_attribute = ApiProperties.api_properties[indicator_type.name]['uri_attribute']
        # ro.set_request_uri(prop['uri'].format(indicator_uri_attribute, self._urlsafe(indicator), self.id))
        ro.set_request_uri(prop['uri'].format(self.id, indicator_uri_attribute, self._urlsafe(indicator)))
        ro.set_resource_type(self._resource_type)
        self._resource_container.add_commit_queue(self.id, ro)

    def associate_victim(self, resource_id):
        """ associate victim to task """
        prop = self._resource_properties['association_victim_add']
        ro = RequestObject()
        ro.set_description('associate victim id {0} from "{1}"'.format(
            resource_id, self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(
            self._id, resource_id))
        ro.set_resource_pagination(prop['pagination'])
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

        # phase 0 (no action) -> don't validate and don't POST group, only POST items in commit queue.
        # phase 1 (add) -> validate before POST group, only POST items in commit queue if group POST succeeded.
        # phase 2 (update) -> don't validate before PUT group, POST/PUT items in commit queue.

        """ commit group and related associations, attributes, security labels and tags """
        r_id = self.id
        ro = RequestObject()
        ro.set_body(self.gen_body)
        if self.owner_name is not None:
            ro.set_owner(self.owner_name)
        ro.set_resource_type(self.resource_type)
        if self.phase == 1:
            prop = self._resource_properties['add']
            ro.set_description('adding task "{0}".'.format(self._name))
            ro.set_http_method(prop['http_method'])
            ro.set_owner_allowed(prop['owner_allowed'])
            ro.set_request_uri(prop['uri'].format(self._id))
            ro.set_resource_pagination(prop['pagination'])
            
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
            ro.set_description('update group "{0}".'.format(self._name))
            ro.set_http_method(prop['http_method'])
            ro.set_owner_allowed(prop['owner_allowed'])
            ro.set_request_uri(prop['uri'].format(self._id))
            ro.set_resource_pagination(prop['pagination'])
            
            api_response = self._tc.api_request(ro)
            if api_response.headers['content-type'] == 'application/json':
                api_response_dict = api_response.json()
                if api_response_dict['status'] != 'Success':
                    self._tc.tcl.error('API Request Failure: [{0}]'.format(ro.description))

        # validate all required fields are present

        if r_id is not None:
            #
            # commit all associations, attributes, tags, etc
            #
            for ro in self._resource_container.commit_queue(self.id):
                if self.owner_name is not None:
                    ro.set_owner(self.owner_name)

                # replace the id
                if self.phase == 1 and self.id != r_id:
                    request_uri = str(ro.request_uri.replace(str(self.id), str(r_id)))
                    ro.set_request_uri(request_uri)
                    self._tc.tcl.debug('Replacing {0} with {1}'.format(self.id, str(r_id)))

                api_response2 = self._tc.api_request(ro)
                if 'content-type' in api_response2.headers:
                    if api_response2.headers['content-type'] == 'application/json':
                        api_response_dict2 = api_response2.json()
                        if api_response_dict2['status'] != 'Success':
                            self._tc.tcl.error('API Request Failure: [{0}]'.format(ro.description))
                        else:
                            if ro.success_callback is not None:
                                ro.success_callback(ro, api_response2)
                    elif api_response2.headers['content-type'] == 'application/octet-stream':
                        if api_response2.status_code in [200, 201, 202]:
                            self.set_contents(ro.body)
                            if ro.success_callback is not None:
                                ro.success_callback(ro, api_response2)
                else:
                    # upload PUT response
                    if api_response2.status_code in [200, 201, 202]:
                        self.set_contents(ro.body)
                        if ro.success_callback is not None:
                            ro.success_callback(ro, api_response2)

            # clear the commit queue
            self._resource_container.clear_commit_queue_id(self.id)

            self.set_id(r_id)

        # clear phase
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
        ro.set_description('delete task "{0}".'.format(self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        if self.owner_name is not None:
            ro.set_owner(self.owner_name)
        ro.set_request_uri(prop['uri'].format(self._id))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self.resource_type)
        self._tc.api_request(ro)
        self.set_phase(3)
        
    def delete_assignee(self, assignee):
        """ delete assignee from task by id """
        prop = self._resource_properties['assignee_delete']
        ro = RequestObject()
        ro.set_description('delete assignee {0} from "{1}"'.format(assignee, self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(
            self._id, assignee))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        self._resource_container.add_commit_queue(self.id, ro)

    def delete_attribute(self, attr_id):
        """ delete attribute from task by id """
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

    def delete_escalatee(self, escalatee):
        """ delete escalatee from task by id """
        prop = self._resource_properties['escalatee_delete']
        ro = RequestObject()
        ro.set_description('delete escalatee {0} from "{1}"'.format(escalatee, self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(
            self._id, escalatee))
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
        """ delete tag from task """
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
        """ disassociate group from task """
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

    def disassociate_indicator(self, indicator_type, indicator):
        """ disassociate indicator from task by id """
        prop = self._resource_properties['association_indicator_delete']
        ro = RequestObject()
        ro.set_description('disassociate indicator {0} to "{1}"'.format(
            indicator, self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_resource_pagination(prop['pagination'])
        indicator_uri_attribute = ApiProperties.api_properties[indicator_type.name]['uri_attribute']
        ro.set_request_uri(prop['uri'].format(indicator_uri_attribute, self._urlsafe(indicator), self.id))
        ro.set_resource_type(self._resource_type)
        self._resource_container.add_commit_queue(self.id, ro)

    def disassociate_victim(self, resource_id):
        """ disassociate victim from task """
        prop = self._resource_properties['association_victim_delete']
        ro = RequestObject()
        ro.set_description('disassociate victim id {0} from "{1}"'.format(
            resource_id, self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(
            self._id, resource_id))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        self._resource_container.add_commit_queue(self.id, ro)

    def download(self):
        """ download document  """
        if self._resource_type == ResourceType.DOCUMENTS:
            prop = self._resource_properties['document_download']
        elif self._resource_type == ResourceType.SIGNATURES:
            prop = self._resource_properties['signature_download']
        else:
            self._tc.tcl.error('Download requested for wrong resource type.')
            raise AttributeError(ErrorCodes.e10320.value)

        ro = RequestObject()
        ro.set_description('download {0} for "{1}"'.format(self.resource_type.name.lower(), self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(self._id))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        api_response = self._tc.api_request(ro)

        if api_response.headers['content-type'] in ['application/octet-stream', 'text/plain']:
            self.set_contents(api_response.content)

    @property
    def group_associations(self):
        """ retrieve associations for this task. associations are not stored within the object """
        prop = self._resource_properties['association_groups']
        ro = RequestObject()
        ro.set_description('retrieve group associations for {0}'.format(self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(self._id))
        ro.set_owner(self.owner_name)
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)

        for item in self._tc.result_pagination(ro, 'group'):
            yield parse_group(item, api_filter=ro.description, request_uri=ro.request_uri)

    @property
    def indicator_associations(self):
        """ retrieve associations for this task. associations are not stored within the object """
        prop = self._resource_properties['association_indicators']
        ro = RequestObject()
        ro.set_description('retrieve indicator associations for {0}'.format(self._name))
        ro.set_owner(self.owner_name)
        ro.set_http_method(prop['http_method'])
        ro.set_owner(self.owner_name)
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(self._id))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)

        for item in self._tc.result_pagination(ro, 'indicator'):
            import IndicatorObject  #Causes circular import

            yield IndicatorObject.parse_indicator(
                item, api_filter=ro.description, request_uri=ro.request_uri, indicators_regex=self._tc._indicators_regex)

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

    def load_attributes(self, automatically_reload=False):
        self._reload_attributes = automatically_reload
        """ retrieve attributes for this task """
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

    def load_data(self, resource_obj):
        """ load data from resource object to self """
        for key in resource_obj.__slots__:
            setattr(self, key, getattr(resource_obj, key))

    def load_security_label(self):
        """ retrieve security label for this task """
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
        """ retrieve tags for this task """
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

    def update_attribute(self, attr_id, attr_value):
        """ update task attribute by id """
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

    @property
    def victim_associations(self):
        """ retrieve associations for this tasks. associations are not stored within the object """
        prop = self._resource_properties['association_victims']
        ro = RequestObject()
        ro.set_description('retrieve victim associations for {0}'.format(self._name))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_owner(self.owner_name)
        ro.set_request_uri(prop['uri'].format(self._id))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)

        for item in self._tc.result_pagination(ro, 'victim'):
            yield parse_victim(item, api_filter=ro.description, request_uri=ro.request_uri)

    #
    # attributes
    #
    @property
    def attributes(self):
        """ """
        return self._resource_obj._attributes
        
        
"""
{
    "status": "Success",
    "data": {
        "resultCount": 1,
        "task": [
            {
                "id": 22,
                "name": "Test Task",
                "ownerName": "SumX",
                "dateAdded": "2016-04-22T13:07:36Z",
                "webLink": "https://ti.sumx.us/auth/workflow/task.xhtml?task=22",
                "status": "Not Started",
                "escalated": false,
                "reminded": false,
                "overdue": false,
                "dueDate": "2016-04-29T00:00:00Z",
                "reminderDate": "2016-04-26T13:06:00Z",
                "escalationDate": "2016-05-04T13:06:00Z"
            }
        ]
    }
}

{
    "status": "Success",
    "data": {
        "task": {
            "id": 22,
            "name": "Test Task",
            "owner": {
                "id": 2,
                "name": "SumX",
                "type": "Organization"
            },
            "dateAdded": "2016-04-22T13:07:36Z",
            "webLink": "https://ti.sumx.us/auth/workflow/task.xhtml?task=22",
            "status": "Not Started",
            "escalated": false,
            "reminded": false,
            "overdue": false,
            "dueDate": "2016-04-29T00:00:00Z",
            "reminderDate": "2016-04-26T13:06:00Z",
            "escalationDate": "2016-05-04T13:06:00Z",
            "assignee": [
                {
                    "userName": "bsummers",
                    "firstName": "Bracey",
                    "lastName": "Summers"
                }
            ]
        }
    }
}
"""