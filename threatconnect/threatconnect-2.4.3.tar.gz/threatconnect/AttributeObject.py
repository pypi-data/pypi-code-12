""" standard """
import ApiProperties
from RequestObject import RequestObject
from SecurityLabelObject import parse_security_label, SecurityLabelObject

""" custom """
from ErrorCodes import ErrorCodes


def parse_attribute(attribute_dict, container):
    """ """
    # store the resource object in the master resource object list
    # roi = resource_obj.add_master_resource_obj(AttributeObject(), attribute_dict['id'])

    # retrieve the resource object and update data
    # attribute = resource_obj.get_resource_by_identity(roi)
    attribute = AttributeObject(container)

    #
    # standard values
    #
    attribute.set_date_added(attribute_dict['dateAdded'])
    attribute.set_displayed(attribute_dict['displayed'])
    attribute.set_id(attribute_dict['id'])
    attribute.set_last_modified(attribute_dict['lastModified'])
    attribute.set_type(attribute_dict['type'])
    attribute.set_value(attribute_dict['value'])

    return attribute


class AttributeObject(object):
    __slots__ = (
        '_date_added',
        '_displayed',
        '_id',
        '_last_modified',
        '_required_attrs',
        '_type',
        '_value',
        '_validated',
        '_writable_attrs',
        '_resource_properties',
        '_security_labels',
        '_container'
    )

    def __init__(self, container):
        self._resource_properties = ApiProperties.api_properties['ATTRIBUTES']['properties']
        self._date_added = None
        self._displayed = None
        self._id = None
        self._last_modified = None
        self._required_attrs = ['type', 'value']
        self._type = None
        self._value = None
        self._security_labels = []
        self._container = container
        self._writable_attrs = {
            '_displayed': 'set_displayed',
            '_type': 'set_type',
            '_value': 'set_value'
        }

        # validation
        self._validated = False

    #
    # unicode
    #
    @staticmethod
    def _uni(data):
        """ """
        if isinstance(data, (int, list, dict)):
            return data
        elif isinstance(data, unicode):
            return unicode(data.encode('utf-8').strip(), errors='ignore')  # re-encode poorly encoded unicode
        elif not isinstance(data, unicode):
            return unicode(data, 'utf-8', errors='ignore')
        else:
            return data

    """ shared attribute methods """

    #
    # date_added
    #
    @property
    def date_added(self):
        """ """
        return self._date_added

    def set_date_added(self, data):
        """Read-Only attribute metadata"""
        self._date_added = data

    #
    # displayed
    #
    @property
    def displayed(self):
        """ """
        return self._displayed

    def set_displayed(self, data):
        """Read-Write attribute metadata"""
        self._displayed = data

    #
    # id
    #
    @property
    def id(self):
        """ """
        return self._id

    def set_id(self, data):
        """Read-Only attribute metadata"""
        if isinstance(data, int):
            self._id = data
        else:
            raise AttributeError(ErrorCodes.e10020.value.format(data))

    #
    # last_modified
    #
    @property
    def last_modified(self):
        """ """
        return self._last_modified

    def set_last_modified(self, data):
        """Read-Only attribute metadata"""
        self._last_modified = data

    #
    # type
    #
    @property
    def type(self):
        """ """
        return self._type

    def set_type(self, data):
        """Read-Write attribute metadata"""
        self._type = self._uni(data)

    #
    # value
    #
    @property
    def value(self):
        """ """
        return self._value

    def set_value(self, data):
        """Read-Write attribute metadata"""
        self._value = self._uni(data)

    #
    # validated
    #
    @property
    def validated(self):
        """ """
        return self._validated

    def validate(self):
        """ """
        for required in self._required_attrs:
            if getattr(self, required) is None:
                self._validated = False
                return

        self._validated = True

    def load_security_labels(self):
        """ retrieve attributes for this indicator """
        prop = self._resource_properties['load_security_labels']
        ro = RequestObject()
        ro.set_description('load security labels for attribute {0} of object {1}'.format(self.id, self._container.id))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        resource_uri = self._container._resource_properties['id']['uri']
        try:
            resource_uri = resource_uri.format(self._container.indicator)
        except AttributeError:
            resource_uri = resource_uri.format(self._container.id)
        ro.set_request_uri(prop['uri'].format(resource_uri, self.id))
        ro.set_resource_pagination(prop['pagination'])
        api_response = self._container._tc.api_request(ro)

        if api_response.headers['content-type'] == 'application/json':
            api_response_dict = api_response.json()
            if api_response_dict['status'] == 'Success':
                self._security_labels = []
                data = api_response_dict['data']['securityLabel']
                for item in data:
                    self.__add_security_label(parse_security_label(item))  # add to main resource object

    def delete_security_label(self, security_label_name):
        """ retrieve attributes for this indicator """
        prop = self._resource_properties['delete_security_label']
        ro = RequestObject()
        ro.set_description('deleting security label {0} for attribute {1} of object {2}'.format(security_label_name,
                                                                                                self.id,
                                                                                                self._container.id))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        resource_uri = self._container._resource_properties['id']['uri']
        try:
            resource_uri = resource_uri.format(self._container.indicator)
        except AttributeError:
            resource_uri = resource_uri.format(self._container.id)
        ro.set_request_uri(prop['uri'].format(resource_uri, self.id, security_label_name))
        ro.set_resource_pagination(prop['pagination'])

        self._container._resource_container.add_commit_queue(self._container.id, ro)

    def __add_security_label(self, security_label):
        self._security_labels.append(security_label)

    def add_security_label(self, security_label_name):
        """ retrieve attributes for this indicator """
        prop = self._resource_properties['add_security_label']
        ro = RequestObject()
        ro.set_description('deleting security label {0} for attribute {1} of object {2}'.format(security_label_name,
                                                                                                self.id,
                                                                                                self._container.id))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        resource_uri = self._container._resource_properties['id']['uri']
        try:
            resource_uri = resource_uri.format(self._container.indicator)
        except AttributeError:
            resource_uri = resource_uri.format(self._container.id)
        ro.set_request_uri(prop['uri'].format(resource_uri, self.id, security_label_name))
        ro.set_resource_pagination(prop['pagination'])
        callback = lambda status: self.__failed_add_security_label(security_label_name)
        ro.set_failure_callback(callback)
        self._container._resource_container.add_commit_queue(self._container.id, ro)

        security_label = SecurityLabelObject()
        security_label.set_name(security_label_name)
        self.__add_security_label(security_label)

    def __failed_add_security_label(self, security_label_name):
        for security_label in self._security_labels:
            if security_label.name == security_label_name:
                self._security_labels.remove(security_label)
                break

    #
    # security_labels
    #
    @property
    def security_labels(self):
        """ """
        return self._security_labels

    #
    # add print method
    #
    def __str__(self):
        """allow object to be displayed with print"""

        printable_string = '\n{0!s:_^80}\n'.format('Attribute Object Properties')

        #
        # retrievable methods
        #
        printable_string += '{0!s:40}\n'.format('Retrievable Methods')
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('id', self.id))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('type', self.type))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('value', self.value))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('displayed', self.displayed))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('date_added', self.date_added))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('last_modified', self.last_modified))

        return printable_string
