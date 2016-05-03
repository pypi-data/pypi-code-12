__author__ = 'dcortes'

from repository_base import RepositoryBase
from dexma_api_v3.gateway.gateway_session import GatewaySession
from dexma_api_v3.factory.session import Session


class RepositorySession(RepositoryBase):

    def __init__(self, endpoint):
        self.gateway = GatewaySession(endpoint)

    def _validate_session(self, session_dict):
        session = Session(session_dict)
        session.validate()
        return session

    def get(self, token, hash):
        session_dict = self.gateway.get(token, hash)
        return self._validate_session(session_dict)