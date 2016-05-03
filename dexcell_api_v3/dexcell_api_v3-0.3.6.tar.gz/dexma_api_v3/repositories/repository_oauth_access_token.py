__author__ = 'dcortes'

from dexma_api_v3.gateway.gateway_oauth_access_token import GatewayOauthAccessToken


class RepositoryOauthAccessToken():

    def __init__(self, id, secret, endpoint):
        self.gateway = GatewayOauthAccessToken(id, secret, endpoint)

    def get(self, dep_token):
        token = self.gateway.get(dep_token)
        if type(token) in [str, unicode]: return token
        else: raise Exception("bad token")