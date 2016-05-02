# -*- coding: utf-8 -*-


def with_name(function):
    """method decorator that provides self name access"""
    def wrap(self, *args, **kwargs):
        """wrapped calls"""
        self.__fname__ = function.__name__
        return function(self, *args, **kwargs)
    return wrap


def safe_super(_class, _inst):
    """safe super call that resolves for the same method
    even with multiple inheritance"""
    try:
        return getattr(super(_class, _inst), _inst.__fname__)
    except:
        return lambda *x, **kx: ()





