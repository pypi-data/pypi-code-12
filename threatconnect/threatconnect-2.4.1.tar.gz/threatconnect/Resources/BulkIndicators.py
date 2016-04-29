""" standard """
import re
import types

""" custom """
from threatconnect import IndicatorFilterMethods

from threatconnect import ApiProperties
from threatconnect.Config.ResourceType import ResourceType
from threatconnect.FilterObject import FilterObject
from threatconnect.IndicatorObject import IndicatorObjectAdvanced
from threatconnect.RequestObject import RequestObject
from threatconnect.Resource import Resource


class BulkIndicators(Resource):
    """ """

    def __init__(self, tc_obj):
        """ """
        super(BulkIndicators, self).__init__(tc_obj)

        self._filter_class = BulkIndicatorFilterObject
        self._resource_type = ResourceType.INDICATORS

    def _method_wrapper(self, resource_object):
        """ return resource object as new object with additional methods """
        return IndicatorObjectAdvanced(self.tc, self, resource_object)

    @ property
    def default_request_object(self):
        """ default request when no filters are provided """
        resource_properties = ApiProperties.api_properties[self._resource_type.name]['properties']
        # create default request object for non-filtered requests
        request_object = RequestObject()
        request_object.set_http_method(resource_properties['bulk']['http_method'])
        request_object.set_owner_allowed(resource_properties['bulk']['owner_allowed'])
        request_object.set_request_uri(resource_properties['bulk']['uri'])
        request_object.set_resource_pagination(resource_properties['bulk']['pagination'])
        request_object.set_resource_type(self._resource_type)

        return request_object


class BulkIndicatorFilterObject(FilterObject):
    """ """

    def __init__(self, tc_obj):
        """ """
        super(BulkIndicatorFilterObject, self).__init__(tc_obj)
        self._owners = []

        self._resource_type = ResourceType.INDICATORS
        self._resource_properties = ApiProperties.api_properties[self._resource_type.name]['properties']

        #
        # add_obj filter methods
        #
        for method_name in self._resource_properties['filters']:
            # only add post filters for Bulk Indicator download
            if re.findall('add_pf_', method_name):
                self.add_post_filter_names(method_name)
                method = getattr(IndicatorFilterMethods, method_name)
                setattr(self, method_name, types.MethodType(method, self))

    @ property
    def default_request_object(self):
        """ default request when only a owner filter is provided """
        request_object = RequestObject()
        request_object.set_description('filter by owner')
        request_object.set_http_method(self._resource_properties['bulk']['http_method'])
        request_object.set_owner_allowed(self._resource_properties['bulk']['owner_allowed'])
        request_object.set_request_uri(self._resource_properties['bulk']['uri'])
        request_object.set_resource_pagination(self._resource_properties['bulk']['pagination'])
        request_object.set_resource_type(self._resource_type)

        return request_object
