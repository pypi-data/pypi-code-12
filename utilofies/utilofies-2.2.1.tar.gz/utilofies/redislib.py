# -*- encoding: utf-8 -*-
from __future__ import unicode_literals, division, \
                       absolute_import, print_function
from .stdlib import Timeout


class DataStructure(object):
    """Very optimistic wrapper for Redis data structures."""

    def __init__(self, redis, key, timeout=None):
        self.redis = redis
        self.key = key
        self.timeout = timeout

    def __getattr__(self, funcname):
        def func(*args, **kwargs):
            with Timeout(self.timeout or 0):
                return getattr(self.redis, funcname)(
                    self.key, *args, **kwargs)
        return func


class DataStructureCategory(object):

    def __init__(self, redis, prefix, timeout=None):
        self.redis = redis
        self.prefix = prefix
        self.timeout = timeout

    def __getitem__(self, key):
        return DataStructure(self.redis,
                             ':'.join((self.prefix, key)),
                             timeout=self.timeout)


class RedisWrapper(object):

    def __init__(self, redis, prefix, timeout=None):
        self.redis = redis
        self.prefix = prefix
        self.timeout = timeout

    def __getattr__(self, catname):
        return DataStructureCategory(self.redis,
                                     ':'.join((self.prefix, catname)),
                                     timeout=self.timeout)

    def __getitem__(self, key):
        return DataStructure(self.redis,
                             ':'.join((self.prefix, key)),
                             timeout=self.timeout)

