#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Focus event - abstract class"""

__author__ = 'Bartosz Kościów'


class Focus(object):
    """event focus/blur"""
    def __init__(self):
        self.has_focus = False

    def event_focus(self):
        """called on focus gain"""
        raise NotImplementedError("event_focus not implemented")

    def event_blur(self):
        """called on focus lost"""
        raise NotImplementedError("event_blur not implemented")
