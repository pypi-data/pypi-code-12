# -*- coding: utf-8 -*-

import wx
import wx.py.shell


class pythonTextEntry(wx.py.shell.Shell):
    """wxTextCtrl override for execute python code"""
    def __init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString,
        pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.TE_MULTILINE |
            wx.TE_PROCESS_ENTER, validator=wx.DefaultValidator, name=wx.TextCtrlNameStr):
        """Initialize the control"""
        glb = globals()
        _l = {'__builtins__': glb['__builtins__'], '__name__': '__main__', '__doc__': None, '__package__': None}
        super(pythonTextEntry, self).__init__(parent, id, locals=_l)










