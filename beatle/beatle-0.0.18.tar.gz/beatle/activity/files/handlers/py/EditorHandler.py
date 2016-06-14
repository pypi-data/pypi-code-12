# -*- coding: utf-8 -*-
import wx
from wx.stc import *
from app.handlers import EditorHandlerBase
import app.resources as rc

MARGIN_LINE_NUMBERS = 0
MARK_MARGIN = 1
MARGIN_FOLD = 2

STC_MASK_MARKERS = ~STC_MASK_FOLDERS

MARK_BOOKMARK = 0
MARK_BREAKPOINT = 1
DEBUG_CURRENT = 32

#missing indicators
STC_INDIC_FULLBOX = 16

#undefined wrappers
SCI_ANNOTATIONSETTEXT = 2540
SCI_ANNOTATIONGETTEXT = 2541
SCI_ANNOTATIONSETSTYLE = 2542
SCI_ANNOTATIONGETSTYLE = 2543
SCI_ANNOTATIONSETSTYLES = 2544
SCI_ANNOTATIONGETSTYLES = 2545
SCI_ANNOTATIONGETLINES = 2546
SCI_ANNOTATIONCLEARALL = 2547
ANNOTATION_HIDDEN = 0
ANNOTATION_STANDARD = 1
ANNOTATION_BOXED = 2
SCI_ANNOTATIONSETVISIBLE = 2548
SCI_ANNOTATIONGETVISIBLE = 2549
SCI_ANNOTATIONSETSTYLEOFFSET = 2550
SCI_ANNOTATIONGETSTYLEOFFSET = 2551

SCI_STYLESETCHANGEABLE = 2099
STC_FIND_MATCHCASE = 4
STC_FIND_POSIX = 4194304
STC_FIND_REGEXP = 2097152
STC_FIND_WHOLEWORD = 2
STC_FIND_WORDSTART = 1048576


BOOKMARK_TOGGLE  = 30000
BOOKMARK_UP      = 30001
BOOKMARK_DOWN    = 30002
BREAKPOINT_TOGGLE= 30003
FIND = 30004
FIND_NEXT = 30005
FIND_PREV = 30006

import keyword


