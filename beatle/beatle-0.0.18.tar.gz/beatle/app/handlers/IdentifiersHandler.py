# -*- coding: utf-8 -*-
import wx


"""Defines basic interface for app/editor"""


class IdentifiersHandler(object):
    """Application identifiers handler"""
    _identifiers = {}

    def __init__(self):
        """Ensures this is a singleton"""
        raise RuntimeError('IdentifiersHandler is a singleton')
        super(IdentifiersHandler, self).__init__()

    @classmethod
    def new(cls, name=None):
        """Create a new identifier"""
        if name:
            if name in cls._identifiers:
                raise RuntimeError('Identifier {name} already exists'.format(name=name))
            value = wx.Window.NewControlId()
            cls._identifiers[name] = value
            return value
        else:
            return wx.Window.NewControlId()

    @classmethod
    def register(cls, name):
        """Register a identifier"""
        value = cls._identifiers.get(name, None)
        if value is None:
            value = cls.new(name)
        return value
