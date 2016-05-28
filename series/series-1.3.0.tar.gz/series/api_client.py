import requests

from flask import json

from tek.config import configurable
from tek import logger

from series.client.errors import SeriesClientException


def command_decorator():
    doc = {}

    def command(args, description):
        def decor(func):
            doc[func.__name__] = args, description
            return func
        return decor
    return doc, command


class ApiClient(object):

    doc, command = command_decorator()

    def __init__(self, info_output=True):
        self._info_output = info_output

    def _url(self, path):
        return '{}:{}/{}'.format(self._rest_api_url, self._rest_api_port, path)

    def _request(self, req_type, path, body):
        headers = {'content-type': 'application/json'}
        requester = getattr(requests, req_type)
        try:
            response = requester(self._url(path), data=json.dumps(body),
                                 headers=headers)
        except requests.RequestException as e:
            msg = 'Request failed! ({})'.format(e)
            raise SeriesClientException(msg) from e
        else:
            if response.status_code >= 400:
                logger.error(
                    'API response status {}'.format(response.status_code))
            try:
                _json = response.json()
            except ValueError as e:
                msg = 'Error in API request (no JSON in response)!'
                raise SeriesClientException(msg) from e
            else:
                data = _json.get('response', {})
                if isinstance(data, dict) and 'error' in data:
                    logger.error(data['error'])
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
            logger.info(msg)

    @command('', 'Display this help text')
    def help(self):
        if self.doc:
            maxlen = len(max(self.doc.keys(), key=len))
            pad = lambda s: s.ljust(maxlen)
            logger.info('Available seriesd commands:')
            for name, (args, description) in self.doc.items():
                logger.info('')
                logger.info('{}    {}'.format(pad(name), args))
                logger.info('  {}'.format(description))

__all__ = ['ApiClient']
