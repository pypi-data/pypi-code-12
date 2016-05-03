import requests

import postageapp

from ostruct import OpenStruct

import json

from json import JSONEncoder

class RequestEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

class Request:
    def __init__(self, method = None):
        self._method = method or 'send_message'
        self._arguments = OpenStruct()

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, _method):
        self._method = _method

        return self._method

    @property
    def arguments(self):
        return self._arguments

    @arguments.setter
    def arguments(self, _arguments):
        self._arguments = _arguments
        return self._arguments

    def api_url(self):
        if (postageapp.config.port):
            return "%s://%s:%d/v.1.0/%s.json" % (
                postageapp.config.proto,
                postageapp.config.host,
                postageapp.config.port,
                self.method
            )
        else:
            return "%s://%s/v.1.0/%s.json" % (
                postageapp.config.proto,
                postageapp.config.host,
                self.method
            )

    def headers(self):
        return {
            'User-Agent': 'PostageApp Python %s (%s)' % (postageapp.__version__, postageapp.config.framework),
            'Content-Type': 'application/json'
        }

    def send(self):
        body = {
            'api_key': postageapp.config.api_key,
            'arguments': self._arguments
        }

        r = requests.post(self.api_url(), data=RequestEncoder().encode(body), headers=self.headers())
        return r.json()
