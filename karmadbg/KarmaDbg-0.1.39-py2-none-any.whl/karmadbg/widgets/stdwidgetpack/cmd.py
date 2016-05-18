from PySide.QtGui import *
from PySide.QtCore import *

from karmadbg.uicore.async import async

class QCmdConsole( QTextEdit ):

    inputComplete = Signal(str)
    needAutoComplete = Signal(str)
    
    def __init__(self,parent=None):
        super(QCmdConsole, self).__init__(parent)
        self.historyCmd = []
        self.editLine = ""

        self.inputRequired = False
        self.logInsertPosition = 0

        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setAcceptDrops(False)
        self.cursorPositionChanged.connect( self.onCursorChanged )

    def writeToLog(self, str ):
        cursor = self.textCursor()
        cursor.setPosition( self.logInsertPosition, QTextCursor.MoveAnchor )
        cursor.insertText( str )
        self.logInsertPosition = cursor.position()
        self.ensureCursorVisible()

    def setReadOnly(self, readOnly):
        self.setUndoRedoEnabled(not readOnly)
        super(QCmdConsole, self).setReadOnly(readOnly)

    def requireInput(self):
        self.inputRequired = True
        cursor = self.textCursor()
        cursor.movePosition( QTextCursor.End )
        self.editPosition = cursor.position()
        self.setTextCursor( cursor )
        self.ensureCursorVisible()
        self.setReadOnly(False)

    def stopInput( self ):
        self.setReadOnly(True)

    def setEditLine( self, str ):
        cursor = self.textCursor()
        pos = self.logInsertPosition
        cursor.setPosition( pos, QTextCursor.MoveAnchor)
        cursor.movePosition( QTextCursor.End, QTextCursor.KeepAnchor )
        cursor.insertText(str)

    def getEditLine(self):
        cursor = self.textCursor()
        cursor.setPosition( self.logInsertPosition, QTextCursor.MoveAnchor)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor )
        return cursor.selectedText() 

    def onCursorChanged(self):

        if not self.inputRequired:
            return

        if  not self.hasFocus():
            return

        cursor = self.textCursor()
           
        if cursor.position() < self.document().lastBlock().position():
            self.setReadOnly(True)
            return

        if cursor.position() < self.logInsertPosition:
            cursor.setPosition(self.logInsertPosition, QTextCursor.MoveAnchor)
            self.setTextCursor(cursor)
            self.ensureCursorVisible()

        self.setReadOnly(False)

    def insertFromMimeData(self,source):
        self.insertPlainText(source.text())


    def keyPressEvent(self,event):

        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            return
        if event.key() == Qt.Key_Up:
            return
        if event.key() == Qt.Key_Down:
            return
        if event.key() == Qt.Key_Tab:
            return
        if event.key() == Qt.Key_Backspace:
            return self.onBackspaceKeyPress(event)

        super(QCmdConsole, self).keyPressEvent(event)


    def keyReleaseEvent(self, event):

        if event.key() == Qt.Key_Return:
            return self.onInputKeyRelease(event) if event.modifiers() == Qt.NoModifier else None

        if event.key() == Qt.Key_Enter:
            return self.onInputKeyRelease(event) if event.modifiers() == Qt.KeypadModifier else None

        if event.key() == Qt.Key_Up:
            return self.onKeyUpRelease(event)

        if event.key() == Qt.Key_Down:
            return self.onKeyDownRelease(event)

        if event.key() == Qt.Key_Tab:
            return self.onKeyTabRelease(event)

        super(QCmdConsole, self).keyReleaseEvent(event)

    def resizeEvent (self, resizeEvent):
        super(QCmdConsole, self).resizeEvent(resizeEvent)
        self.ensureCursorVisible()

    #def focusInEvent(self, event):
    #    cursor = self.textCursor()
    #    cursor.movePosition( QTextCursor.End )
    #    self.setTextCursor( cursor )
    #    self.ensureCursorVisible()
    #    self.setReadOnly(False)
    #    super(QCmdConsole, self).focusInEvent(event)

    def onInputKeyRelease(self,event):

        if not self.inputRequired:
            return

        inputText = self.getEditLine()

        self.inputRequired = False
        self.setEditLine("")

        self.ensureCursorVisible()
        self.historyAdd( inputText )
        self.setReadOnly(True)

        self.inputComplete.emit( inputText )


    def onKeyTabRelease(self,event):

        if not self.inputRequired:
            return

        cursor = self.textCursor()
        if cursor.position() < self.logInsertPosition:
            return

        cursor.setPosition(self.logInsertPosition, QTextCursor.KeepAnchor )
        text = cursor.selectedText() 

        self.needAutoComplete.emit(text)


    def onKeyUpRelease(self,event):

        if not self.inputRequired:
            return

        if self.historyForward():
            self.setEditLine( self.historyCmd[0] )

    def onKeyDownRelease(self,event):

        if not self.inputRequired:
            return

        if self.historyBack():
            self.setEditLine( self.historyCmd[0] )


    def contextMenuEvent(self, event):

        def cmdActionTrigger(cmd):
            return lambda : self.setEditLine(cmd)

        menu = self.createStandardContextMenu()
        menu.addSeparator()
        clearAction = QAction("Clear",self)
        clearAction.triggered.connect(self.clear)
        menu.addAction(clearAction)

        historyCmd = []
        for cmd in self.historyCmd[::-1]:
            if cmd not in historyCmd:
                historyCmd.append(cmd)
                if len(historyCmd) >= 20:
                    break;

        if len(historyCmd)>0:
            lastCmdMenu = menu.addMenu("Last commands")
            for cmd in historyCmd:
                cmdAction = QAction(cmd,self)
                cmdAction.triggered.connect(cmdActionTrigger(cmd))
                lastCmdMenu.addAction(cmdAction)

        menu.exec_(event.globalPos())

    def onBackspaceKeyPress(self,event):

        if not self.inputRequired:
            return

        cursor = self.textCursor()

        if cursor.position() <= self.logInsertPosition:
            return

        super(QCmdConsole, self).keyPressEvent(event)

   
    def historyBack(self):
        if len(self.historyCmd):
            cmd = self.historyCmd[0]
            self.historyCmd.pop(0)
            self.historyCmd.append( cmd )
            return True
        return False

    def historyForward(self):
        if len(self.historyCmd):
            cmd = self.historyCmd[-1]
            self.historyCmd.pop()
            self.historyCmd.insert( 0, cmd )
            return True
        return False

    def historyAdd(self, historyStr):
        if historyStr=="":
            return
        if len(self.historyCmd) == 0 or ( historyStr != self.historyCmd[0] and historyStr != self.historyCmd[-1] ):
            self.historyCmd.append(historyStr)
            if len( self.historyCmd ) > 100:
                self.historyCmd.pop()

    def find(self, text, fromBegin):
        if fromBegin:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.Start, QTextCursor.MoveAnchor)
            self.setTextCursor(cursor)
        super(QCmdConsole,self).find(text)

    def clear(self):
         self.logInsertPosition = 0
         super(QCmdConsole,self).clear()
         self.inputComplete.emit("")


