# -*- coding: utf-8 -*-
"""This module defines a custom event for dispatching messages to logger window"""

import wx


class SearchEvent(wx.PyCommandEvent):
    """Custom event"""
    _type = wx.NewEventType()

    def __init__(self, line, fname, id=wx.ID_ANY):
        """Initializer"""
        self._line = line
        self._fname = fname
        wx.PyCommandEvent.__init__(self, SearchEvent._type, id)

    @property
    def line(self):
        """Returns the line"""
        return self._line

    @property
    def fname(self):
        """Returns the file"""
        return self._fname

EVT_SEARCH = wx.PyEventBinder(SearchEvent._type, 1)