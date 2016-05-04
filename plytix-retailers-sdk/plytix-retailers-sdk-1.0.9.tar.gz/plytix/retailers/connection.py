from plytix.retailers import API_URL

import requests
from requests.auth import HTTPDigestAuth


class PlytixRetailersConnection(object):
    """ Stores the credentials to connect to the Plytix Retailers API
    """
    def __init__(self, api_key, api_pwd):
        """
        :param api_key: The API key.
        :param api_pwd: The API password
        :return: The credentials to connect to the Plytix Retailers API
        """
        self.api_key = api_key
        self.api_pwd = api_pwd

        self.initialized = True

    @property
    def key(self):
        """
        :return: The API key.
        """
        return self.api_key

    @property
    def pwd(self):
        """
        :return: The API password.
        """
        return self.api_pwd

    def _make_request(self, endpoint, method, **kwargs):
        """
        Execute a request to the API.
        :param endpoint: Request's endpoint.
        :param method: Request's method.
        :param kwargs: Additional fields to pass to the request like query_string, custom headers, etc.
        :return: The request's response from the API.
        """
        url = '{api_url}/{endpoint}'.format(api_url=API_URL, endpoint=endpoint)

        auth = HTTPDigestAuth(self.key, self.pwd)
        headers = {'Content-Type': 'application/json'}
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])

        if method == 'GET':
            r = requests.get(url, auth=auth, headers=headers, **kwargs)
        elif method == 'POST':
            r = requests.post(url, auth=auth, headers=headers, **kwargs)
        elif method == 'PUT':
            r = requests.put(url, auth=auth, headers=headers, **kwargs)
        else:
            raise NotImplementedError  # pragma: no cover

        r.raise_for_status()
        return BaseResponse(r)

    def get(self, endpoint, **kwargs):
        """ Make a GET request to the Plytix API.
        :param endpoint: Endpoint for the request.
        :return: BaseResponse object
        """
        return self._make_request(endpoint, 'GET', **kwargs)

    def post(self, endpoint, **kwargs):
        """ Make a POST request to the Plytix API.
        :param endpoint: Endpoint for the request.
        :return: BaseResponse object
        """
        return self._make_request(endpoint, 'POST', **kwargs)

    def put(self, endpoint, **kwargs):
        """ Make a PUT request to the Plytix API.
        :param endpoint: Endpoint for the request.
        :return: BaseResponse object
        """
        return self._make_request(endpoint, 'PUT', **kwargs)


class BaseResponse(object):
    """ Represents a response to a Plytix API request.
    """
    def __init__(self, response):
        self._response = response

    def json(self):
        """
        :return: The parsed JSON response.
        """
        return self._response.json()

    @property
    def content(self):
        """
        :return: The content of the response body.
        """
        return self._response.content

    @property
    def ok(self):
        """
        :return: Return True if the response was successful.
        """
        return self._response.ok

    @property
    def response(self):
        """
        :return: Return the network response.
        """
        return self._response

    @property
    def status_code(self):
        """
        :return: Return the HTTP status code of the response.
        """
        return self._response.status_code