class CmdConsoleWidget(QDockWidget):

    def __init__(self, widgetSettings, uimanager):

        super(CmdConsoleWidget,self).__init__()

        self.settings = widgetSettings
        self.uimanager = uimanager
        self.skipEcho = False

        self.textInputRequired = False

        self.console = QCmdConsole(self)

        self.setWidget( self.console )
        self.setWindowTitle("Command")

        self.console.inputComplete.connect(self.onInputComplete)
        #self.console.needAutoComplete.connect(self.onAutoComplete)

        self.uimanager.mainwnd.addDockWidget(Qt.BottomDockWidgetArea, self)

        self.uimanager.textOutputted.connect(self.onOutputRequired)
        self.uimanager.textInputRequired.connect(self.onInputRequired)
        self.uimanager.readyForCommand.connect(self.onCommandRequired)
        self.uimanager.commandProvided.connect(self.onCommandProcessing)


    def onOutputRequired(self, str):
        if not self.skipEcho:
            self.console.writeToLog(str)
        self.skipEcho = False

    def onInputRequired(self):
        self.textInputRequired = True
        self.console.requireInput()

    @async
    def onCommandRequired(self):
        prompt = yield( self.uimanager.debugClient.getPromptAsync() )
        self.console.writeToLog(prompt)
        self.textInputRequired = False
        self.console.requireInput()

    def onInputComplete(self, inputStr):
        self.console.stopInput()
        if self.textInputRequired:
            self.uimanager.textInputComplete(inputStr)
            self.textInputRequired = False
            return
        self.skipEcho = True
        self.uimanager.callCommand(inputStr)
        
    def onCommandProcessing(self):
        self.console.stopInput()

