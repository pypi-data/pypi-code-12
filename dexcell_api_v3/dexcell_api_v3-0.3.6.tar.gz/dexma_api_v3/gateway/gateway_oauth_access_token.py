__author__ = 'dcortes'

from dexma_drivers.http_connector import HttpConnector


class GatewayOauthAccessToken():

    def __init__(self, id, secret, endpoint, http_management=None):
        self.id = id
        self.secret = secret
        self.call = "oauth/access-token"
        self.endpoint = endpoint
        self.http_management = http_management if http_management is not None else HttpConnector

    def get(self, temp_token):
        parameters = {"temp_token": temp_token, "secret": self.secret, "id": self.id}
        return self.http_management.post(self.endpoint, "/{}".format(self.call), data=parameters, response="str")