#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Action event - abstract class"""

__author__ = 'Bartosz Kościów'


class Action(object):
    """event action"""
    def __init__(self):
        self._callback = None

    def event_action(self):
        """called on action"""
        raise NotImplementedError("event_action not implemented")

    @property
    def callback(self):
        """return callback"""
        return self._callback

    @callback.setter
    def callback(self, func):
        """set callback"""
        self._callback = func
