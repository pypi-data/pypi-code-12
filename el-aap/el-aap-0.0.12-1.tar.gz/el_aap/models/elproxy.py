__author__ = 'schlitzer'

import logging

from bottle import request, response
import requests

from el_aap_api.errors import method_wrapper


class ElasticSearchProxy(object):
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.log = logging.getLogger('el_aap')

    @method_wrapper
    def _set_headers_and_status(self, r):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.debug("{0} setting response status {1}".format(request_id, r.status_code))
        response.status = r.status_code
        for header, value in r.headers.items():
            if header == 'Content-Length':
                continue
            self.log.debug("{0} setting response header {1}, with value {2}".format(request_id, header, value))
            response.set_header(header, value)

    @method_wrapper
    def delete(self):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.debug("{0} fetching answer from backend".format(request_id))
        r = requests.delete(
            allow_redirects=False,
            url=self.endpoint+request.path,
            params=request.query,
            headers=request.headers,
            data=request.body
        )
        self.log.debug("{0} successfully fetched answer from backend".format(request_id))
        self._set_headers_and_status(r)
        return r.content

    @method_wrapper
    def get(self):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.debug("{0} fetching answer from backend".format(request_id))
        r = requests.get(
            allow_redirects=False,
            url=self.endpoint+request.path,
            params=request.query,
            headers=request.headers,
            data=request.body
        )
        self.log.debug("{0} successfully fetched answer from backend".format(request_id))
        self._set_headers_and_status(r)
        return r.content

    @method_wrapper
    def post(self):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.debug("{0} fetching answer from backend".format(request_id))
        r = requests.post(
            allow_redirects=False,
            url=self.endpoint+request.path,
            params=request.query,
            headers=request.headers,
            data=request.body
        )
        self.log.debug("{0} successfully fetched answer from backend".format(request_id))
        self._set_headers_and_status(r)
        return r.content

    @method_wrapper
    def put(self):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.debug("{0} fetching answer from backend".format(request_id))
        r = requests.put(
            allow_redirects=False,
            url=self.endpoint+request.path,
            params=request.query,
            headers=request.headers,
            data=request.body
        )
        self.log.debug("{0} successfully fetched answer from backend".format(request_id))
        self._set_headers_and_status(r)
        return r.content
