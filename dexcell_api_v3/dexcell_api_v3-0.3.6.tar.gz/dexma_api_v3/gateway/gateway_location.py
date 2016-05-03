__author__ = 'dcortes'

from gateway_base import GatewayBase


class GatewayLocation(GatewayBase):

    def __init__(self, endpoint, http_management=None):
        call = "locations"
        super(GatewayLocation, self).__init__(endpoint, call, http_management=http_management)

    def get(self, token, id):
        return super(GatewayLocation, self).get(token, id)

    def fetch(self, token, parameters=None):
        parameters = parameters.deepcopy() if parameters is not None else {}
        parameters["limit"] = 200 if "limit" not in parameters else parameters["limit"]
        parameters["start"] = 0 if "start" not in parameters else parameters["start"]
        data = super(GatewayLocation, self).fetch(token, parameters)
        while len(data) == parameters["limit"]:
            parameters["start"] += 1
            some_locations = super(GatewayLocation, self).fetch(token, parameters)
            data.extend(some_locations)
        return data

    def save(self, token, location):
        """ #TODO """
        return