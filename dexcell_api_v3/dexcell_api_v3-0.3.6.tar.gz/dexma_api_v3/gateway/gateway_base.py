__author__ = 'dcortes'

import abc

from dexma_drivers.http_connector import HttpConnector


""" This is a abstract class, like an interface in java"""
class GatewayBase(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, endpoint, call, http_management=None):
        self.call = call
        self.endpoint = endpoint
        self.http_management = http_management if http_management is not None else HttpConnector

    @abc.abstractmethod
    def get(self, token, id):
        headers = {"x-dexcell-token": token}
        return self.http_management.get(self.endpoint, "/{}/{}".format(self.call, id), headers=headers)

    @abc.abstractmethod
    def fetch(self, token, parameters):
        headers = {"x-dexcell-token": token}
        return self.http_management.get(self.endpoint, "/{}".format(self.call), headers=headers, params=parameters)

    @abc.abstractmethod
    def save(self, token, id):
        headers = {"x-dexcell-token": token}
        return self.http_management.post(self.endpoint, "/{}/{}".format(id, self.call), headers=headers)
