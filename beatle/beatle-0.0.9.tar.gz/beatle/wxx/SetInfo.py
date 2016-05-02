# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

import wx.lib.agw.supertooltip as ttip


class SetInfo(object):
    """Class decorator for setting tooltip info into dialog"""
    def __init__(self, text, about="what's this?"):
        """"""
        self._text = text
        self._about = about

    def __call__(self, method):
        """"""
        def wrapped_call(*args, **kwargs):
            """Code dialog creation"""
            method(*args, **kwargs)
            this = args[0]
            tip = ttip.SuperToolTip(self._text)
            tip.SetHeader(self._about)
            tip.SetTarget(this.m_info)
            tip.SetDrawHeaderLine(True)
            tip.ApplyStyle("Office 2007 Blue")
            tip.SetDropShadow(True)
        return wrapped_call