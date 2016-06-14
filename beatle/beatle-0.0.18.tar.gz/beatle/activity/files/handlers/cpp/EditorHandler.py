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


class EditorHandler(EditorHandlerBase):
    """Declares c++ editor handler"""

    keyword_list = [
            "alignas",
            "alignof",
            "and",
            "and_eq",
            "asm",
            "auto",
            "bitand",
            "bitor",
            "break",
            "case",
            "catch",
            "class",
            "compl",
            "const",
            "constexpr",
            "const_cast",
            "continue",
            "decltype",
            "default",
            "delete",
            "do",
            "dynamic_cast",
            "else",
            "enum",
            "explicit",
            "export",
            "extern",
            "false",
            "for",
            "final",
            "friend",
            "goto",
            "if",
            "inline",
            "mutable",
            "namespace",
            "new",
            "noexcept",
            "not",
            "not_eq",
            "nullptr",
            "operator",
            "or",
            "or_eq",
            "private",
            "protected",
            "public",
            "register",
            "reinterpret_cast",
            "return",
            "signed",
            "sizeof",
            "static",
            "static_assert",
            "static_cast",
            "struct",
            "switch",
            "template",
            "this",
            "thread_local",
            "throw",
            "true",
            "try",
            "typedef",
            "typeid",
            "typename",
            "union",
            "unsigned",
            "using",
            "virtual",
            "void",
            "volatile",
            "wchar_t",
            "while",
            "xor xor_eq"
    ]

    style_items = [
        (STC_C_DEFAULT, "default"),
        (STC_C_STRING, "string"),
        (STC_C_STRING + 64, "string (disabled)"),
        (STC_C_PREPROCESSOR, "preprocessor"),
        (STC_C_PREPROCESSOR + 64, "preprocessor (disabled)"),
        (STC_C_IDENTIFIER, "identifier"),
        (STC_C_IDENTIFIER + 64, "identifier (disabled)"),
        (STC_C_NUMBER, "number"),
        (STC_C_NUMBER + 64, "number (disabled)"),
        (STC_C_CHARACTER, "character"),
        (STC_C_CHARACTER + 64, "character (disabled)"),
        (STC_C_WORD, "keyword"),
        (STC_C_WORD + 64, "keyword (disabled)"),
        (STC_C_WORD2, "keyword2"),
        (STC_C_WORD2 + 64, "keyword2 (disabled)"),
        (STC_C_COMMENT, "comment"),
        (STC_C_COMMENT + 64, "comment (disabled)"),
        (STC_C_COMMENTLINE, "line comment"),
        (STC_C_COMMENTLINE + 64, "line comment (disabled)"),
        (STC_C_COMMENTDOC, "comment doc"),
        (STC_C_COMMENTDOC + 64, "comment doc (disabled)"),
        (STC_C_COMMENTDOCKEYWORD, "comment doc keyword"),
        (STC_C_COMMENTDOCKEYWORD + 64, "comment doc keyword (disabled)"),
        (STC_C_COMMENTDOCKEYWORDERROR, "comment doc keyword error"),
        (STC_C_COMMENTDOCKEYWORDERROR + 64, "comment doc keyword error (disabled)"),
        (STC_C_GLOBALCLASS, "global class"),
        (STC_C_GLOBALCLASS + 64, "global class (disabled)"),
        # pike? (STC_C_HASHQUOTEDSTRING, "hash-quoted string"),
        # pike? (STC_C_HASHQUOTEDSTRING + 64, "hash-quoted string (disabled)"),
        (STC_C_OPERATOR, "operator"),
        (STC_C_OPERATOR + 64, "operator (disabled)"),
        (STC_C_PREPROCESSORCOMMENT, "preprocessor comment"),
        (STC_C_PREPROCESSORCOMMENT + 64, "preprocessor comment (disabled)"),
        (STC_C_REGEX, "regex"),
        (STC_C_REGEX + 64, "regex (disabled)"),
        (STC_C_STRINGEOL, "string end-of-line"),
        (STC_C_STRINGEOL + 64, "string end-of-line (disabled)"),
        (STC_C_STRINGRAW, "raw string"),
        (STC_C_STRINGRAW + 64, "raw string (disabled)"),
        (STC_C_VERBATIM, "verbatim string"),
        (STC_C_VERBATIM + 64, "verbatim string (disabled)"),
        (STC_C_UUID, "uuid"),
        (STC_C_UUID + 64, "uuid (disabled)"),
        (STC_STYLE_BRACELIGHT, "brace light"),
        (STC_STYLE_BRACELIGHT + 64, "brace light (inactive)"),
        (STC_STYLE_BRACEBAD, "brace bad"),
        (STC_STYLE_BRACEBAD + 64, "brace bad (inactive)"),
        (SCI_STYLESETCHANGEABLE, "changeable"),
        (STC_STYLE_LINENUMBER, "line numbers"),
        (STC_STYLE_INDENTGUIDE, "ident guide")
        ]

    style = {
            'default': "fore:#FFFFFF, back:#000000",
            'string': "fore:#960000",
            'string (disabled)': "fore:#646464",
            'preprocessor': "fore:#a56900",
            'preprocessor (disabled)': "fore:#646464",
            'identifier': "fore:#28003C",
            'identifier (disabled)': "fore:#646464",
            'number': "fore:#009600",
            'number (disabled)': "fore:#646464",
            'character': "fore:#960000",
            'character (disabled)': "fore:#646464",
            'keyword': "fore:#000096, bold",
            'keyword (disabled)': "fore:#646464, bold",
            'keyword2': "fore:#009600, bold",
            'keyword2 (disabled)': "fore:#646464, bold",
            'comment': "fore:#969696",
            'comment (disabled)': "fore:#646464",
            'line comment': "fore:#969696, back:#FFFFFF",
            'line comment (disabled)': "fore:#646464, back:#FFFFFF",
            'comment doc': "fore:#969696",
            'comment doc (disabled)': "fore:#646464",
            'comment doc keyword': "fore:#0000c8, bold",
            'comment doc keyword (disabled)': "fore:#646464, bold",
            'comment doc keyword error': "fore:#c80000, bold",
            'comment doc keyword error (disabled)': "fore:#646464, bold",
            "brace light": "fore:#000000,back:#7FFF7F,bold",
            "brace light (inactive)": "fore:#000000,back:#7FFF7F,bold",
            "brace bad": "fore:#000000,back:#FF7F7F,bold",
            "brace bad (inactive)": "fore:#000000,back:#FF7F7F,bold",
            "changeable": "back:#5F5F5F,back:#000000,bold",
            "line numbers": "fore:#4B4B4B, back:#DCDCDC",
            "ident guide": "fore:#960000,bold",
        }

    def __init__(self, **kwargs):
        """Init"""
        self._fileObj = kwargs['obj']
        kwargs['lexer'] = STC_LEX_CPP
        kwargs['text'] = self._fileObj.GetText()
        kwargs['read_only'] = self._fileObj._readOnly
        super(EditorHandler, self).__init__(**kwargs)

    def init_fonts(self, editor):
        """default font initialization"""
        super(EditorHandler, self).init_fonts(editor)
        font = self.font
        for i in range(0, 39):
            editor.StyleSetFont(i + 64, font)    # inactive styles

    def SetupMargins(self, editor):
        """Setup margins"""
        #Enable code folding
        editor.SetMarginType(MARK_MARGIN, STC_MARGIN_SYMBOL)
        editor.SetMarginType(MARGIN_LINE_NUMBERS, STC_MARGIN_NUMBER)
        editor.SetMarginType(MARGIN_FOLD, STC_MARGIN_SYMBOL)
        editor.SetMarginWidth(MARK_MARGIN, 11)
        editor.SetMarginWidth(MARGIN_LINE_NUMBERS, 50)
        editor.SetMarginWidth(MARGIN_FOLD, 15)
        editor.SetMarginMask(MARK_MARGIN, STC_MASK_MARKERS)
        editor.SetMarginMask(MARGIN_FOLD, STC_MASK_FOLDERS)
        editor.SetMarginSensitive(MARK_MARGIN, True)
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
        editor.SetIndent(4)
        editor.SetUseTabs(True)
        editor.SetTabIndents(True)
        editor.SetTabWidth(4)

    def SetupEvents(self, editor):
        """Setup events"""
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
        self.SetProperties(editor)
        self.SetupEvents(editor)
        super(EditorHandler, self).Initialize(editor)