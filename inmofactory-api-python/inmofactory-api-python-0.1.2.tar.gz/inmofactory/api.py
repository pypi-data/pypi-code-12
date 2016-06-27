# coding=utf-8
"""
Inmofactory API
"""
__copyright__ = 'Copyright 2016, DNest'

import json
import requests
import base64

WEBSERVICE_URL = 'https://api.inmofactory.com/api/property'


class InmofactoryAPI(object):
    user = ''
    password = ''
    agency_id = ''
    agent_id = ''
    user_password_base64 = ''

    create_mandatory_params = ['ExternalId', 'AgencyReference', 'TypeId', 'PropertyStatusId', 'ShowSurface',
                               'ContactTypeId', 'IsPromotion', 'PropertyAddress', 'PropertyFeature',
                               'PropertyContactInfo', 'PropertyUser', 'PropertyTransaction']

    def __init__(self, user, password, agency_id, agent_id):
        self.user = user
        self.password = password
        self.agency_id = agency_id
        self.agent_id = agent_id

        self.user_password_base64 = base64.b64encode(
            '%s:%s' % (self.user, self.password)
        )

    def _make_request(self, json_payload=None, method='POST', url='', params={}):
        response = requests.request(method, WEBSERVICE_URL + url, json=json_payload,
                                    headers={'cache-control': 'no-cache',
                                             'content-type': 'application/json; charset=utf8',
                                             'Authorization': 'Basic %s' % self.user_password_base64},
                                    params=params)
        response_content = response.content
        response_content = response_content.replace("'", '"')
        json_dict = json.loads(response_content)
        return json_dict

    def check_params(self, property_dict):
        for param in self.create_mandatory_params:
            if param not in property_dict:
                raise Exception('You must define a %s' % param)

    def check_response(self, response_dict):
        if response_dict['StatusCode'] == '201':
            return 'OK'
        return response_dict['Message']

    def get_base_dict(self):
        return {
            'AgencyReference': self.agency_id,
            'PropertyUser': [
                {
                    'UserId': self.agent_id,
                    'IsPrincipal': True
                }
            ]
        }

    def insert(self, property_dict):
        base_dict = self.get_base_dict()
        base_dict.update(property_dict)

        response = self._make_request(json.dumps(base_dict))
        return self.check_response(response)

    def update(self, property_dict):
        base_dict = self.get_base_dict()
        base_dict.update(property_dict)

        response = self._make_request(json.dumps(base_dict), method='PUT')
        return self.check_response(response)

    def delete(self, property_id):
        response = self._make_request(method='DELETE', url='/%s' % property_id)
        return self.check_response(response)