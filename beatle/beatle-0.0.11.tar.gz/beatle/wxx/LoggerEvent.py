# -*- coding: utf-8 -*-
"""This module defines a custom event for dispatching messages to logger window"""

import wx


class LoggerEvent(wx.PyCommandEvent):
    """Custom event"""
    _type = wx.NewEventType()

    def __init__(self, message, level=wx.LOG_Info, id=wx.ID_ANY):
        """Initializer"""
        self._message = message
        self._level = level
        wx.PyCommandEvent.__init__(self, LoggerEvent._type, id)

    @property
    def level(self):
        """Returns the message level"""
        return self._level

    @property
    def message(self):
        """Returns the message"""
        return self._message

EVT_LOGGER = wx.PyEventBinder(LoggerEvent._type, 1)