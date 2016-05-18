
import cgi
import os.path

from PySide.QtCore import Qt, QObject, Signal, QTextCodec
from PySide.QtGui import QDockWidget, QTextEdit, QAction, QTextCursor

from karmadbg.uicore.async import async

import pygments
from pygments.lexers import PythonLexer, CppLexer
from pygments.formatters import HtmlFormatter

class HtmlCacheFormatter(HtmlFormatter):

    def __init__(self, *args, **kwargs):
        super(HtmlCacheFormatter,self).__init__(*args, **kwargs)
        self.lineCache = []

    def wrap(self, source, outfile):
        return self._wrap_code(source)

    def _wrap_code(self, source):
        for i, t in source:
            if t == "\n":
                t = " \n"
            t = "<div class=\"highlight\"><pre>" + t + "</pre></div>"
            self.lineCache.append(t)
            yield 1, t

class SourceView(QTextEdit):

    breakpointAdded = Signal(int)
    breakpointRemoved = Signal(int)

    def __init__(self, parent, css):
        super(SourceView,self).__init__(parent)
        self.setReadOnly(True)
        self.currentLine = -1
        self.breakpointLines = set()
        self.css = css
        self.originContent = ""
        self.codec = QTextCodec.codecForLocale()
        self.document().setDefaultStyleSheet(css)
    
        cursor = QTextCursor(self.document())
        cursor.insertHtml( self.highlightSourceLine("test") )
        self.sourceBlockFmt = cursor.blockFormat()
        self.document().clear()

        cursor = QTextCursor(self.document())
        cursor.insertHtml( self.highlightCurrentLine("test") )
        self.currentBlockFmt = cursor.blockFormat()
        self.document().clear()

        cursor = QTextCursor(self.document())
        cursor.insertHtml( self.highlightBreakpointLine("test") )
        self.breakBlockFmt = cursor.blockFormat()
        self.document().clear()

    def setContent(self, content):
        if content != self.originContent:
            self.originContent = content
            self.buildDocument()

    def buildDocument(self):

        self.document().clear()

        formatter = HtmlCacheFormatter()

        localizedText = self.codec.toUnicode(self.originContent)
        self.plainLines = localizedText.splitlines()

        highlightedText = pygments.highlight(localizedText, self.lexer, formatter)
        self.highlightedLines = formatter.lineCache

        cursor = QTextCursor(self.document())
        cursor.insertHtml(highlightedText)

    def highlightSourceLine(self, str):
        return  "<pre class=\"source\">%s</pre>\n" % cgi.escape(str)

    def highlightCurrentLine(self, str):
        return  "<pre class=\"current\">%s</pre>\n" % cgi.escape(str)

    def highlightBreakpointLine(self, str):
        return "<pre class=\"breakpoint\">%s</pre>\n" % cgi.escape(str)

    def setLine(self, lineno, lineContent, blockFormat):

        block = self.document().findBlockByNumber(lineno-1)
        cursor = QTextCursor(block)
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        cursor.insertHtml(lineContent)
        cursor.setBlockFormat(blockFormat)

    def setCurrentLine(self, lineno):

        self.resetCurrentLine()

        self.currentLine = lineno

        assert( lineno -1 < len(self.plainLines) )
        line = self.plainLines[lineno-1]

        self.setLine(lineno, self.highlightCurrentLine(line), self.currentBlockFmt)
        self.showLine(lineno)

    def resetCurrentLine(self):

        lineno = self.currentLine
        self.currentLine = -1
        if lineno == -1:
            return

        line = self.highlightedLines[lineno-1]
        self.setLine(lineno, line, self.sourceBlockFmt)

    def addBreakpoint(self,lineno):
        self.breakpointLines.add(lineno)
        line = self.plainLines[lineno-1]
        self.setLine(lineno, self.highlightBreakpointLine(line), self.breakBlockFmt)

    def removeBreakpoint(self, lineno):
        self.breakpointLines.remove(lineno)
        line = self.highlightedLines[lineno-1]
        self.setLine(lineno, line, self.sourceBlockFmt)

    def removeAllBreakpoints(self):

        for lineno in self.breakpointLines:
            line = self.highlightedLines[lineno-1]
            self.setLine(lineno, line, self.sourceBlockFmt)
        self.breakpointLines = set()

    def getBreakpointLines(self):
        return list(self.breakpointLines)

    def contextMenuEvent(self, event):

        menu = self.createStandardContextMenu()

        def getSeFileEncoding(codecName):
            return lambda : self.setFileEncoding(codecName) 
        encodingMenu = menu.addMenu("Encoding")

        codecNames = [codeName.data() for codeName in QTextCodec.availableCodecs()]
        codecNames.sort()

        currentCodecName = str(self.codec.name())

        for codecName in codecNames:
            action = QAction(codecName, self)
            action.setCheckable(True)
            action.triggered.connect( getSeFileEncoding(codecName) )
            if codecName == currentCodecName:
                action.setChecked(True)
            encodingMenu.addAction(action)

        bpLineNo = self.cursorForPosition(event.pos()).blockNumber() + 1

        bpAction = QAction("Toggle breakpoint",self)
        bpAction.triggered.connect(lambda : self.setBreakpointOnLine(bpLineNo))
        menu.addAction(bpAction)

        menu.exec_(event.globalPos())

    def setBreakpointOnLine(self,bpLineNo):
        if bpLineNo in self.breakpointLines:
            self.breakpointRemoved.emit(bpLineNo)
        else:
            self.breakpointAdded.emit(bpLineNo)

    def setFileEncoding(self,codecName):

        self.codec = QTextCodec.codecForName(codecName)
        self.buildDocument()

        if not self.currentLine == -1:
            line = self.plainLines[lineno-1]
            self.setLine(self.currentLine, self.highlightCurrentLine(line), self.currentBlockFmt )

        for lineno in self.breakpointLines:
            line = self.plainLines[lineno-1]
            self.setLine(lineno, self.highlightBreakpointLine(line), self.breakBlockFmt)

    def showLine(self, lineno):
        cursor = QTextCursor(self.document().findBlockByLineNumber(lineno-1) )
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

