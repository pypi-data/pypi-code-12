#! /usr/bin/env python
# Copyright (C) 2016 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/
"""Utilities."""


def monkeypatch(cls, methodname=None):
    """patch a class with decorated method"""
    def decorator(func):
        """decorated"""
        name = methodname or func.__name__
        if not func.__doc__:
            func.__doc__ = getattr(cls, name).__doc__
        setattr(cls, name, func)
        return func
    return decorator
