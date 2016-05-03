__author__ = 'dcortes'

from copy import deepcopy

from gateway_base import GatewayBase


class GatewaySession(GatewayBase):

    def __init__(self, endpoint, http_management=None):
        call = "session"
        super(GatewaySession, self).__init__(endpoint, call, http_management=http_management)

    def get(self, token, hash):
        return super(GatewaySession, self).get(token, hash)

    def fetch(self, token, parameters=None):
        pass

    def save(self, token, device):
        pass