""" standard """
import time

""" third-party """
import dateutil.parser

""" custom """
from Config.FilterOperator import FilterOperator
import ApiProperties
import SharedMethods

from Config.ResourceType import ResourceType
from ErrorCodes import ErrorCodes
from PostFilterObject import PostFilterObject
from RequestObject import RequestObject


def add_adversary_id(self, data_int):
    """ filter api results by adversary id """
    # validation of data input
    if not isinstance(data_int, int):
        raise AttributeError(ErrorCodes.e4000.value.format(data_int))

    prop = self._resource_properties['groups']
    ro = RequestObject()
    ro.set_description('api filter by adversary id {0}'.format(data_int))
    ro.set_http_method(prop['http_method'])
    ro.set_owner_allowed(prop['owner_allowed'])
    ro.set_request_uri(prop['uri'], ['adversaries', data_int])
    ro.set_resource_pagination(prop['pagination'])
    ro.set_resource_type(self._resource_type)
    self._add_request_objects(ro)


def add_document_id(self, data_int):
    """ filter api results by document id """
    # validation of data input
    if not isinstance(data_int, int):
        raise AttributeError(ErrorCodes.e4020.value.format(data_int))

    prop = self._resource_properties['groups']
    ro = RequestObject()
    ro.set_description('api filter by documents id {0}'.format(data_int))
    ro.set_http_method(prop['http_method'])
    ro.set_owner_allowed(prop['owner_allowed'])
    ro.set_request_uri(prop['uri'], ['documents', data_int])
    ro.set_resource_pagination(prop['pagination'])
    ro.set_resource_type(self._resource_type)
    self._add_request_objects(ro)


def add_email_id(self, data_int):
    """ filter api results by email id """
    # validation of data input
    if not isinstance(data_int, int):
        raise AttributeError(ErrorCodes.e4030.value.format(data_int))

    prop = self._resource_properties['groups']
    ro = RequestObject()
    ro.set_description('api filter by email id {0}'.format(data_int))
    ro.set_http_method(prop['http_method'])
    ro.set_owner_allowed(prop['owner_allowed'])
    ro.set_request_uri(prop['uri'], ['emails', data_int])
    ro.set_resource_pagination(prop['pagination'])
    ro.set_resource_type(self._resource_type)
    self._add_request_objects(ro)


def add_incident_id(self, data_int):
    """ filter api results by incident id """
    # validation of data input
    if not isinstance(data_int, int):
        raise AttributeError(ErrorCodes.e4040.value.format(data_int))

    prop = self._resource_properties['groups']
    ro = RequestObject()
    ro.set_description('api filter by incident id {0}'.format(data_int))
    ro.set_http_method(prop['http_method'])
    ro.set_owner_allowed(prop['owner_allowed'])
    ro.set_request_uri(prop['uri'], ['incidents', data_int])
    ro.set_resource_pagination(prop['pagination'])
    ro.set_resource_type(self._resource_type)
    self._add_request_objects(ro)


def add_indicator(self, data, indicator_type = None):
    """ filter api results by indicator """
    # validation indicator
    if not SharedMethods.validate_indicator(self.tc._indicators_regex, data):
        raise AttributeError(ErrorCodes.e5010.value.format(data))

    # get indicator uri attribute

    if indicator_type is None:
        indicator_type = SharedMethods.get_resource_type(self.tc._indicators_regex, data)
    indicator_uri_attribute = ApiProperties.api_properties[indicator_type.name]['uri_attribute']



    prop = self._resource_properties['indicator']
    ro = RequestObject()
    ro.set_description('api filter by indicator id {0}'.format(data))
    ro.set_owner_allowed(prop['owner_allowed'])
    # TODO: Check this logic
    if self._resource_type == ResourceType.INDICATORS:
        ro.set_request_uri(prop['uri'], [indicator_uri_attribute, SharedMethods.urlsafe(data)])
    else:
        ro.set_request_uri(prop['uri'], [SharedMethods.urlsafe(data)])
    ro.set_resource_pagination(prop['pagination'])
    ro.set_resource_type(indicator_type)
    self._add_request_objects(ro)


