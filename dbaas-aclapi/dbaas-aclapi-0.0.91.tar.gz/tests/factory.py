import json
import unittest
from dbaas_aclapi.acl_base_client import AclClient


class Response(object):

    def __init__(self, data):
        self.data = json.dumps(data)


class AclApiStub(AclClient):

    def __init__(self, *args, **kwargs):
        super(AclApiStub, self).__init__(*args, **kwargs)
        self._requests = []

    def _make_request(self, http_verb, endpoint, payload=None, timeout=None):
        self._requests.append((http_verb, endpoint, payload))

        return Response({"response": True})

    @property
    def last_request(self):
        return self._requests[-1]

    def query_acls(self, payload):
        _ = 'api/ipv{}/acl/search'.format(self.ip_version)
        _ = self._make_request(http_verb="POST", endpoint=_, payload=payload)

        response = Response({'vlans': [{'environment': '13912', 'rules': [{'source': '10.236.5.68/32', 'l4-options': {'dest-port-op': 'eq', 'dest-port-start': '3306'}, 'protocol': 'tcp',
                                                                           'description': 'permit 10.236.5.68/32 access for database myown in dev', 'sequence': 18622, 'action': 'permit', 'destination': '10.236.1.45/32', 'id': '98920'}], 'kind': 'object#acl', 'num_vlan': 8}]})

        return json.loads(response.data)


class AclApiTestCase(unittest.TestCase):

    def setUp(self):
        self.base_url = 'https://acl_api.mock.test.globoi.globo.com'
        self.username = 'dbaas'
        self.password = 'dbaas'
        self.database_environment = 'dev'
        self.ip_version = 4
        self.acl_api_client = AclApiStub(
            self.base_url, self.username, self.password,
            self.database_environment, self.ip_version)


class Request(object):
    def __init__(self, user):
        self.args = [user]
