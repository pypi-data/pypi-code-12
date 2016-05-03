__author__ = 'dcortes'

from copy import deepcopy

from gateway_base import GatewayBase


class GatewayUtilityContractElectricity(GatewayBase):

    def __init__(self, endpoint, http_management=None):
        call = "utility/contracts/electricity"
        super(GatewayUtilityContractElectricity, self).__init__(endpoint, call, http_management=http_management)

    def get(self, token, id):
        return super(GatewayUtilityContractElectricity, self).get(token, id)

    def fetch(self, token, parameters=None):
        parameters = deepcopy(parameters) if parameters is not None else {}
        parameters["limit"] = 500 if "limit" not in parameters else parameters["limit"]
        parameters["start"] = 0 if "start" not in parameters else parameters["start"]
        data = super(GatewayUtilityContractElectricity, self).fetch(token, parameters)
        while len(data) == parameters["limit"]:
            parameters["start"] += 1
            some_devices = super(GatewayUtilityContractElectricity, self).fetch(token, parameters)
            data.extend(some_devices)
        return data

    def save(self, token, device):
        """ #TODO """
        return