def add_security_label(self, data):
    """ filter api results by security label """
    # validation of data input
    if not isinstance(data, str):
        raise AttributeError(ErrorCodes.e4050.value.format(data))

    prop = self._resource_properties['security_labels']
    ro = RequestObject()
    ro.set_description('api filter by security label "{0}"'.format(data))
    ro.set_owner_allowed(prop['owner_allowed'])
    ro.set_resource_pagination(prop['pagination'])
    ro.set_request_uri(prop['uri'], [SharedMethods.urlsafe(data)])
    ro.set_resource_type(self._resource_type)
    self._add_request_objects(ro)


def add_signature_id(self, data_int):
    """ filter api results by signature id """
    # validation of data input
    if not isinstance(data_int, int):
        raise AttributeError(ErrorCodes.e4060.value.format(data_int))

    prop = self._resource_properties['groups']
    ro = RequestObject()
    ro.set_description('api filter by signature id {0}'.format(data_int))
    ro.set_http_method(prop['http_method'])
    ro.set_owner_allowed(prop['owner_allowed'])
    ro.set_request_uri(prop['uri'], ['signatures', data_int])
    ro.set_resource_pagination(prop['pagination'])
    ro.set_resource_type(self._resource_type)
    self._add_request_objects(ro)


def add_tag(self, data):
    """ filter api results by tag """
    # validation of data input
    if not isinstance(data, str):
        raise AttributeError(ErrorCodes.e4070.value.format(data))

    prop = self._resource_properties['tags']
    ro = RequestObject()
    ro.set_description('api filter by tag "{0}"'.format(data))
    ro.set_owner_allowed(prop['owner_allowed'])
    ro.set_resource_pagination(prop['pagination'])
    ro.set_request_uri(prop['uri'], [SharedMethods.urlsafe(data)])
    ro.set_resource_type(self._resource_type)
    self._add_request_objects(ro)


def add_task_id(self, data_int):
    """ """
    if not isinstance(data_int, int):
        raise AttributeError(ErrorCodes.e4080.value.format(data_int))

    prop = self._resource_properties['tasks']
    ro = RequestObject()
    ro.set_description('api filter by tasks id {0}'.format(data_int))
    ro.set_http_method(prop['http_method'])
    ro.set_owner_allowed(prop['owner_allowed'])
    ro.set_request_uri(prop['uri'], [data_int])
    ro.set_resource_pagination(prop['pagination'])
    ro.set_resource_type(self._resource_type)
    self._add_request_objects(ro)


def add_threat_id(self, data_int):
    """ filter api results by threat id """
    # validation of data input
    if not isinstance(data_int, int):
        raise AttributeError(ErrorCodes.e4080.value.format(data_int))

    prop = self._resource_properties['groups']
    ro = RequestObject()
    ro.set_description('api filter by threat id {0}'.format(data_int))
    ro.set_http_method(prop['http_method'])
    ro.set_owner_allowed(prop['owner_allowed'])
    ro.set_request_uri(prop['uri'], ['threats', data_int])
    ro.set_resource_pagination(prop['pagination'])
    ro.set_resource_type(self._resource_type)
    self._add_request_objects(ro)


def add_victim_id(self, data_int):
    """ filter api results by victim id """
    # validation of data input
    if not isinstance(data_int, int):
        raise AttributeError(ErrorCodes.e4090.value.format(data_int))

    prop = self._resource_properties['victims']
    ro = RequestObject()
    ro.set_description('api filter by victim id {0}'.format(data_int))
    ro.set_owner_allowed(prop['owner_allowed'])
    ro.set_resource_pagination(prop['pagination'])
    ro.set_request_uri(prop['uri'], [data_int])
    ro.set_resource_type(self._resource_type)
    self._add_request_objects(ro)


#
# Post Filters
#


def add_pf_attribute(self, data, operator=FilterOperator.EQ):
    """ add post filter by attribute
    :type operator: FilterOperator
    """
    post_filter = PostFilterObject()
    post_filter.set_description('post filter by attribute {0} {1}'.format(operator.name, data))
    post_filter.set_method('filter_attribute')
    post_filter.set_filter(data)
    post_filter.set_operator(operator)
    self.add_post_filter(post_filter)