class EditorHandler(EditorHandlerBase):
    """Declares SQL editor handler"""

    keyword_list = keyword.kwlist
    keyword_list2 = ['self', 'None', 'True', 'False','arg', 'kwarg', 'super']

    style_items = [
        (STC_P_DEFAULT, 'default'),
        (STC_P_CHARACTER, 'char'),
        (STC_P_CLASSNAME, 'class name'),
        (STC_P_COMMENTBLOCK, 'comment block'),
        (STC_P_COMMENTLINE, 'comment line'),
        (STC_P_DECORATOR, 'decorator'),
        (STC_P_DEFNAME, 'function name'),
        (STC_P_IDENTIFIER, 'identifier'),
        (STC_P_NUMBER, "number"),
        (STC_P_OPERATOR, "operator"),
        (STC_P_STRING, "string"),
        (STC_P_STRINGEOL, "string eol"),
        (STC_P_TRIPLE, "triple quotes"),
        (STC_P_TRIPLEDOUBLE, "triple double quotes"),
        (STC_P_WORD, "keyword"),
        (STC_P_WORD2, "keyword2"),
        (STC_STYLE_BRACELIGHT, "brace light"),
        (STC_STYLE_BRACELIGHT + 64, "brace light (inactive)"),
        (STC_STYLE_BRACEBAD, "brace bad"),
        (STC_STYLE_BRACEBAD + 64, "brace bad (inactive)"),
        (SCI_STYLESETCHANGEABLE, "changeable"),
        (STC_STYLE_LINENUMBER, "line numbers"),
        (STC_STYLE_INDENTGUIDE, "ident guide"),
        (MARGIN_FOLD, "fold margin"),
    ]

    style = {
        'default': "fore:#FFFFFF, back:#000000",
        'char': "fore:#960000",
        'class name': "fore:#000096,bold",
        'comment block': "fore:#7F7F7F,back:#FFFFFF,bold",
        'comment line': "fore:#7F7F7F,back:#FFFFFF,bold",
        'decorator': "fore:#640064",
        'function name': "fore:#28003C",
        'identifier': "fore:#3C0028",
        "number": "fore:#009600,back:#FFFFFF,bold",
        "operator": "fore:#140064",
        "string": "fore:#960000",
        "string eol": "fore:#0F0000",
        "triple quotes": "fore:#960000",
        "triple double quotes": "fore:#960000",
        "keyword": "fore:#000096,bold",
        "keyword2": "fore:#000A50,bold",
        "brace light": "fore:#000000,back:#7FFF7F,bold",
        "brace light (inactive)": "fore:#000000,back:#7FFF7F,bold",
        "brace bad": "fore:#000000,back:#FF7F7F,bold",
        "brace bad (inactive)": "fore:#000000,back:#FF7F7F,bold",
        "changeable": "back:#5F5F5F,back:#000000,bold",
        "line numbers": "fore:#4B4B4B, back:#DCDCDC",
        "ident guide": "fore:#960000,bold",
        "fold margin": "back:#CBCBCB",
    }

    def __init__(self, **kwargs):
        """Init"""
        self._fileObj = kwargs['obj']
        kwargs['lexer'] = STC_LEX_PYTHON
        kwargs['text'] = self._fileObj.GetText()
        kwargs['read_only'] = self._fileObj._readOnly
        super(EditorHandler, self).__init__(**kwargs)

    def SetupMargins(self, editor):
        """Setup margins"""
        #Enable code folding
        editor.SetMarginType(MARK_MARGIN, STC_MARGIN_SYMBOL)
        editor.SetMarginType(MARGIN_LINE_NUMBERS, STC_MARGIN_NUMBER)
        editor.SetMarginType(MARGIN_FOLD, STC_MARGIN_SYMBOL)
        editor.SetMarginWidth(MARK_MARGIN, 11)
        editor.SetMarginMask(MARK_MARGIN, STC_MASK_MARKERS)
        editor.SetMarginSensitive(MARK_MARGIN, True)
        editor.SetMarginWidth(MARGIN_LINE_NUMBERS, 50)
        editor.SetMarginWidth(MARGIN_FOLD, 15)
        editor.SetMarginMask(MARGIN_FOLD, STC_MASK_FOLDERS)
        editor.SetMarginSensitive(MARGIN_FOLD, True)
        editor.SetMarginSensitive(MARGIN_LINE_NUMBERS, True)

    def SetupMarkers(self, editor):
        """Setup markers"""
        editor.MarkerDefineBitmap(MARK_BOOKMARK, wx.BitmapFromXPMData(rc._bookmark))
        editor.MarkerDefine(MARK_BREAKPOINT, STC_MARK_CIRCLE, "blue", "red")
        editor.MarkerDefine(STC_MARKNUM_FOLDEREND, STC_MARK_BOXPLUSCONNECTED, "white", "black")
        editor.MarkerDefine(STC_MARKNUM_FOLDEROPENMID, STC_MARK_BOXMINUSCONNECTED, "white", "black")
        editor.MarkerDefine(STC_MARKNUM_FOLDERMIDTAIL, STC_MARK_TCORNER, "white", "black")
        editor.MarkerDefine(STC_MARKNUM_FOLDERTAIL, STC_MARK_LCORNER, "white", "black")
        editor.MarkerDefine(STC_MARKNUM_FOLDERSUB, STC_MARK_VLINE, "white", "black")
        editor.MarkerDefine(STC_MARKNUM_FOLDER, STC_MARK_BOXPLUS, "white", "black")
        editor.MarkerDefine(STC_MARKNUM_FOLDEROPEN, STC_MARK_BOXMINUS, "white", "black")

    def SetProperties(self, editor):
        """Set other properties"""
        # Properties found from http://www.scintilla.org/SciTEDoc.html
        editor.SetProperty("fold", "1")
        editor.SetProperty("fold.comment", "1")
        editor.SetProperty("fold.compact", "0")
        editor.SetProperty("fold.margin.width", "5")
        editor.SetProperty("indent.automatic", "1")
        editor.SetProperty("indent.opening", "1")
        editor.SetProperty("indent.closing", "1")
        editor.SetProperty("indent.size", "4")
        editor.SetProperty("tabsize", "4")
        editor.SetProperty("indent.size", "4")
        editor.SetProperty("use.tabs", "1")
        editor.SetProperty("tab.indents", "1")
        editor.SetProperty("tab.timmy.whinge.level", "1")
        editor.SetIndent(4)
        editor.SetUseTabs(True)
        editor.SetTabIndents(True)
        editor.SetTabWidth(4)
        editor.IndicatorSetStyle(DEBUG_CURRENT, STC_INDIC_FULLBOX)
        editor.SetWrapMode(False)

    def SetupEvents(self, editor):
        """Set event handling"""
        editor.CmdKeyAssign(ord('+'), STC_SCMOD_CTRL, STC_CMD_ZOOMIN)
        editor.CmdKeyAssign(ord('-'), STC_SCMOD_CTRL, STC_CMD_ZOOMOUT)
        editor.Bind(wx.EVT_MENU, editor.ToggleBookmark, id=BOOKMARK_TOGGLE)
        editor.Bind(wx.EVT_MENU, editor.PrevBookmark, id=BOOKMARK_UP)
        editor.Bind(wx.EVT_MENU, editor.NextBookmark, id=BOOKMARK_DOWN)
        editor.Bind(wx.EVT_MENU, editor.Find, id=FIND)
        editor.Bind(wx.EVT_MENU, editor.FindNext, id=FIND_NEXT)
        editor.Bind(wx.EVT_MENU, editor.FindPrevious, id=FIND_PREV)
        editor.Bind(EVT_STC_MARGINCLICK, editor.OnMarginClick)
        editor.Bind(wx.EVT_KEY_UP, editor.OnKey)
        editor.Bind(EVT_STC_UPDATEUI, editor.OnUpdateEditUI)

        aTable = wx.AcceleratorTable([
            #wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F9, BREAKPOINT_TOGGLE), <- mus be handled by the view
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F2, BOOKMARK_TOGGLE),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, wx.WXK_UP, BOOKMARK_UP),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, wx.WXK_DOWN, BOOKMARK_DOWN),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('F'), FIND),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F3, FIND_NEXT),
            wx.AcceleratorEntry(wx.ACCEL_SHIFT, wx.WXK_F3, FIND_PREV),
        ])
        editor.SetAcceleratorTable(aTable)

    def Initialize(self, editor):
        """Base initialization"""
        editor.StyleClearAll()
        editor.SetLexer(self.lexer)
        editor.SetCodePage(STC_CP_UTF8)
        editor.SetStyleBits(editor.GetStyleBitsNeeded())
        self.init_fonts(editor)
        editor.HandleBreakpoints(self._fileObj.breakpoints)
        editor.HandleBookmarks(self._fileObj.bookmarks)
        editor.EnableBreakpoints(True)
        editor.EnableBookmarks(True)

        # this feature is really ugly! (80 columns gray marker)
        #
        self.SetProperties(editor)
        self.SetupEvents(editor)

        super(EditorHandler, self).Initialize(editor)