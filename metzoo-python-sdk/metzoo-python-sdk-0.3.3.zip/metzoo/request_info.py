# -*- coding: utf-8 -*-

class RequestInfo(object):
    """Used to send requests"""

    def __init__(self, method, route):
        self._method = method
        self._route = route

    @property
    def method(self):
        return self._method

    @property
    def route(self):
        return self._route
