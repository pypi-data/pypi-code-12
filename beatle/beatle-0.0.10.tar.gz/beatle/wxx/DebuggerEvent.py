# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""This module defines a custom event for dispatching messages to logger window"""

import wx

# Predefined event types
FILE_LINE_INFO = 1  # posted when the info line is returned
DEBUG_ENDED = 2     # posted when the debug session has end
UNKNOWN_DEBUG_INFO = 3  # posted when some remote message fails to get parsed
UPDATE_THREADS_INFO = 4  # posted when the threads info is available
UPDATE_LOCALS_INFO = 5  # posted when the locals info is available
UPDATE_BREAKPOINTS_INFO = 6  # posted when breakpoints info is available
USER_COMMAND_RESPONSE = 7  # posted while the reponse for an user command


class DebuggerEvent(wx.PyCommandEvent):
    """Custom event"""
    _type = wx.NewEventType()

    def __init__(self, wich, message=None, id=wx.ID_ANY):
        """Initializer"""
        self._wich = wich
        self._message = message
        wx.PyCommandEvent.__init__(self, DebuggerEvent._type, id)

    @property
    def wich(self):
        """Returns the message"""
        return self._wich

    @property
    def message(self):
        """Returns the message"""
        return self._message

EVT_DEBUGGER = wx.PyEventBinder(DebuggerEvent._type, 1)