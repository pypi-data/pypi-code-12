""" standard """

""" custom """
from Config.FilterOperator import FilterOperator
import ApiProperties
import SharedMethods

from ErrorCodes import ErrorCodes
from PostFilterObject import PostFilterObject
from RequestObject import RequestObject


def add_id(self, data_int):
    """ """
    # validation of data input
    if not isinstance(data_int, int):
        raise AttributeError(ErrorCodes.e4030.value.format(data_int))

    prop = self._resource_properties['id']
    ro = RequestObject()
    ro.set_description('api filter by id {0}'.format(data_int))
    ro.set_http_method(prop['http_method'])
    ro.set_owner_allowed(prop['owner_allowed'])
    ro.set_request_uri(prop['uri'], [data_int])
    ro.set_resource_pagination(prop['pagination'])
    ro.set_resource_type(self._resource_type)
    self._add_request_objects(ro)

def add_indicator(self, data):
    """ filter api results by indicator """
    # validation indicator
    if not SharedMethods.validate_indicator(self.tc._indicators_regex, data):
        raise AttributeError(ErrorCodes.e5010.value.format(data))

    # get indicator uri attribute
    indicator_type = SharedMethods.get_resource_type(self.tc._indicators_regex, data)
    indicator_uri_attribute = ApiProperties.api_properties[indicator_type.name]['uri_attribute']

    prop = self._resource_properties['indicators']
    ro = RequestObject()
    ro.set_description('api filter by indicator id {0}'.format(data))
    ro.set_owner_allowed(prop['owner_allowed'])
    ro.set_request_uri(prop['uri'], [indicator_uri_attribute, SharedMethods.urlsafe(data)])
    ro.set_resource_pagination(prop['pagination'])
    ro.set_resource_type(self._resource_type)
    self._add_request_objects(ro)


#
# Post Filters
#


def add_pf_name(self, data, operator=FilterOperator.EQ):
    """ add post filter by name 
    :type operator: FilterOperator
    """
    post_filter = PostFilterObject()
    post_filter.set_description('post filter by name {0} "{1}"'.format(operator.name, data))
    post_filter.set_method('filter_name')
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
