"""
Falkonry Client

Client to access Condition Prediction APIs

:copyright: (c) 2016 by Falkonry Inc.
:license: MIT, see LICENSE for more details.

"""

import json
import base64
import requests
from falkonryclient.helper import utils as Utils
from cStringIO import StringIO

"""
HttpService:
    Service to make API requests to Falkonry Service
"""


class HttpService:

    def __init__(self, host, token):
        """
        constructor
        :param host: host address of Falkonry service
        :param token: Authorization token
        """
        self.host  = host if host is not None else "https://service.falkonry.io"
        self.token = base64.b64encode(token) if token is not None else ""

    def get(self, url):
        """
        To make a GET request to Falkonry API server
        :param url: string
        """

        response = requests.get(
            self.host + url,
            headers={
                'Authorization': 'Token ' + self.token
            }
        )
        if response.status_code is 200:
            return json.loads(response.content)
        else:
            raise Exception(response.content)

    def post(self, url, entity):
        """
        To make a POST request to Falkonry API server
        :param url: string
        :param entity: Instantiated class object
        """

        response = requests.post(
            self.host + url,
            entity.to_json(),
            headers={
                "Content-Type": "application/json",
                'Authorization': 'Token ' + self.token
            }
        )
        if response.status_code is 201:
            return json.loads(response.content)
        else:
            raise Exception(response.content)

    def put(self, url, entity):
        """
        To make a PUT request to Falkonry API server
        :param url: string
        :param entity: Instantiated class object
        """

        response = requests.put(
            self.host + url,
            entity.to_json(),
            headers={
                "Content-Type": "application/json",
                'Authorization': 'Token ' + self.token
            }
        )
        if response.status_code is 200:
            return json.loads(response.content)
        else:
            raise Exception(response.content)

    def fpost(self, url, form_data):
        """
        To make a form-data POST request to Falkonry API server
        :param url: string
        :param form_data: form-data
        """
        response = None

        if 'files' in form_data:
            response = requests.post(
                self.host + url,
                data=form_data['data'] if 'data' in form_data else {},
                files=form_data['files'] if 'files' in form_data else {},
                headers={
                    'Authorization': 'Token ' + self.token
                }
            )
        else:
            response = requests.post(
                self.host + url,
                data=json.dumps(form_data['data'] if 'data' in form_data else {}),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'Token ' + self.token
                }
            )
        if response.status_code is 201 or response.status_code is 202:
            return json.loads(response.content)
        else:
            raise Exception(response.content)

    def delete(self, url):
        """
        To make a DELETE request to Falkonry API server
        :param url: string
        """
        response = requests.delete(
            self.host + url,
            headers={
              'Authorization': 'Token ' + self.token
            }
        )
        if response.status_code is 200:
            return json.loads(response.content)
        else:
            raise Exception(response.content)

    def upstream(self, url, form_data):
        """
        To make a form-data POST request to Falkonry API server using stream
        :param url: string
        :param form_data: form-data
        """
        response = requests.post(
            self.host + url,
            files=form_data['files'] if 'files' in form_data else {},
            headers={
                'Authorization': 'Token ' + self.token
            }
        )
        if response.status_code is 202:
            return json.loads(response.content)
        else:
            raise Exception(response.content)

    def downstream(self, url):
        """
        To make a GET request to Falkonry API server and return stream
        :param url: string
        """
        response = requests.get(
            self.host + url,
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/x-json-stream',
                'Authorization': 'Token ' + self.token
            },
            stream=True
        )
        if response.status_code is 200:
            return response.iter_lines()
        else:
            raise Exception(response.content)
