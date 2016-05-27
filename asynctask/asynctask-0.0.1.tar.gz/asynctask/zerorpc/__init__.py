#!/usr/bin/env python
# coding=utf-8

import json

serializer = json.dumps
deserializer = json.loads

class Error(Exception):
    def __init__(self, error_type, message='', tb=None):
        self.error_type = error_type
        self.message = message
        self.traceback = tb
    def __repr__(self):
        return "%s('%s')" % (self.error_type, self.message)
    __str__ = __repr__