class PythonSourceView(SourceView):

    def __init__(self, parent, css):
        self.lexer = PythonLexer(stripnl=False)
        super(PythonSourceView,self).__init__(parent, css)

class CppSourceView(SourceView):

    def __init__(self, parent, css):
        self.lexer = CppLexer(stripnl=False)
        super(CppSourceView,self).__init__(parent, css)


class SourceWidget( QDockWidget ):

    def __init__(self, uimanager, sourceFileName):
        super(SourceWidget, self).__init__()
        self.uimanager = uimanager
        self.mainWnd =uimanager.mainwnd
        self.sourceFileName = sourceFileName
        self.setWindowTitle(self.sourceFileName)
        self.setObjectName(self.sourceFileName)

    def reload(self):
        with open(self.sourceFileName) as f:
            fileContent = f.read()
            self.sourceView.setContent(fileContent)

    def setCurrentLine(self,lineno):
        self.sourceView.setCurrentLine(lineno)

    def resetCurrentLine(self):
        self.sourceView.resetCurrentLine()

    def addBreakpoint(self, lineno):
        self.sourceView.addBreakpoint(lineno)

    def removeBreakpoint(self,lineno):
        self.sourceView.removeBreakpoint(lineno)

    def removeAllBreakpoints(self):
        self.sourceView.removeAllBreakpoints()

    def showLine(self, line):
        self.sourceView.showLine(line)

class PythonSourceWidget(SourceWidget):

    def __init__(self, uimanager, sourceFileName):
        super(PythonSourceWidget,self).__init__(uimanager, sourceFileName)
        self.sourceView = PythonSourceView(self, uimanager.docCss)
        self.setWidget(self.sourceView)
        self.sourceView.breakpointAdded.connect(self.onAddBreakpoint)
        self.sourceView.breakpointRemoved.connect(self.onRemoveBreakpoint)

    def onAddBreakpoint(self, bpline):
        self.uimanager.debugClient.addPythonBreakpoint(self.sourceFileName, bpline)

    def onRemoveBreakpoint(self, bpline):
        self.uimanager.debugClient.removePythonBreakpoint(self.sourceFileName, bpline)


class NativeSourceWidget(SourceWidget):

    def __init__(self, uimanager, sourceFileName):
        super(NativeSourceWidget,self).__init__(uimanager, sourceFileName)
        self.sourceView = CppSourceView(self, uimanager.docCss)
        self.setWidget(self.sourceView)
        self.sourceView.breakpointAdded.connect(self.onAddBreakpoint)
        self.sourceView.breakpointRemoved.connect(self.onRemoveBreakpoint)

    def onAddBreakpoint(self, bpline):
        self.uimanager.debugClient.addBreakpoint(self.sourceFileName, bpline)

    def onRemoveBreakpoint(self, bpline):
        self.uimanager.debugClient.removeBreakpoint(self.sourceFileName, bpline)


