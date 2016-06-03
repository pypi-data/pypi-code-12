# -*- coding: utf-8 -*-
"""
affinitic.caching

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
import cPickle
import md5
import os
import pkg_resources

try:
    pkg_resources.get_distribution('sqlalchemy')
except pkg_resources.DistributionNotFound:

    class RowProxy(object):
        pass
else:  # we have sqlalchemy
    try:
        from sqlalchemy.engine.base import RowProxy
    except ImportError, e:
        from sqlalchemy.engine import RowProxy


from lovely.memcached.event import invalidateCache
from lovely.memcached.event import InvalidateCacheEvent
from lovely.memcached.interfaces import IMemcachedClient
from lovely.memcached.utility import MemcachedClient

from zope import component
from zope import event
from zope.component import queryUtility
from zope.ramcache.interfaces.ram import IRAMCache

from plone.memoize import volatile
from plone.memoize.interfaces import ICacheChooser
from plone.memoize.ram import (AbstractDict, store_in_cache, RAMCacheAdapter)

from affinitic.caching.interfaces import IMemcachedDefaultNameSpace


class MemcachedClientWithNameSpace(MemcachedClient):
    """
    Delegate the namespace definition to a utility
    Cache the namespace calculation
    """
    _defaultNS = None

    @property
    def defaultNS(self):
        if self._defaultNS is not None:
            return self._defaultNS
        defaultNameSpace = queryUtility(IMemcachedDefaultNameSpace)
        if defaultNameSpace is not None:
            defaultNameSpace = defaultNameSpace()
            if defaultNameSpace is not None:
                self._defaultNS = defaultNameSpace

    def _getNS(self, ns, raw):
        defaultNameSpace = self.defaultNS or 'defaultNS'
        if not ns and defaultNameSpace:
            if raw:
                ns = str(defaultNameSpace)
            else:
                ns = defaultNameSpace
        return ns or None


def memcachedClient():
    servers = os.environ.get("MEMCACHE_SERVER", "127.0.0.1:11211").split(",")
    defaultAge = int(os.environ.get("MEMCACHE_DEFAULT_AGE", '86400'))
    return MemcachedClientWithNameSpace(servers, defaultNS=None,
                                        defaultAge=defaultAge)


class MemcacheAdapter(AbstractDict):

    def __init__(self, client, globalkey=''):
        self.client = client

    def _make_key(self, source):
        key = str(MEMCACHED_KEY_PREFIX) + md5.new(source).hexdigest()
        return key

    def __getitem__(self, key):
        cached_value = self.client.query(self._make_key(key), raw=True)
        if cached_value is None:
            raise KeyError(key)
        else:
            return cPickle.loads(cached_value)

    def __setitem__(self, key, value):
        try:
            cached_value = cPickle.dumps(value)
        except TypeError:
            if isinstance(value, list) and isinstance(value[0], RowProxy):
                value = [RowProxyDict(d) for d in value]
            elif isinstance(value, RowProxy):
                value = RowProxyDict(value)
            else:
                raise
            cached_value = cPickle.dumps(value)
        self.client.set(cached_value, self._make_key(key), raw=True,
                        dependencies=[])

    def set(self, key, value, dependencies=[]):
        try:
            cached_value = cPickle.dumps(value)
        except TypeError:
            if isinstance(value, list) and isinstance(value[0], RowProxy):
                value = [RowProxyDict(d) for d in value]
            elif isinstance(value, RowProxy):
                value = RowProxyDict(value)
            else:
                raise
            cached_value = cPickle.dumps(value)
        self.client.set(cached_value, self._make_key(key), raw=True,
                        dependencies=dependencies)

    def setWithLifetime(self, key, value, lifetime, dependencies=[]):
        cached_value = cPickle.dumps(value)
        self.client.set(cached_value, self._make_key(key), raw=True,
                        lifetime=lifetime,
                        dependencies=dependencies)

IS_MEMCACHED_ACTIVE = True
MEMCACHED_KEY_PREFIX = 0


def get_memcached_usage():
    return IS_MEMCACHED_ACTIVE


def get_memcached_prefix():
    return MEMCACHED_KEY_PREFIX


def flush_memcached():
    global MEMCACHED_KEY_PREFIX
    MEMCACHED_KEY_PREFIX += 1


def set_memcached_usage(value):
    global IS_MEMCACHED_ACTIVE
    IS_MEMCACHED_ACTIVE = value
    if IS_MEMCACHED_ACTIVE:
        flush_memcached()


def activate_memcached_usage():
    set_memcached_usage(True)


def deactivate_memcached_usage():
    set_memcached_usage(False)


def toggle_memcached_usage():
    set_memcached_usage(not IS_MEMCACHED_ACTIVE)


def choose_cache(fun_name):
    client = queryUtility(IMemcachedClient)
    if client is not None:
        return MemcacheAdapter(client, globalkey=fun_name)
    else:
        return RAMCacheAdapter(queryUtility(IRAMCache),
                               globalkey=fun_name)


_marker = object()


def cache(get_key, dependencies=None, get_dependencies=None, lifetime=None):

    def decorator(fun):

        def replacement(*args, **kwargs):
            if not IS_MEMCACHED_ACTIVE:
                return fun(*args, **kwargs)
            try:
                key = get_key(fun, *args, **kwargs)
            except volatile.DontCache:
                return fun(*args, **kwargs)
            key = str(key)

            # Do not cache when not using memcache with dependencies
            memcache_client = queryUtility(IMemcachedClient)
            if (dependencies is not None or get_dependencies is not None) and not memcache_client:
                return fun(*args, **kwargs)

            if dependencies is not None or get_dependencies is not None:
                deps = dependencies
                if get_dependencies is not None:
                    deps = get_dependencies(fun, *args, **kwargs)
            cache = store_in_cache(fun, *args, **kwargs)
            cached_value = cache.get(key, _marker)
            if cached_value is _marker:
                if lifetime is None:
                    cached_value = fun(*args, **kwargs)
                    cache.set(key, cached_value, deps)
                else:
                    cached_value = fun(*args, **kwargs)
                    cache.setWithLifetime(key, cached_value, lifetime, deps)
            return cached_value
        return replacement
    return decorator


def invalidate_key(funcname, key):
    client = queryUtility(IMemcachedClient)
    cache = queryUtility(ICacheChooser)(key)
    if client is not None:
        invalidateEvent = InvalidateCacheEvent(key=cache._make_key(key),
                                               raw=True)
        event.notify(invalidateEvent)
    else:
        key = dict(key=cache._make_key(key))
        cache.ramcache.invalidate(funcname, key=key)


def invalidate_dependencies(dependencies):
    """
    Invalidate all caches linked to dependencies
    """
    client = queryUtility(IMemcachedClient)
    component.provideHandler(invalidateCache)
    # memcached
    if client is not None:
        invalidateEvent = InvalidateCacheEvent(raw=True,
                                               dependencies=dependencies)
        event.notify(invalidateEvent)
    # ramcache
    else:
        # Cannot invalidate dependencies with ramcache
        pass


class RowProxyDict(dict):
    """
    dict allowing to get values via __getattr__
    """

    def __getattr__(self, item):
        """Maps values to attributes.
        Only called if there *isn't* an attribute with this name
        """
        if self.has_key(item):
            return self.__getitem__(item)
        elif self.has_key(item.upper()):
            return self.__getitem__(item.upper())
        else:
            raise AttributeError(item)
