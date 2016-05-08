# encoding: utf-8

__author__ = u'Yonka'


class ConnectionBrokenException(RuntimeError):
    pass


class AuthFailedException(RuntimeError):
    pass


class RequestTimeoutException(RuntimeError):
    pass


class InvalidRequestRuntimeException(RuntimeError):
    pass
