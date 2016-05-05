""" std modules """
import types

""" custom modules """
from threatconnect import IndicatorFilterMethods
# from threatconnect.Config.ResourceProperties import ResourceProperties
from threatconnect.FilterObject import FilterObject
# from threatconnect.Properties.BulkIndicators import BulkProperties
from threatconnect.RequestObject import RequestObject
from threatconnect.Resource import Resource

""" Note: PEP 8 intentionally ignored for variable/methods to match API standard. """


class Bulk(Resource):
    """ """

    def __init__(self, tc_obj):
        """ """
        super(Bulk, self).__init__(tc_obj)
        self._filter_class = BulkFilterObject

        # set properties
        # properties = BulkProperties(base_uri=self.base_uri)
        # self._resource_type = properties.resource_type

        # create default request object for non-filtered requests
        self._request_object = RequestObject('bulk', 'default')
        # self._request_object.set_http_method(properties.http_method)
        # self._request_object.set_owner_allowed(properties.base_owner_allowed)
        # self._request_object.set_request_uri(properties.base_path)
        # self._request_object.set_resource_pagination(properties.resource_pagination)
        # self._request_object.set_resource_type(properties.resource_type)


class BulkFilterObject(FilterObject):
    """ """
    def __init__(self, base_uri, tcl):
        """ """
        super(BulkFilterObject, self).__init__(base_uri, tcl)
        self._owners = []

        # define properties for resource type
        # self._properties = BulkProperties(base_uri=self.base_uri)
        self._properties = None
        self._resource_type = self._properties.resource_type

        # create default request object for filtered request with only owners
        self._request_object = RequestObject('groups', 'default')
        self._request_object.set_http_method(self._properties.http_method)
        self._request_object.set_owner_allowed(self._properties.base_owner_allowed)
        self._request_object.set_request_uri(self._properties.base_path)
        self._request_object.set_resource_pagination(self._properties.resource_pagination)
        self._request_object.set_resource_type(self._properties.resource_type)

        #
        # add_obj filter methods
        #
        for method_name in self._properties.filters:
            method = getattr(IndicatorFilterMethods, method_name)
            setattr(self, method_name, types.MethodType(method, self))
