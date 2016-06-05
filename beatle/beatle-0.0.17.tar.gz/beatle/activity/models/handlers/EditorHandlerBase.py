# -*- coding: utf-8 -*-
import wx
from wx.stc import *
from  ctx import theContext as context


"""Defines basic interface for app/editor"""


class EditorHandlerBase(object):
    """Interface for editor handlers"""

    cookie_lexers = {
        'text': STC_LEX_NULL,
        'c++': STC_LEX_CPP,
        'python': STC_LEX_PYTHON,
        'sql': STC_LEX_SQL,
        'bash': STC_LEX_BASH,
        'css': STC_LEX_CSS,
        'html': STC_LEX_HTML,
        'mathlab': STC_LEX_MATLAB,
        'octave': STC_LEX_OCTAVE,
        'xml': STC_LEX_XML,
        'apache': STC_LEX_CONF,
        'make': STC_LEX_MAKEFILE,
        'nasm': STC_LEX_ASM,
        'vhdl': STC_LEX_VHDL
    }

    keyword_list = []
    keyword_list2 = []
    style_items = []
    style = {}

    def __init__(self, **kwargs):
        """Initialize handler"""
        self.lexer = kwargs.get('lexer', 'text')
        self.font = kwargs.get('font', 'config/defaultFont')
        self.text = kwargs.get('text', '')
        if 'keywords' in kwargs:
            self.keyword_list = kwargs['keywords']
        if 'keywords2' in kwargs:
            self.keyword_list2 = kwargs['keywords2']
        self.read_only = kwargs.get('read_only', False)
        super(EditorHandlerBase, self).__init__()

    @property
    def lexer(self):
        """get property"""
        return self._lexer

    @lexer.setter
    def lexer(self, value):
        """set property"""
        if value in self.cookie_lexers:
            self._lexer = self.cookie_lexers[value]
        else:
            self._lexer = value

    @property
    def font(self):
        """return the font"""
        return self._font

    @font.setter
    def font(self, font_section):
        """set the font by config section. fallback to default"""
        self._font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font_info = self._font.GetNativeFontInfo().ToString()
        font_info = context.config.Read(font_section, font_info)
        self._font.SetNativeFontInfoFromString(font_info)

    @property
    def keywords(self):
        """return keywords"""
        return ' '.join(self.keyword_list)

    @property
    def keywords2(self):
        """return keywords"""
        return ' '.join(self.keyword_list2)

    def SetupMargins(self, editor):
        """Setup margins"""
        pass

    def SetupMarkers(self, editor):
        """Setup markers"""
        pass

    def SetProperties(self, editor):
        """Set other properties"""
        pass

    def SetupEvents(self, editor):
        """Set event handling"""
        pass

    def init_fonts(self, editor):
        """default font initialization"""
        font = self.font
        for i in range(0, 39):
            editor.StyleSetFont(i, font)

    def InitStyles(self, editor):
        """Initialize the styles"""
        for item in self.style_items:
            id, name = item
            if name in self.style:
                editor.StyleSetSpec(id, self.style[name])

    def InitKeywords(self, editor):
        """Initialize keywords"""
        editor.SetKeyWords(0, self.keywords)
        editor.SetKeyWords(1, self.keywords2)

    def SetupAuto(self, editor):
        """Setup autosuggested"""
        s = self.keyword_list + self.keyword_list2
        s.sort()
        editor._auto = ' '.join(s)

    def Initialize(self, editor):
        """Initialize editor"""
        #if self.keywords:
        #    editor.SetKeyWords(0, self.keywords)
        editor.SetText(self.text)
        editor.EmptyUndoBuffer()
        editor.SetSavePoint()
        editor.SetUndoCollection(True)
        self.InitStyles(editor)
        self.InitKeywords(editor)
        self.SetupAuto(editor)
        editor.SetReadOnly(self.read_only)

