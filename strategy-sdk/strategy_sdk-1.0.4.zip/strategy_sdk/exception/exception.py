# encoding: utf-8

__author__ = 'Yonka'


class ConnectionBrokenException(RuntimeError):
    pass


class AuthFailedException(RuntimeError):
    pass


class RequestTimeoutException(RuntimeError):
    pass


class InvalidRequestRuntimeException(RuntimeError):
    pass
