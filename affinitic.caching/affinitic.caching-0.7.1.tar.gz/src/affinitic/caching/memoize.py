# encoding: utf-8
"""
memoize.py

Created by jfroche.
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

from zope import component

from plone.memoize import volatile
from plone.memoize.interfaces import ICacheChooser

from affinitic.caching.interfaces import IInvalidateKey


def cache_for_functions(func, lifetime=86400):
    """
    Use this to decorate statics methods or separate functions.
    You can define a lifetime duration for the value that are cached with the
    lifetime parameter (in second), by default it's 1 day.
    """

    def store_in_cache(func, *args, **kwargs):
        key = '%s.%s' % (func.__module__, func.__name__)
        cache_chooser = component.getUtility(ICacheChooser)
        cache = cache_chooser(key)
        if hasattr(cache, 'client'):
            cache.client.defaultAge = lifetime
        else:
            cache.ramcache.update(lifetime)
        return cache

    def get_key(func, *args, **kwargs):
        items = []
        for item in kwargs.items():
            elements = []
            for i in item:
                if isinstance(i, list):
                    i = tuple(i)
                elements.append(i)
            items.append(tuple(elements))
        return (args, frozenset(items), )

    def cache(get_key):
        return volatile.cache(get_key, get_cache=store_in_cache)

    return cache(get_key)(func)


def cache_for_instances(func, lifetime=86400):
    """
    Use this to decorate class instances methods only.
    You can define a lifetime duration for the value that are cached with the
    lifetime parameter (in second), by default it's 1 day.
    """

    def store_in_cache(func, *args, **kwargs):
        key = '%s.%s' % (func.__module__, func.__name__)
        cache_chooser = component.getUtility(ICacheChooser)
        cache = cache_chooser(key)
        if hasattr(cache, 'client'):
            cache.client.defaultAge = lifetime
        else:
            cache.ramcache.update(lifetime)
        return cache

    def get_key(func, *args, **kwargs):
        items = []
        for item in kwargs.items():
            elements = []
            for i in item:
                if isinstance(i, list):
                    i = tuple(i)
                elements.append(i)
            items.append(tuple(elements))
        # remove 'self' attribute received from instance method
        return (args[1:], frozenset(items), )

    def cache(get_key):
        return volatile.cache(get_key, get_cache=store_in_cache)

    return cache(get_key)(func)


def clear_after(funcname, args=(), kwargs={}):
    """
    Use this to decorate class methods or functions.
    This decorator invalidates the given function in the cache depending of
    his arguments after the decorate function was executed
    See clear_cache docs for details on parameters.
    """

    def get_key(arg, kwargs):
        return (arg, frozenset(kwargs.items()), )

    def clear(func):

        def wrapped_clear(*args, **kwargs):
            func(*args, **kwargs)
            component.queryUtility(IInvalidateKey)(funcname, key)
        return wrapped_clear
    key = '%s:%s' % (funcname, get_key(args, kwargs))
    return clear


def clear_before(funcname, args=(), kwargs={}):
    """
    Use this to decorate class methods or functions.
    This decorator invalidates the given function in the cache depending of
    his arguments before the decorate function was executed
    See clear_cache docs for details on parameters.
    """

    def get_key(arg, kwargs):
        return (arg, frozenset(kwargs.items()), )

    def clear(func):

        def wrapped_clear(*args, **kwargs):
            component.queryUtility(IInvalidateKey)(funcname, key)
            func(*args, **kwargs)
        return wrapped_clear
    key = '%s:%s' % (funcname, get_key(args, kwargs))
    return clear


def clear_cache(funcname, args=(), kwargs={}):
    """
    Use this function to invalidate a specific function or methods depending
    of his arguments in the cache
    Parameters : - funcname : a string with the complete path and the function
                              name. ex: 'arsia.cerise.core.memoize.clear_cache'
                 - args : a tuple with the arguments passed to the function.
                          ex: ('param1', )
                 - kwargs : a dictionary with the keyword arguments passed
                            to the function. ex: {'key1': value}
    """

    def get_key(arg, kwargs):
        return (arg, frozenset(kwargs.items()), )

    key = '%s:%s' % (funcname, get_key(args, kwargs))
    component.queryUtility(IInvalidateKey)(funcname, key)


def invalidate_key(funcname, key):
    cache = component.queryUtility(ICacheChooser)(key)
    cache.ramcache.invalidate(funcname, key=dict(key=cache._make_key(key)))


def one_day_memoize_for_instances(func):
    """
    Use this to decorate class instances methods only
    Cached return values are cleared every day
    """
    return cache_for_instances(func, lifetime=86400)


def one_day_memoize_for_functions(func):
    """
    Use this to decorate statics methods or separate functions.
    Cached return values are cleared every day.
    """
    return cache_for_functions(func, lifetime=86400)


def one_hour_memoize_for_instances(func):
    """
    Use this to decorate class instances methods only
    Cached return values are cleared every hour
    """
    return cache_for_instances(func, lifetime=3600)


def one_hour_memoize_for_functions(func):
    """
    Use this to decorate statics methods or separate functions.
    Cached return values are cleared every hour
    """
    return cache_for_functions(func, lifetime=3600)
