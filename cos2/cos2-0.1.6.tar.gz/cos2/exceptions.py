# -*- coding: utf-8 -*-

"""
cos2.exceptions
~~~~~~~~~~~~~~

异常类。
"""

import re

import json


from .compat import to_string


_COS_ERROR_TO_EXCEPTION = {} # populated at end of module


COS_CLIENT_ERROR_STATUS = -1
COS_REQUEST_ERROR_STATUS = -2


class CosError(Exception):
    def __init__(self, status, headers, body, details):
        #: HTTP 状态码
        self.status = status

        #: 请求ID，用于跟踪一个COS请求。提交工单时，最好能够提供请求ID
        self.request_id = headers.get('x-cos-request-id', '')

        #: HTTP响应体（部分）
        self.body = body

        #: 详细错误信息，是一个string到string的dict
        self.details = details

        #: COS错误码
        self.code = self.details.get('Code', '')

        #: COS错误信息
        self.message = self.details.get('Message', '')

    def __str__(self):
        return str(self.details)


class ClientError(CosError):
    def __init__(self, message):
        CosError.__init__(self, COS_CLIENT_ERROR_STATUS, {}, 'ClientError: ' + message, {})

    def __str__(self):
        return self.body


class RequestError(CosError):
    def __init__(self, e):
        CosError.__init__(self, COS_REQUEST_ERROR_STATUS, {}, 'RequestError: ' + str(e), {})
        self.exception = e

    def __str__(self):
        return self.body


class ServerError(CosError):
    pass


class NotFound(ServerError):
    status = 404
    code = ''


class MalformedXml(ServerError):
    status = 400
    code = 'MalformedXML'


class InvalidArgument(ServerError):
    status = 400
    code = 'InvalidArgument'

    def __init__(self, status, headers, body, details):
        super(InvalidArgument, self).__init__(status, headers, body, details)
        self.name = details.get('ArgumentName')
        self.value = details.get('ArgumentValue')


class InvalidObjectName(ServerError):
    status = 400
    code = 'InvalidObjectName'
class OperationZoneMismatch(ServerError):
    status = 400
    code = 'OperationZoneMismatch'

class NoSuchBucket(NotFound):
    status = 404
    code = 'NoSuchBucket'


class NoSuchKey(NotFound):
    status = 404
    code = 'NoSuchKey'


class NoSuchUpload(NotFound):
    status = 404
    code = 'NoSuchUpload'


class NoSuchWebsite(NotFound):
    status = 404
    code = 'NoSuchWebsiteConfiguration'

class Conflict(ServerError):
    status = 409
    code = ''


class BucketNotEmpty(Conflict):
    status = 409
    code = 'BucketNotEmpty'
class BucketAlreadyOwnedByYou(Conflict):
    status = 409
    code = 'BucketAlreadyOwnedByYou'


class NotModified(ServerError):
    status = 304
    code = ''


class AccessDenied(ServerError):
    status = 403
    code = 'AccessDenied'


def make_exception(resp):
    status = resp.status
    headers = resp.headers
    body = resp.read(4096)
    details = _parse_error_body(body)
    code = details.get('Code')
    if(code == None):
        code = ''

    try:
        klass = _COS_ERROR_TO_EXCEPTION[(status, code)]
        return klass(status, headers, body, details)
    except KeyError:
        return ServerError(status, headers, body, details)

def _parse_error_body(body):
    tmp_string =to_string(body)
    try:
        resp = json.loads(tmp_string)
        return resp
    except ValueError:
        return {}


def _walk_subclasses(klass):
    for sub in klass.__subclasses__():
        yield sub
        for subsub in _walk_subclasses(sub):
            yield subsub


for klass in _walk_subclasses(ServerError):
    status = getattr(klass, 'status', None)
    code = getattr(klass, 'code', None)

    if status is not None and code is not None:
        _COS_ERROR_TO_EXCEPTION[(status, code)] = klass