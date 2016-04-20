'''
Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.
'''
import functools
import json
import sys
import time

import requests

from sxclient import exceptions

from sxclient.query.utils import job_poll_params
from sxclient.tools import generate_poll_times


HTTP_STATUS_TO_EXCEPTIONS_MAP = {
    400: exceptions.SXClusterBadRequest,
    401: exceptions.SXClusterUnauthorized,
    403: exceptions.SXClusterForbidden,
    404: exceptions.SXClusterNotFound,
    408: exceptions.SXClusterRequestTimeout,
    410: exceptions.SXClusterNodeNotAMember,
    413: exceptions.SXClusterPayloadTooLarge,
    429: exceptions.SXClusterTooManyRequests,
}


class BaseQueryHandler(object):
    '''
    Prepare and send a query to an SX cluster.

    Initialization parameters (set as the attributes):
      - node_address -- address of the cluster's node to connect to
      - cluster -- Cluster data structure containing cluster's location
        data
      - session -- requests.Session-derived object used to send the
        requests

    Other attributes:
      - url -- actual URL used to connect to the node
      - cluster_uuid -- UUID of the cluster
      - timeout -- timeout set for requests being made
      - query -- latest sent query
      - response -- latest received response
      - poll_time_gen -- poll time generator; if replaced, should
        accept two arguments, start and end, and indefinitely yield the
        values from the interval bounded by start and end.

    This a base class that does not implement body serialization. Subclasses
    you can use are: JSONBodyQueryHandler, BinaryBodyQueryHandler.
    '''
    def __init__(self, node_address, cluster, session):
        self.node_address = node_address
        self.cluster = cluster
        self.session = session
        self.timeout = session.request_timeout
        self.query = None
        self.response = None
        self.poll_time_gen = functools.partial(generate_poll_times, steps=10)

    @property
    def url(self):
        return self.cluster.get_host_url(self.node_address)

    def prepare_query(self, query_params, body=None):
        query = self._create_query(query_params, body)
        query.node_address = self.node_address
        self.query = query

    def make_query(self):
        if self.query.is_complex:
            self._make_complex_query()
        else:
            self._make_simple_query()

    def _make_simple_query(self):
        self.response = self._send_request(
            self.query, self.session, self.timeout)

    def _make_complex_query(self):
        resp = self._send_request(self.query, self.session, self.timeout)
        resp_body = resp.json()
        req_id = resp_body[u'requestId']
        min_time = resp_body[u'minPollInterval'] / 1000.0
        max_time = resp_body[u'maxPollInterval'] / 1000.0

        for period in self.poll_time_gen(min_time, max_time):
            time.sleep(period)
            resp = self._make_poll_query(req_id, timeout=self.timeout)
            self.response = resp
            resp_body = resp.json()
            status = resp_body[u'requestStatus']

            if status == u'PENDING':
                continue
            elif status == u'OK':
                break
            elif status == u'ERROR':
                resp_msg = resp_body[u'requestMessage']
                raise exceptions.SXClusterNonFatalError(resp_msg)
            else:
                raise exceptions.SXClusterNonFatalError(
                    'Invalid poll response status'
                )

    def _serialize_request_body(self, body):
        raise NotImplementedError

    def _create_query(self, query_params, body=None):

        verb = query_params.verb
        is_complex = query_params.is_complex
        path = query_params.path
        params = query_params.params

        url = '/'.join([self.url, path])
        body_str = self._serialize_request_body(body)
        query = requests.Request(verb, url, params=params, data=body_str)
        query = self.session.prepare_request(query)
        query.is_complex = is_complex
        query.node_address = self.node_address
        return query

    def _make_poll_query(self, req_id, timeout=None):
        poll_query = self._create_query(job_poll_params(req_id))
        resp = self._send_request(poll_query,
                                  self.session,
                                  timeout=timeout)
        return resp

    @classmethod
    def _handle_http_error(cls, resp):
        err_val, err_tb = sys.exc_info()[1:]
        try:
            resp_msg = resp.json()[u'ErrorMessage']
        except ValueError:
            resp_msg = ''

        exc = HTTP_STATUS_TO_EXCEPTIONS_MAP.get(resp.status_code)
        if exc is None:
            if 400 <= resp.status_code < 500:
                exc = exceptions.SXClusterClientError
            elif resp.status_code >= 500:
                exc = exceptions.SXClusterInternalError

        raise exc, str(err_val) + ' ' + resp_msg, err_tb

    @classmethod
    def validate_response(cls, resp):
        pass

    @classmethod
    def _send_request(cls, req, session, timeout=None):
        '''
        Send 'requests.PreparedRequests', using session provided in the
        argument and raise error in case of failure.
        '''
        try:
            resp = session.send(req, timeout=timeout)
        except (requests.ConnectionError, requests.Timeout):
            err_val, err_tb = sys.exc_info()[1:]
            raise exceptions.SXClusterNonFatalError, str(err_val), err_tb

        resp.node_address = req.node_address

        # Check whether the response status is valid.
        try:
            resp.raise_for_status()
        except requests.HTTPError:
            cls._handle_http_error(resp)

        cls.validate_response(resp)

        # Check whether the response contains 'SX-Cluster' header.
        if 'sx-cluster' not in resp.headers:
            msg = "No 'SX-Cluster' header in the response"
            raise exceptions.SXClusterNonFatalError(msg)

        return resp


class JSONBodyQueryHandler(BaseQueryHandler):
    def _serialize_request_body(self, body):
        return json.dumps(body, encoding='utf-8') if body else ''

    @classmethod
    def validate_response(cls, resp):
        # Check whether the response content is parseable into JSON.
        try:
            info = resp.json()
        except ValueError:
            err_val, err_tb = sys.exc_info()[1:]
            new_msg = ': '.join(['Cannot parse JSON', str(err_val)])
            raise exceptions.SXClusterNonFatalError, new_msg, err_tb

        # Check whether there is an error message in parsed response content.
        if u'ErrorMessage' in info:
            raise exceptions.SXClusterNonFatalError(info[u'ErrorMessage'])


class BinaryBodyQueryHandler(BaseQueryHandler):
    def _serialize_request_body(self, body):
        return body
