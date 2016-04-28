from ErrorCodes import ErrorCodes
from RequestObject import RequestObject


def add_id(self, data_int):
    """ """
    # validation of data input
    if not isinstance(data_int, int):
        raise AttributeError(ErrorCodes.e4020.value.format(data_int))

    prop = self._resource_properties['id']
    ro = RequestObject()
    ro.set_description('api filter by id {0}'.format(data_int))
    ro.set_http_method(prop['http_method'])
    ro.set_owner_allowed(prop['owner_allowed'])
    ro.set_request_uri(prop['uri'], [data_int])
    ro.set_resource_pagination(prop['pagination'])
    ro.set_resource_type(self._resource_type)
    self._add_request_objects(ro)
