from datetime import datetime, timedelta
import logging

from tornado import escape, gen, httpclient
from urllib import parse
import validators


class ApiClient:
    def __init__(self):
        self._http = httpclient.AsyncHTTPClient()

    @gen.coroutine
    def async_request(self, url, parameters=None, http_method='GET', body=None, headers=None):
        url = self.encode_url(url, parameters)
        default_header = {'Content-Type': 'application/json'}
        headers = self.append_headers(header_to_append=default_header, base_headers=headers)

        if body:
            body = self._validate_body(body)
        if not self._is_method_valid(http_method):
            raise ValueError('Unsupported method: {method}'.format(method=http_method))
        if not self._is_headers_type_valid(headers):
            raise TypeError('Invalid headers type')

        try:
            logging.debug('Requesting: {url}'.format(url=url))
            response = yield self._http.fetch(httpclient.HTTPRequest(url, http_method, headers, body=body))
            logging.debug('Success: {url}'.format(url=url))
            if response.body:
                return escape.json_decode(response.body)
        except httpclient.HTTPError as e:
            e.message = 'Unable to complete {url}: {message}'.format(url=url, message=e.message)
            raise e

    def _is_method_valid(self, http_method):
        supported_methods = ['GET', 'POST', 'DELETE', 'PUT', 'PATCH']
        return http_method in supported_methods

    @staticmethod
    def encode_url(url, parameters=None):
        if parameters:
            if not isinstance(parameters, dict):
                raise TypeError('Parameters must be instance of dict.')
            url += parse.urlencode(parameters)
        if not validators.url(url):
            raise ValueError('Invalid url format: {url}'.format(url=url))
        return url

    def _is_json_valid(self, json):
        is_valid = True
        try:
            escape.json_decode(json)
        except ValueError:
            is_valid = False
        return is_valid

    def _validate_body(self, body):
        if isinstance(body, dict):
            body = escape.json_encode(body)
        elif not self._is_json_valid(body):
            raise ValueError('Invalid json format')
        return body

    def _is_headers_type_valid(self, headers):
        return bool(isinstance(headers, dict))

    def append_headers(self, header_to_append: dict, base_headers=None):
        if base_headers is None:
            base_headers = dict()
        else:
            if not isinstance(base_headers, dict):
                raise TypeError(
                    'Invalid type in function append_headers, expected {expected}, {given} given.'.format(
                        expected=dict.__name__,
                        given=type(base_headers)))
        z = base_headers.copy()
        z.update(header_to_append)
        return z


class OAuthApiClient(ApiClient):
    def __init__(self,
                 oauth_authorization_url,
                 oauth_client_id,
                 oauth_client_secret,
                 oauth_grant_type,
                 username=None,
                 password=None,
                 renew_token_before_seconds=None,
                 non_expiring_token=None):
        super().__init__()
        self._access_token = None
        self._token_expires_at = None
        self._oauth_authorization_url = oauth_authorization_url
        self._oauth_client_id = oauth_client_id
        self._oauth_client_secret = oauth_client_secret
        self._oauth_grant_type = oauth_grant_type
        self._username = username
        self._password = password
        self._renew_token_before_seconds = renew_token_before_seconds
        self._non_expiring_token = non_expiring_token

    @gen.coroutine
    def oauth_async_request(self, url, parameters=None, http_method='GET', body=None, headers=None):
        access_token = yield self._get_access_token()
        auth_header = {'Authorization': 'Bearer {access_token}'.format(access_token=access_token)}
        headers = self.append_headers(header_to_append=auth_header, base_headers=headers)
        response = yield self.async_request(url=url, parameters=parameters, http_method=http_method, body=body, headers=headers)
        return response

    @gen.coroutine
    def _get_access_token(self):
        if self._renew_token_before_seconds is None:
            self._renew_token_before_seconds = 300

        if self._non_expiring_token is not None:
            return self._non_expiring_token

        if self._access_token is None:
            yield self._oauth_authorization_request(self._oauth_grant_type)
        elif (self._token_expires_at - datetime.now()).total_seconds() < int(self._renew_token_before_seconds):
            if 'refresh_token' in self._get_supported_grant_types():
                yield self._oauth_authorization_request('refresh_token')
            else:
                yield self._oauth_authorization_request(self._oauth_grant_type)
        return str(self._access_token)

    def _set_access_token(self, access_token):
        self._access_token = access_token

    def _set_access_token_expires_at(self, expires_in: int):
        self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)

    @gen.coroutine
    def _oauth_authorization_request(self, grant_type, method='POST'):
        url = self._oauth_authorization_url
        payload = self._get_payload(grant_type)
        response = yield self.async_request(url, method, payload)
        self._set_access_token(response.get('access_token'))
        self._set_access_token_expires_at(int(response.get('expires_in')))

    def _get_payload(self, grant_type):
        if not self._is_grant_type_valid(grant_type):
            raise ValueError('Unsupported grant type: {grant_type}'.format(grant_type=grant_type))
        payload = {'client_id': self._oauth_client_id, 'client_secret': self._oauth_client_secret}
        if grant_type == 'password':
            payload.update({'username': self._username, 'password': self._password})
        elif grant_type == 'refresh_token':
            current_access_token = self._access_token
            if not current_access_token:
                raise ValueError('Cannot refresh empty token: {current_access_token}.'.format(
                    current_access_token=current_access_token))
            payload.update({'refresh_token': current_access_token})
        payload.update({'grant_type': grant_type})
        return payload

    @staticmethod
    def _get_supported_grant_types():
        return ['password', 'client_credentials']

    def _is_grant_type_valid(self, grant_type):
        is_valid = False
        supported_grant_types = self._get_supported_grant_types()
        if not isinstance(supported_grant_types, list):
            raise TypeError(
                'Function {function} must return list.'.format(function=self._get_supported_grant_types.__name__))
        if grant_type in supported_grant_types:
            is_valid = True
        return is_valid
