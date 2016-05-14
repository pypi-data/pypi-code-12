# -*- coding: utf-8 -*-
# by mel

# Custom editor wrapper for C++/python of wx.Scintilla control
import re
import wx
import ctx
import app.resources as rc
from wx.stc import *
from  ctx import theContext as context

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


class Editor(StyledTextCtrl):
    """Common C++ editor class"""
    def __init__(self, parent, id=wx.ID_ANY, language='c++', bookmarks={}, breakpoints={}):
        """Initialize control"""
        super(Editor, self).__init__(parent, id, wx.DefaultPosition,
            wx.DefaultSize, wx.HSCROLL | wx.VSCROLL)
        self._language = language
        self.parent = parent
        self._auto = ""
        self.search_text = ''
        self.StyleClearAll()
        if self._language == 'c++':
            self.SetLexer(STC_LEX_CPP)
        else:
            self.SetLexer(STC_LEX_PYTHON)
        self.SetCodePage(STC_CP_UTF8)
        self._bookmarks = bookmarks
        self._breakpoints = breakpoints
        self._enable_breakpoints = False
        self._enable_bookmarks = False
        self.SetStyleBits(self.GetStyleBitsNeeded())

        #Default font style
        config = context.config
        f = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        dfs = f.GetNativeFontInfo().ToString()
        dfs = config.Read("config/defaultFont", dfs)
        f.SetNativeFontInfoFromString(dfs)
        for i in range(0, 39):
            self.StyleSetFont(i, f)
            if self._language == 'c++':
                self.StyleSetFont(i + 64, f)    # inactive styles

        self.SetExtraAscent(6)
        #Enable code folding
        self.SetMarginType(MARK_MARGIN, STC_MARGIN_SYMBOL)
        self.SetMarginType(MARGIN_LINE_NUMBERS, STC_MARGIN_NUMBER)
        self.SetMarginType(MARGIN_FOLD, STC_MARGIN_SYMBOL)

        self.SetMarginWidth(MARK_MARGIN, 11)
        self.SetMarginMask(MARK_MARGIN, STC_MASK_MARKERS)
        #self.StyleSetForeground(STC_STYLE_LINENUMBER, wx.Colour(75, 75, 75))
        #self.StyleSetBackground(STC_STYLE_LINENUMBER, wx.Colour(220, 220, 220))
        self.SetMarginSensitive(MARK_MARGIN, True)

        self.SetMarginWidth(MARGIN_LINE_NUMBERS, 50)
        self.StyleSetForeground(STC_STYLE_LINENUMBER, wx.Colour(75, 75, 75))
        self.StyleSetBackground(STC_STYLE_LINENUMBER, wx.Colour(220, 220, 220))
        self.SetMarginSensitive(MARGIN_LINE_NUMBERS, True)

        self.SetMarginWidth(MARGIN_FOLD, 15)
        self.SetMarginMask(MARGIN_FOLD, STC_MASK_FOLDERS)
        self.StyleSetBackground(MARGIN_FOLD, wx.Colour(200, 200, 200))
        self.SetMarginSensitive(MARGIN_FOLD, True)

        # Properties found from http://www.scintilla.org/SciTEDoc.html
        self.SetProperty("fold", "1")
        self.SetProperty("fold.comment", "1")
        self.SetProperty("fold.compact", "0")
        self.SetProperty("fold.margin.width", "5")
        self.SetProperty("indent.automatic", "1")
        self.SetProperty("indent.opening", "1")
        self.SetProperty("indent.closing", "1")
        self.SetProperty("indent.size", "4")
        self.SetProperty("tabsize", "4")
        self.SetProperty("indent.size", "4")
        self.SetProperty("use.tabs", "1")
        self.SetProperty("tab.indents", "1")
        self.SetIndent(4)
        self.SetUseTabs(True)
        self.SetTabIndents(True)
        self.SetTabWidth(4)

        self.IndicatorSetStyle(DEBUG_CURRENT, STC_INDIC_FULLBOX)

        grey = wx.Colour(100, 100, 100)
        white = wx.Colour(255, 255, 255)
        # define margin marks
        #self.bookmark_image = wx.Bitmap("bookmark.png", wx.BITMAP_TYPE_PNG)
        #self.MarkerDefine(MARK_BOOKMARK, STC_MARK_ROUNDRECT, "green", "gray")
        #self.MarkerDefineBitmap(MARK_BOOKMARK, self.bookmark_image)
        self.MarkerDefineBitmap(MARK_BOOKMARK, wx.BitmapFromXPMData(rc._bookmark))
        self.MarkerDefine(MARK_BREAKPOINT, STC_MARK_CIRCLE, "blue", "red")
        #testing
        testing = 1
        if testing:
            self.MarkerDefine(STC_MARKNUM_FOLDEREND, STC_MARK_BOXPLUSCONNECTED, "white", "black")
            self.MarkerDefine(STC_MARKNUM_FOLDEROPENMID, STC_MARK_BOXMINUSCONNECTED, "white", "black")
            self.MarkerDefine(STC_MARKNUM_FOLDERMIDTAIL, STC_MARK_TCORNER, "white", "black")
            self.MarkerDefine(STC_MARKNUM_FOLDERTAIL, STC_MARK_LCORNER, "white", "black")
            self.MarkerDefine(STC_MARKNUM_FOLDERSUB, STC_MARK_VLINE, "white", "black")
            self.MarkerDefine(STC_MARKNUM_FOLDER, STC_MARK_BOXPLUS, "white", "black")
            self.MarkerDefine(STC_MARKNUM_FOLDEROPEN, STC_MARK_BOXMINUS, "white", "black")
        else:
            self.MarkerDefine(STC_MARKNUM_FOLDEROPEN, STC_MARK_CIRCLEMINUS)
            self.MarkerDefine(STC_MARKNUM_FOLDER, STC_MARK_CIRCLEPLUS)

            self.MarkerSetForeground(STC_MARKNUM_FOLDER, white)
            self.MarkerSetBackground(STC_MARKNUM_FOLDER, grey)
            self.MarkerSetForeground(STC_MARKNUM_FOLDEROPEN, white)
            self.MarkerSetBackground(STC_MARKNUM_FOLDEROPEN, grey)
            self.MarkerDefine(STC_MARKNUM_FOLDERSUB, STC_MARK_VLINE)
            self.MarkerSetForeground(STC_MARKNUM_FOLDERSUB, white)
            self.MarkerSetBackground(STC_MARKNUM_FOLDERSUB, grey)
            self.MarkerDefine(STC_MARKNUM_FOLDEREND,
                STC_MARK_CIRCLEPLUSCONNECTED)
            self.MarkerSetForeground(STC_MARKNUM_FOLDEREND, white)
            self.MarkerSetBackground(STC_MARKNUM_FOLDEREND, grey)

            self.MarkerDefine(STC_MARKNUM_FOLDEROPENMID,
                STC_MARK_CIRCLEMINUSCONNECTED)
            self.MarkerSetForeground(STC_MARKNUM_FOLDEROPENMID,
                white)
            self.MarkerSetBackground(STC_MARKNUM_FOLDEROPENMID,
                grey)

            self.MarkerDefine(STC_MARKNUM_FOLDERMIDTAIL,
                STC_MARK_TCORNERCURVE)
            self.MarkerSetForeground(STC_MARKNUM_FOLDERMIDTAIL,
                white)
            self.MarkerSetBackground(STC_MARKNUM_FOLDERMIDTAIL,
                grey)
            self.MarkerDefine(STC_MARKNUM_FOLDERTAIL,
                STC_MARK_LCORNERCURVE)
            self.MarkerSetForeground(STC_MARKNUM_FOLDERTAIL, white)
            self.MarkerSetBackground(STC_MARKNUM_FOLDERTAIL, grey)
        # ---- End of code folding part

        #self.SetWrapMode(STC_WRAP_WORD)
        self.SetWrapMode(False)
        self.SetIndentationGuides(True)

        self.StyleSetForeground(STC_STYLE_INDENTGUIDE,
            wx.Colour(150, 0, 0))

        if self._language == 'c++':
            self.StyleSetForeground(STC_C_STRING, wx.Colour(150, 0, 0))
            self.StyleSetForeground(STC_C_STRING + 64, wx.Colour(150, 0, 0))
            self.StyleSetForeground(STC_C_PREPROCESSOR,
                wx.Colour(165, 105, 0))
            self.StyleSetForeground(STC_C_PREPROCESSOR + 64,
                wx.Colour(165, 105, 0))
            self.StyleSetForeground(STC_C_IDENTIFIER, wx.Colour(40, 0, 60))
            self.StyleSetForeground(STC_C_IDENTIFIER + 64, wx.Colour(40, 0, 60))
            self.StyleSetForeground(STC_C_NUMBER, wx.Colour(0, 150, 0))
            self.StyleSetBackground(STC_C_NUMBER, wx.Colour(255, 255, 255))
            self.StyleSetForeground(STC_C_NUMBER + 64, wx.Colour(0, 150, 0))
            self.StyleSetBackground(STC_C_NUMBER + 64, wx.Colour(255, 255, 255))
            self.StyleSetForeground(STC_C_CHARACTER, wx.Colour(150, 0, 0))
            self.StyleSetForeground(STC_C_CHARACTER + 64, wx.Colour(150, 0, 0))
            self.StyleSetForeground(STC_C_WORD, wx.Colour(0, 0, 150))
            self.StyleSetForeground(STC_C_WORD + 64, wx.Colour(0, 0, 150))
            self.StyleSetForeground(STC_C_WORD2, wx.Colour(0, 150, 0))
            self.StyleSetForeground(STC_C_WORD2 + 64, wx.Colour(0, 150, 0))
            self.StyleSetForeground(STC_C_COMMENT, wx.Colour(150, 150, 150))
            self.StyleSetForeground(STC_C_COMMENT + 64, wx.Colour(150, 150, 150))
            self.StyleSetForeground(STC_C_COMMENTLINE, wx.Colour(150, 150, 150))
            self.StyleSetForeground(STC_C_COMMENTLINE + 64, wx.Colour(150, 150, 150))
            self.StyleSetBackground(STC_C_COMMENTLINE, wx.WHITE)
            self.StyleSetBackground(STC_C_COMMENTLINE + 64, wx.WHITE)
            self.StyleSetForeground(STC_C_COMMENTDOC, wx.Colour(150, 150, 150))
            self.StyleSetForeground(STC_C_COMMENTDOC + 64, wx.Colour(150, 150, 150))
            self.StyleSetForeground(STC_C_COMMENTDOCKEYWORD, wx.Colour(0, 0, 200))
            self.StyleSetForeground(STC_C_COMMENTDOCKEYWORD + 64, wx.Colour(0, 0, 200))
            self.StyleSetForeground(STC_C_COMMENTDOCKEYWORDERROR, wx.Colour(0, 0, 200))
            self.StyleSetForeground(STC_C_COMMENTDOCKEYWORDERROR + 64, wx.Colour(0, 0, 200))
            self.StyleSetBold(STC_C_WORD, True)
            self.StyleSetBold(STC_C_WORD + 64, True)
            self.StyleSetBold(STC_C_WORD2, True)
            self.StyleSetBold(STC_C_WORD2 + 64, True)
            self.StyleSetBold(STC_C_COMMENTDOCKEYWORD, True)
            self.StyleSetBold(STC_C_COMMENTDOCKEYWORD + 64, True)
            #self.StyleSetChangeable(STC_C_COMMENT, False)
        elif self._language == 'python':
            # standard python tab checking lib
            self.SetProperty("tab.timmy.whinge.level", "1")
            self.StyleSetForeground(STC_P_CHARACTER, wx.Colour(150, 0, 0))
            self.StyleSetForeground(STC_P_CLASSNAME, wx.Colour(0, 0, 150))
            #self.StyleSetForeground(STC_P_COMMENTBLOCK, wx.Colour(150, 150, 150))
            self.StyleSetSpec(STC_P_COMMENTBLOCK, "fore:#7F7F7F,back:#FFFFFF,bold")
            #self.StyleSetForeground(STC_P_COMMENTLINE, wx.Colour(150, 150, 150))
            self.StyleSetSpec(STC_P_COMMENTLINE, "fore:#7F7F7F,back:#FFFFFF,bold")
            self.StyleSetForeground(STC_P_DECORATOR, wx.Colour(100, 0, 100))
            self.StyleSetForeground(STC_P_DEFAULT, wx.Colour(255, 255, 255))
            #self.StyleSetForeground(STC_P_DEFAULT, wx.Colour(10, 10, 50))
            self.StyleSetForeground(STC_P_DEFNAME, wx.Colour(40, 0, 60))
            self.StyleSetForeground(STC_P_IDENTIFIER, wx.Colour(60, 0, 40))
            self.StyleSetSpec(STC_P_NUMBER, "fore:#009600,back:#FFFFFF,bold")
            self.StyleSetForeground(STC_P_OPERATOR, wx.Colour(20, 0, 100))
            self.StyleSetForeground(STC_P_STRING, wx.Colour(150, 0, 0))
            self.StyleSetForeground(STC_P_STRINGEOL, wx.Colour(15, 0, 0))
            self.StyleSetForeground(STC_P_TRIPLE, wx.Colour(150, 0, 0))
            self.StyleSetForeground(STC_P_TRIPLEDOUBLE, wx.Colour(150, 0, 0))
            self.StyleSetForeground(STC_P_WORD, wx.Colour(0, 0, 150))
            self.StyleSetForeground(STC_P_WORD2, wx.Colour(0, 10, 80))
            self.StyleSetBold(STC_P_WORD, True)
            self.StyleSetBold(STC_P_WORD2, True)
            self.StyleSetBold(STC_P_CLASSNAME, True)
            #self.StyleSetChangeable(STC_P_IDENTIFIER, False)

        self.StyleSetSpec(STC_STYLE_BRACELIGHT, "fore:#000000,back:#7FFF7F,bold")
        self.StyleSetSpec(STC_STYLE_BRACELIGHT + 64, "fore:#000000,back:#7FFF7F,bold")
        self.StyleSetSpec(STC_STYLE_BRACEBAD, "fore:#000000,back:#FF7F7F,bold")
        self.StyleSetSpec(STC_STYLE_BRACEBAD + 64, "fore:#000000,back:#FF7F7F,bold")
        self.StyleSetSpec(SCI_STYLESETCHANGEABLE, "back:#5F5F5F,back:#000000,bold")

        #self.CmdKeyAssign(ord(' '), STC_SCMOD_CTRL, SCN_STYLENEEDED)
        self.CmdKeyAssign(ord('+'), STC_SCMOD_CTRL, STC_CMD_ZOOMIN)
        self.CmdKeyAssign(ord('-'), STC_SCMOD_CTRL, STC_CMD_ZOOMOUT)

        self.CmdKeyAssign(ord('+'), STC_SCMOD_CTRL, STC_CMD_ZOOMIN)
        self.CmdKeyAssign(ord('-'), STC_SCMOD_CTRL, STC_CMD_ZOOMOUT)

        #self.Bind(wx.EVT_MENU, self.ToggleBreakpoint, id=BREAKPOINT_TOGGLE)

        self.Bind(wx.EVT_MENU, self.ToggleBookmark, id=BOOKMARK_TOGGLE)
        self.Bind(wx.EVT_MENU, self.PrevBookmark, id=BOOKMARK_UP)
        self.Bind(wx.EVT_MENU, self.NextBookmark, id=BOOKMARK_DOWN)
        self.Bind(wx.EVT_MENU, self.Find, id=FIND)
        self.Bind(wx.EVT_MENU, self.FindNext, id=FIND_NEXT)
        self.Bind(wx.EVT_MENU, self.FindPrevious, id=FIND_PREV)

        aTable = wx.AcceleratorTable([
            #wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F9, BREAKPOINT_TOGGLE), <- mus be handled by the view
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F2, BOOKMARK_TOGGLE),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, wx.WXK_UP, BOOKMARK_UP),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, wx.WXK_DOWN, BOOKMARK_DOWN),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('F'), FIND),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F3, FIND_NEXT),
            wx.AcceleratorEntry(wx.ACCEL_SHIFT, wx.WXK_F3, FIND_PREV),
        ])
        self.SetAcceleratorTable(aTable)

        #self.AutoCompSetSeparator(ord(' '))
        self.popup_handler = None

    def EnableBreakpoints(self, enable=True):
        """Control if breakpoints are enabled"""
        if self._enable_breakpoints:
            if not enable:
                for br in self._breakpoints:
                    self.MarkerDelete(br, MARK_BREAKPOINT)
        else:
            if enable:
                for br in self._breakpoints:
                    self.MarkerAdd(br, MARK_BREAKPOINT)
        self._enable_breakpoints = enable

    def EnableBookmarks(self, enable=True):
        """Control if bookmarks are enabled"""
        if self._enable_bookmarks:
            if not enable:
                for br in self._bookmarks:
                    self.MarkerDelete(br, MARK_BOOKMARK)
        else:
            if enable:
                for br in self._bookmarks:
                    self.MarkerAdd(br, MARK_BOOKMARK)
        self._enable_bookmarks = enable

    def HandleBreakpoints(self, breakpoints):
        """This method can be only used while the breakpoints
        are disabled and is used for replacing the breakpoint dictionnary
        whith the project dictionnary."""
        assert not self._enable_breakpoints
        self._breakpoints = breakpoints

    def HandleBookmarks(self, bookmarks):
        """This method can be only used while the bookmarks
        are disabled and is used for replacing the bookmarks dictionnary
        whith the project dictionnary."""
        assert not self._enable_bookmarks
        self._bookmarks = bookmarks

    def SetBreakpoints(self, breakpoints):
        """Set the breakpoints"""
        if self._enable_breakpoints:
            remove = [br for br in self._breakpoints if br not in breakpoints]
            add = [br for br in breakpoints if br not in self._breakpoints]
            for br in remove:
                self.MarkerDelete(br, MARK_BREAKPOINT)
            for br in add:
                self.MarkerAdd(br, MARK_BREAKPOINT)
        self._breakpoints = breakpoints

    def GetLineStartPosition(self, line):
        """Get the starting position of the given line
        @param line: int
        @return: int
        """
        if line > 0:
            spos = self.GetLineEndPosition(line - 1)
            if self.GetLine(line).endswith("\r\n"):
                spos += 2
            else:
                spos += 1
        else:
            spos = 0
        return spos

    def GotoLine(self, line, select=False):
        """Called for goto to line"""
        super(Editor, self).GotoLine(line)
        if select:
            pos = self.GetLineEndPosition(line)
            if line > 0:
                start = self.GetLineEndPosition(line - 1) + 1
            else:
                start = 0
            self.SetSelectionStart(start)
            self.SetSelectionEnd(pos)

    def Select(self, sline, scol, eline, ecol):
        """Select a range"""
        super(Editor, self).GotoLine(sline)
        start = self.GetLineStartPosition(sline) + scol
        end = self.GetLineStartPosition(eline) + ecol
        self.SetSelectionStart(start)
        self.SetSelectionEnd(end)

    def IsModified(self):
        """Emulate unmodifiable flag using undo stack"""
        return self.CanUndo()

    def ResetModified(self):
        """Emulate unmodifiable flag using undo stack"""
        #p = self.GetCurrentPos()
        #self.SetSavePoint()
        #self.GotoPos(p)
        self.EmptyUndoBuffer()

    def Initialize(self, types=[]):
        """Initialize editor"""
        # a sample list of keywords,
        l = self._language
        if l == 'c++':
            self._keywords = "alignas alignof and and_eq asm auto "\
                "bitand bitor break case catch class "\
                "compl const constexpr const_cast continue decltype default "\
                "delete do dynamic_cast else enum explicit export extern "\
                "false for final friend goto if inline mutable namespace "\
                "new noexcept not not_eq nullptr operator or or_eq private "\
                " protected public register reinterpret_cast return signed "\
                "sizeof static static_assert static_cast struct switch template "\
                "this thread_local throw true try typedef typeid typename "\
                "union unsigned using virtual void volatile wchar_t while "\
                "xor xor_eq"
            self.SetKeyWords(0, self._keywords)
            self._types = ""
            for k in types:
                if "unsigned" in k:
                    continue
                if "long" in k:
                    continue
                self._types += k + " "
            self._types += "long unsigned "
            s = (self._types + self._keywords).split(' ')
            s.sort()
            self._auto = ""
            for k in s:
                self._auto += " " + k
            self.SetKeyWords(1, self._types)
        elif l == 'python':
            import keyword
            self._keywords = ' '.join(keyword.kwlist)
            self.SetKeyWords(0, self._keywords)
            self.SetKeyWords(1, 'self None True False arg kwarg super')
        self.EmptyUndoBuffer()
        self.SetSavePoint()
        self.SetUndoCollection(True)
        self.Bind(EVT_STC_MARGINCLICK, self.OnMarginClick)
        self.Bind(wx.EVT_KEY_UP, self.OnKey)
        self.Bind(EVT_STC_UPDATEUI, self.OnUpdateEditUI)

    @property
    def breakpoint(self):
        """check if the line holds breakpoint"""
        if not self._enable_breakpoints:
            return False
        line = self.GetCurrentLine()
        return line in self._breakpoints

    def ToggleBreakpoint(self, arg):
        """Toggle breakpoint at some line"""
        if not self._enable_breakpoints:
            return
        if isinstance(arg, wx.Event):
            line = self.GetCurrentLine()
        else:
            line = arg or self.GetCurrentLine()
        if line in self._breakpoints:
            del self._breakpoints[line]
            self.MarkerDelete(line, MARK_BREAKPOINT)
        else:
            self._breakpoints[line] = None
            self.MarkerAdd(line, MARK_BREAKPOINT)

    def ToggleBookmark(self, arg):
        """Toggle the bookmark at some line"""
        if not self._enable_breakpoints:
            return
        if isinstance(arg, wx.Event):
            line = self.GetCurrentLine()
        else:
            line = arg or self.GetCurrentLine()
        if line in self._bookmarks:
            del self._bookmarks[line]
            assert self.MarkerGet(line)
            self.MarkerDelete(line, MARK_BOOKMARK)
        else:
            self._bookmarks[line] = '<<describe the bookmark here>>'
            self.MarkerAdd(line, MARK_BOOKMARK)

    def NextBookmark(self, event):
        """Goto next bookmark"""
        line = self.GetCurrentLine()
        if self.MarkerGet(line):
                line += 1
        mark = self.MarkerNext(line, 1)
        if mark == wx.NOT_FOUND:
            mark = self.MarkerNext(0, 1)
        if mark != wx.NOT_FOUND:
            self.GotoLine(mark)

    def PrevBookmark(self, event):
        """Goto previous bookmark"""
        line = self.GetCurrentLine()
        if self.MarkerGet(line):
            line -= 1
        mark = self.MarkerPrevious(line, 1)
        if mark == wx.NOT_FOUND:
            mark = self.MarkerPrevious(self.GetLineCount(), 1)
        if mark != wx.NOT_FOUND:
            self.GotoLine(mark)

    def Find(self, event):
        """Find command"""
        # note: search flags
        # SCFIND_MATCHCASE	A match only occurs with text that matches the case of the search string.
        # SCFIND_WHOLEWORD	A match only occurs if the characters before and after are not word characters.
        # SCFIND_WORDSTART	A match only occurs if the character before is not a word character.
        # SCFIND_REGEXP	The search string should be interpreted as a regular expression.
        # SCFIND_POSIX Treat regular expression in a more POSIX compatible manner by interpreting bare
        #              ( and ) for tagged sections rather than \( and \).
        # SCFIND_CXX11REGEX Replaces scintilla regex with <regex> when compiled with CX11_REGEX
        #                   (goto http://www.scintilla.org/ScintillaDoc.html#searchFlags for details)
        from app.ui.dlg import FindText
        dlg = FindText(context.frame)
        if dlg.ShowModal() == wx.ID_OK:
            self.search_text = dlg.seach_text
            self.GotoLine(0)
            self.SearchAnchor()
            self.FindNext(event)

    def FindNext(self, event):
        """Find next command"""
        if self.search_text:
            pos = self.SearchNext(STC_FIND_MATCHCASE, self.search_text)
            if pos != wx.NOT_FOUND:
                epos = pos + len(self.search_text)
                self.GotoPos(pos + 1)
                self.SearchAnchor()
                self.SetSelection(pos, epos)

    def FindPrevious(self, event):
        """Find previous command"""
        if self.search_text:
            pos = self.SearchPrev(STC_FIND_MATCHCASE, self.search_text)
            if pos != wx.NOT_FOUND:
                epos = pos + len(self.search_text)
                self.GotoPos(pos + 1)
                self.SearchAnchor()
                self.SetSelection(pos, epos)

    def DeleteAllBookmarks(self):
        """Remove all book marks"""
        self.MarkerDeleteAll(MARK_MARGIN)

    def OnMarginClick(self, event):
        """Handles margin click"""
        if event.GetMargin() == MARGIN_FOLD:
            # fold or unfold
            lineClick = self.LineFromPosition(event.GetPosition())
            levelClick = self.GetFoldLevel(lineClick)
            if levelClick & STC_FOLDLEVELHEADERFLAG:
                self.ToggleFold(lineClick)
            return
        # toggle bookmark
        lineClick = self.LineFromPosition(event.GetPosition())
        self.ToggleBookmark(lineClick)

    def OnUpdateEditUI(self, event):
        """Handles pos changed"""
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = self.GetCurrentPos()
        if caretPos > 0:
            charBefore = self.GetCharAt(caretPos - 1)
            styleBefore = self.GetStyleAt(caretPos - 1)
        # check before
        if charBefore and chr(charBefore) in "[]{}()":
            if styleBefore == STC_P_OPERATOR:
                braceAtCaret = caretPos - 1
        # check after
        if braceAtCaret < 0:
            charAfter = self.GetCharAt(caretPos)
            styleAfter = self.GetStyleAt(caretPos)
            if charAfter and chr(charAfter) in "[]{}()":
                if styleAfter == STC_P_OPERATOR:
                    braceAtCaret = caretPos
        if braceAtCaret >= 0:
            braceOpposite = self.BraceMatch(braceAtCaret)
        if braceAtCaret != -1 and braceOpposite == -1:
            self.BraceBadLight(braceAtCaret)
        else:
            self.BraceHighlight(braceAtCaret, braceOpposite)

    def AutoIndent(self, intro):
        """Compute autoindent after key"""
        caretPos = self.GetCurrentPos()
        lnno = self.GetCurrentLine()
        if caretPos == 0 or lnno == 0:
            return
        if intro:
            lnpp = self.GetLineEndPosition(lnno - 1)
            iden = self.GetLineIndentation(lnno - 1)
            pre = self.GetCharAt(lnpp - 1)
            if chr(pre) in "[{(:":
                iden = iden + self.GetTabWidth()
            self.SetLineIndentation(lnno, iden)
            self.GotoPos(self.GetLineEndPosition(lnno))
        else:
            pre = self.GetCharAt(caretPos - 1)
            if chr(pre) in "]})":
                braceAtCaret = caretPos - 1
                braceOpposite = self.BraceMatch(braceAtCaret)
                iden = self.GetLineIndentation(
                    self.LineFromPosition(braceOpposite))
                if iden != self.GetLineIndentation(lnno):
                    self.SetLineIndentation(lnno, iden)
                    self.GotoPos(self.GetLineEndPosition(lnno))

    def OnKey(self, event):
        """Handle a scintylla event"""
        (start, end) = self.GetSelection()
        if start < end:
            return
        k = event.GetKeyCode()
        if k in [wx.WXK_NUMPAD_ENTER, wx.WXK_RETURN]:
            self.AutoIndent(True)
            return
        elif k in [wx.WXK_DELETE, wx.WXK_NUMPAD_DELETE, wx.WXK_CLEAR]:
            #self.CharRight()
            #self.DeleteBack()
            return
        elif k == wx.WXK_SPACE and event.ControlDown():
            self.popup_handler and self.popup_handler.Popup(self)
        if len(self._auto) == 0:
            event.Skip()
            return
        elif self.AutoCompActive():
            return
        self.AutoIndent(False)
        # check join letters for popup
        caretPos = self.GetCurrentPos()
        if caretPos > 2:
            text, pos = self.GetCurLine()
            text = text[:pos]
            rtext = text[::-1]
            match = re.search(r'(?P<text>(\.|\-|\>\-)?[_A-Za-z0-9]*)\s*', rtext)
            if match:
                s = match.group('text')[::-1]
                if self.popup_handler and k in [ord('.'), ord('>'), ord('<')]:
                    if s[-1] == '.':
                        self.popup_handler.Popup(self, s[:-1])
                        return
                    if s[-2:] == '->':
                        self.popup_handler.Popup(self, s[:-2])
                        return
                if len(s) > 2:
                    self.AutoCompShow(len(s), self._auto)


