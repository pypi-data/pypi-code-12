from __future__ import unicode_literals

import chargehound
import requests
from chargehound.error import create_chargehound_error
from chargehound.version import VERSION


class APIRequestor(object):

    def parse_response(self, response):
        payload = response.json()
        if response.status_code < 400:
            return payload
        else:
            raise create_chargehound_error(payload)

    def handle_callback(self, callback):
        def handle_response(response,  **kwargs):
            parsed = self.parse_response(response)
            callback(parsed)
        return handle_response

    def get_url(self, path):
        return 'https://' + chargehound.host + chargehound.base_path + path

    def make_request(self, method, path, params=None, data=None,
                     callback=None):
        headers = {
            'accept': 'application/json',
            'user-agent': 'Chargehound/v1 PythonBindings/%s' % VERSION
        }

        auth = (chargehound.api_key, '')

        if callback:
            hooks = dict(response=self.handle_callback(callback))
        else:
            hooks = None

        if method == 'get':
            return self.parse_response(requests.get(self.get_url(path),
                                       auth=auth,
                                       params=params,
                                       headers=headers,
                                       hooks=hooks))
        elif method == 'post':
            return self.parse_response(requests.post(self.get_url(path),
                                       auth=auth,
                                       json=data,
                                       headers=headers,
                                       hooks=hooks))

    def request(self, method, path, params=None, data=None, callback=None):
        if callback is None:
            return self.make_request(method, path, params, data)
        else:
            return self.make_request(method, path, params, data, callback)
