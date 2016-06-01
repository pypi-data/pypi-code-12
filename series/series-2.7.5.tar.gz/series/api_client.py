import requests

from flask import json

from series.logging import Logging

from series.client.errors import SeriesClientException


def command_decorator():
    doc = {}

    def command(args, description):
        def decor(func):
            doc[func.__name__] = args, description
            return func
        return decor
    return doc, command


class ApiClient(Logging):

    doc, command = command_decorator()

    def __init__(self, info_output=True):
        self._info_output = info_output

    def _url(self, path):
        return '{}:{}/{}'.format(self._rest_api_url, self._rest_api_port, path)

    def _request(self, req_type, path, body):
        headers = {'content-type': 'application/json'}
        requester = getattr(requests, req_type)
        url = self._url(path)
        self.log.debug('api request: {}'.format(url))
        try:
            response = requester(url, data=json.dumps(body), headers=headers)
        except requests.RequestException as e:
            msg = 'Request failed! ({})'.format(e)
            raise SeriesClientException(msg) from e
        else:
            if response.status_code >= 400:
                self.log.error(
                    'API response status {}'.format(response.status_code))
            try:
                _json = response.json()
            except ValueError as e:
                msg = 'Error in API request (no JSON in response)!'
                raise SeriesClientException(msg) from e
            else:
                data = _json.get('response', {})
                if isinstance(data, dict) and 'error' in data:
                    self.log.error(data['error'])
                return data

    def get(self, path, body={}):
        return self._request('get', path, body)

    def post(self, path, body={}):
        return self._request('post', path, body)

    def put(self, path, body={}):
        return self._request('put', path, body)

    def delete(self, path, body={}):
        return self._request('delete', path, body)

    def _info(self, msg):
        if self._info_output:
            self.log.info(msg)

    @command('', 'Display this help text')
    def help(self):
        if self.doc:
            maxlen = len(max(self.doc.keys(), key=len))
            pad = lambda s: s.ljust(maxlen)
            self.log.info('Available seriesd commands:')
            for name, (args, description) in self.doc.items():
                self.log.info('')
                self.log.info('{}    {}'.format(pad(name), args))
                self.log.info('  {}'.format(description))

__all__ = ['ApiClient']