def add_pf_confidence(self, data, operator=FilterOperator.EQ):
    """ add post filter by confidence
    :type operator: FilterOperator
    """
    post_filter = PostFilterObject()
    post_filter.set_description('post filter by confidence {0} {1}'.format(operator.name, data))
    post_filter.set_method('filter_confidence')
    post_filter.set_filter(data)
    post_filter.set_operator(operator)
    self.add_post_filter(post_filter)


def add_pf_date_added(self, data_date, operator=FilterOperator.EQ):
    """ add post filter by date
    :type operator: FilterOperator
    """
    # properly format date
    date_added = data_date
    date_added = dateutil.parser.parse(date_added)
    date_added_seconds = int(time.mktime(date_added.timetuple()))

    post_filter = PostFilterObject()
    post_filter.set_description('post filter by date added {0} {1} seconds'.format(operator.name, date_added_seconds))
    post_filter.set_method('filter_date_added')
    post_filter.set_filter(date_added_seconds)
    post_filter.set_operator(operator)
    self.add_post_filter(post_filter)


def add_pf_file_type(self, data, operator=FilterOperator.EQ):
    """ add post filter by file type
    :type operator: FilterOperator
    """
    post_filter = PostFilterObject()
    post_filter.set_description('post filter by file type {0} {1}'.format(operator.name, data))
    post_filter.set_method('filter_file_type')
    post_filter.set_filter(data)
    post_filter.set_operator(operator)
    self.add_post_filter(post_filter)


def add_pf_last_modified(self, data_date, operator=FilterOperator.EQ):
    """ add post filter by last modified
    :type operator: FilterOperator
    """
    # properly format date
    last_modified = data_date
    last_modified = dateutil.parser.parse(last_modified)
    last_modified_seconds = int(time.mktime(last_modified.timetuple()))

    post_filter = PostFilterObject()
    post_filter.set_description('post filter by last modified {0} {1} seconds'.format(
        operator.name, last_modified_seconds))
    post_filter.set_method('filter_last_modified')
    post_filter.set_filter(last_modified_seconds)
    post_filter.set_operator(operator)
    self.add_post_filter(post_filter)


def add_pf_rating(self, data, operator=FilterOperator.EQ):
    """ add post filter by rating
    :type operator: FilterOperator
    """
    post_filter = PostFilterObject()
    post_filter.set_description('post filter by rating {0} {1}'.format(operator.name, data))
    post_filter.set_method('filter_rating')
    post_filter.set_filter(data)
    post_filter.set_operator(operator)
    self.add_post_filter(post_filter)


def add_pf_threat_assess_confidence(self, data, operator=FilterOperator.EQ):
    """ add post filter by threat assesses confidence
    :type operator: FilterOperator
    """
    post_filter = PostFilterObject()
    post_filter.set_description('post filter by threat assess confidence {0} {1}'.format(operator.name, data))
    post_filter.set_method('filter_threat_assess_confidence')
    post_filter.set_filter(data)
    post_filter.set_operator(operator)
    self.add_post_filter(post_filter)


def add_pf_threat_assess_rating(self, data, operator=FilterOperator.EQ):
    """ add post filter by threat assesses rating
    :type operator: FilterOperator
    """
    post_filter = PostFilterObject()
    post_filter.set_description('post filter by threat assess rating {0} {1}'.format(operator.name, data))
    post_filter.set_method('filter_threat_assess_rating')
    post_filter.set_filter(data)
    post_filter.set_operator(operator)
    self.add_post_filter(post_filter)


def add_pf_tag(self, data, operator=FilterOperator.EQ):
    """ add post filter by tag
    :type operator: FilterOperator
    """
    post_filter = PostFilterObject()
    post_filter.set_description('post filter by tag {0} {1}'.format(operator.name, data))
    post_filter.set_method('filter_tag')
    post_filter.set_filter(data)
    post_filter.set_operator(operator)
    self.add_post_filter(post_filter)


def add_pf_type(self, data, operator=FilterOperator.EQ):
    """ add post filter by type 
    :type operator: FilterOperator
    """
    post_filter = PostFilterObject()
    post_filter.set_description('post filter by type {0} {1}'.format(operator.name, data))
    post_filter.set_method('filter_type')
    post_filter.set_filter(data)
    post_filter.set_operator(operator)
    self.add_post_filter(post_filter)