class SourceManager(QObject):

    def __init__(self, widgetSettings, uimanager):
        QObject.__init__(self)
        self.uimanager = uimanager
        self.openSources = {}
        self.currentNativeSource = None
        self.currentPythonSource = None

        self.uimanager.showSourceRequired.connect(self.onShowSource)

        self.uimanager.debugClient.targetStopped.connect(self.onTargetStopped)
        self.uimanager.debugClient.targetRunning.connect(self.onTargetRunning)
        self.uimanager.debugClient.targetDetached.connect(self.onTargetDetached)
        self.uimanager.debugClient.targetThreadChanged.connect(self.onTargetDataChanged)
        self.uimanager.debugClient.targetFrameChanged.connect(self.onTargetDataChanged)
        self.uimanager.debugClient.targetBreakpointsChanged.connect(self.onTargetDataChanged)

        self.uimanager.debugClient.pythonStopped.connect(self.onPythonStopped)
        self.uimanager.debugClient.pythonRunning.connect(self.onPythonRunning)
        self.uimanager.debugClient.pythonBreakpointAdded.connect(self.onPythonBreakpointAdded)
        self.uimanager.debugClient.pythonBreakpointRemoved.connect(self.onPythonBreakpointRemoved)
        self.uimanager.debugClient.pythonExit.connect(self.onPythonExit)
        self.uimanager.debugClient.pythonStarted.connect(self.onPythonStarted)
        self.uimanager.debugClient.pythonStackFrameChanged.connect(self.onPythonStopped)

    def getSourceWidget(self, fileName, pythonSource = False):

        if fileName=="":
            return None

        if not os.path.isfile(fileName):
            return None

        if fileName in self.openSources:
            return  self.openSources[fileName]
        else:
            try:
                if pythonSource:
                    source = PythonSourceWidget(self.uimanager, fileName)
                else:
                    source = NativeSourceWidget(self.uimanager, fileName)
                source.reload()
                self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea,source)
                if len(self.openSources) > 0:
                    self.uimanager.mainwnd.tabifyDockWidget(self.openSources.values()[0], source)
                self.openSources[fileName] = source
                return source
            except IOError:
                return None

        return None

    @async
    def onTargetStopped(self):

        if self.currentNativeSource:
            self.currentNativeSource.resetCurrentLine()
            self.currentNativeSource = None

        fileName, line = yield ( self.uimanager.debugClient.getSourceLineAsync() )

        if fileName == "":
            return

        if not os.path.exists(fileName):
            fileName = yield( self.uimanager.debugClient.getSourceFileFromServerAsync() )
            if fileName == "":
                return

        source = self.getSourceWidget(fileName)

        if  source:
            source.setVisible(True)
            source.raise_()
            source.setCurrentLine(line)
            self.currentNativeSource = source

    def onTargetDataChanged(self):
        self.onTargetStopped()

    def onTargetRunning(self):
        if self.currentNativeSource:
            self.currentNativeSource.resetCurrentLine()
            self.currentNativeSource = None

    def onTargetDetached(self):

        if self.currentNativeSource:
            self.currentNativeSource.resetCurrentLine()
            self.currentNativeSource = None

        for source in self.openSources.values():
            if type(source) is NativeSourceWidget:
                source.removeAllBreakpoints()


    def onPythonStarted(self, fileName):
        source = self.getSourceWidget(fileName, pythonSource = True)
        if source:
            source.reload()

    @async
    def onPythonStopped(self):

        self.currentPythonSource = None

        fileName,line = yield( self.uimanager.debugClient.getPythonSourceLineAsync() )

        source = self.getSourceWidget(fileName, pythonSource = True)

        if source:
            source.setCurrentLine(line)
            source.setVisible(True)
            source.raise_()
            self.currentPythonSource = source

    def onPythonRunning(self):
        if self.currentPythonSource:
            self.currentPythonSource.resetCurrentLine()
            self.currentPythonSource = None

    def onPythonBreakpointAdded(self, filename, lineno):
        if filename in self.openSources:
            source = self.openSources[filename]
            source.addBreakpoint(lineno)

    def onPythonBreakpointRemoved(self, filename, lineno):
        if filename in self.openSources:
            source = self.openSources[filename]
            source.removeBreakpoint(lineno)

    def onPythonExit(self):

        if self.currentPythonSource:
            self.currentPythonSource.resetCurrentLine()
            self.currentPythonSource = None

        for source in self.openSources.values():
            if type(source) is PythonSourceWidget:
                source.removeAllBreakpoints()

    def onShowSource(self, fileName, line):

        path, ext  = os.path.splitext(fileName)

        source = self.getSourceWidget(fileName, pythonSource = ext == '.py')
        if  source:
            source.setVisible(True)
            source.raise_()
            source.showLine(line)
