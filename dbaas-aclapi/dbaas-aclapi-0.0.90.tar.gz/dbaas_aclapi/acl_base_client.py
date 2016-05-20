# -*- coding: utf-8 -*-
import json
import urllib3
import logging

logging.basicConfig()
LOG = logging.getLogger("AclBaseClient")
LOG.setLevel(logging.DEBUG)


def get_acl_client(database_environment):
    from util import get_credentials_for
    from dbaas_credentials.models import CredentialType
    acl_credential = get_credentials_for(database_environment,
                                         CredentialType.ACLAPI)
    return AclClient(acl_credential.endpoint, acl_credential.user, acl_credential.password,
                     database_environment)


class AclClient(object):

    def __init__(self, base_url, username, password, database_environment,
                 ip_version=4):
        LOG.info("Initializing new acl base client.")
        self.kind = ""
        self.acls = []
        self.headers = {}
        self.base_url = base_url
        self.username = username
        self.password = password
        self.ip_version = ip_version
        self.database_environment = database_environment
        self._add_basic_athentication()

    def _add_basic_athentication(self):
        LOG.info("Setting up authentication.")
        basic_auth = '{}:{}'.format(self.username, self.password)
        self.headers.update(urllib3.util.make_headers(basic_auth=basic_auth))

    def _add_content_type_json(self,):
        LOG.info("Setting up \"Content-Type\".")
        self.headers.update({'Content-Type': 'application/json'})

    def _make_request(self, http_verb, endpoint, payload=None, timeout=None):
        endpoint = self.base_url + endpoint
        http = urllib3.PoolManager()
        LOG.debug("Requesting {} on {}".format(http_verb, endpoint))

        if http_verb == 'GET':
            if timeout:
                response = http.request(method=http_verb, url=endpoint,
                                        headers=self.headers, timeout=timeout)
            else:
                response = http.request(method=http_verb, url=endpoint,
                                        headers=self.headers)
        else:
            self._add_content_type_json()
            if type(payload) is not str:
                payload = json.dumps(payload)

            LOG.info("JSON PAYLOAD: {}".format(payload))

            response = http.urlopen(method=http_verb, body=payload,
                                    url=endpoint, headers=self.headers)

        LOG.debug("Response {}".format(response.data))

        return response

    def delete_acl(self, environment_id, vlan, acl_id):
        LOG.info("Deleting ACL.")
        endpoint = "api/ipv{}/acl/{}/{}/{}".format(
            self.ip_version, environment_id, vlan, acl_id)
        response = self._make_request(http_verb="DELETE", endpoint=endpoint)

        return json.loads(response.data)

    def grant_acl_for(self, environment, vlan, payload):
        LOG.info("GRANT ACLs for {} on {}".format(vlan, environment))
        LOG.debug("Payload: {}".format(payload))
        endpoint = "api/ipv{}/acl/{}".format(
            self.ip_version, "{}/{}".format(environment, vlan))
        response = self._make_request(http_verb="PUT", endpoint=endpoint,
                                      payload=json.dumps(payload))

        json_data = json.loads(response.data)
        LOG.debug("JSON request.DATA decoded: {}".format(json_data))

        return json_data

    def get_job(self, job_id):
        LOG.info("Retrieving job {}".format(job_id))
        endpoint = "api/jobs/{}".format(job_id)
        response = self._make_request(http_verb="GET", endpoint=endpoint,)

        return json.loads(response.data)

    def run_job(self, job_id):
        LOG.info("Run job {}".format(job_id))
        endpoint = "api/jobs/{}/run".format(job_id)
        response = self._make_request(http_verb="GET", endpoint=endpoint, timeout=3.0)

        return json.loads(response.data)

    def query_acls(self, payload):
        endpoint = 'api/ipv{}/acl/search'.format(self.ip_version)
        response = self._make_request(http_verb="POST", endpoint=endpoint,
                                      payload=payload)

        return json.loads(response.data)
