
from PySide.QtGui import QDockWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QFrame, QLineEdit, QTextCursor, QTextBrowser, QSplitter, QAction
from PySide.QtCore import Qt


from karmadbg.uicore.async import async

import cgi
import re
import pprint

class CmdHtmlWidget( QDockWidget ):

    htmlTemplate = '''
<!DOCTYPE html>

<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta charset="utf-8" />
    <title></title>
</head>
<body>
</body>
</html>
    '''

    def __init__(self, widgetSettings, uimanager):
        super(CmdHtmlWidget,self).__init__()
        self.uimanager = uimanager

        self.historyCmd = []
        self.textInputRequired = False

        self.completedParagraph = True

        self.inputField = QTextEdit(self)
        self.inputField.setMinimumHeight(20)
        
        self.promptLabel = QLabel(">>>", self)
        
        self.historyField = QTextBrowser(self)
        self.historyField.setReadOnly(True)
        self.historyField.setUndoRedoEnabled(False)
        self.historyField.setLineWrapMode(QTextEdit.NoWrap)
        self.historyField.setOpenLinks(False)
        self.historyField.setHtml(self.htmlTemplate)
        self.historyField.anchorClicked.connect(self.onLinkClicked)
        self.historyField.document().setDefaultStyleSheet(uimanager.docCss)

        vlayout = QVBoxLayout()
        vlayout.addWidget(self.promptLabel)
        vlayout.addStretch()

        hlayout = QHBoxLayout()
        hlayout.addLayout(vlayout)
        hlayout.addWidget(self.inputField)
        hlayout.setContentsMargins(4,0,4,4)

        frame = QFrame(self)
        frame.setMinimumHeight(20)
        frame.setLayout(hlayout)

        splitter = QSplitter(Qt.Orientation.Vertical, self)
        self.splitter = splitter
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self.historyField)
        splitter.addWidget(frame)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        
        self.setWidget(splitter)
        self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea, self)

        self.uimanager.textFormattedOutputted.connect(self.onOutputFormatted)
        self.uimanager.readyForCommand.connect(self.onCommandRequired)
        self.uimanager.commandInProgress.connect(self.onCommandInProgress)
        self.uimanager.textInputRequired.connect(self.onInputRequired)

        self.historyField.contextMenuEvent = self.contextMenuEvent
        self.inputField.keyPressEvent = self.onKeyPressEvent
        self.inputField.keyReleaseEvent = self.onKeyReleaseEvent
        self.inputField.insertFromMimeData = self.inputFieldInsertFromMime

    def saveLayout(self, guiSettings) :
        guiSettings.beginGroup(self.objectName())
        guiSettings.setValue("splitterState", self.splitter.saveState())
        guiSettings.endGroup()

    def restoreLayout(self, guiSettings) :
        guiSettings.beginGroup(self.objectName())
        splitterState = guiSettings.value("splitterState")
        if splitterState <> None :
            self.splitter.restoreState(splitterState)
        guiSettings.endGroup()

    def onKeyPressEvent(self,event):  

        if event.key() == Qt.Key_Return and event.modifiers() == Qt.NoModifier:
            return 
        if event.key() == Qt.Key_Enter and event.modifiers() == Qt.NoModifier:
            return
        if event.key() == Qt.Key_Up:
            return
        if event.key() == Qt.Key_Down:
            return
        if event.key() == Qt.Key_Tab:
            return

        QTextEdit.keyPressEvent(self.inputField, event)


    def onKeyReleaseEvent(self, event):

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

        QTextEdit.keyReleaseEvent(self.inputField, event)


    def contextMenuEvent(self, event):

        menu = self.historyField.createStandardContextMenu()
        menu.addSeparator()
        clearAction = QAction("Clear",self)
        clearAction.triggered.connect(lambda: self.historyField.setHtml(self.htmlTemplate))
        menu.addAction(clearAction)
        menu.popup(event.globalPos())

    def inputFieldInsertFromMime(self, mimeSource):
        QTextEdit.insertPlainText(self.inputField, mimeSource.text())

    def onKeyUpRelease(self,event):
        self.historyForward()
        cursor = self.inputField.textCursor()
        cursor.setPosition( 0, QTextCursor.MoveAnchor)
        cursor.movePosition( QTextCursor.End, QTextCursor.KeepAnchor )
        cursor.insertText(self.getHistory(0))

    def onKeyDownRelease(self,event):
        self.historyBack()
        cursor = self.inputField.textCursor()
        cursor.setPosition( 0, QTextCursor.MoveAnchor)
        cursor.movePosition( QTextCursor.End, QTextCursor.KeepAnchor )
        cursor.insertText(self.getHistory(0))

    @async
    def onKeyTabRelease(self,event):
        text = self.inputField.toPlainText()
        autoComplete = yield( self.uimanager.debugClient.getAutoCompleteAsync(text))

        if autoComplete:
            if autoComplete[0] == "filePath":
                self.autoCompleteFilePath(autoComplete)

    def autoCompleteFilePath(self, autoComplete):

        _, inputComplete, hints = autoComplete

        cursor = self.inputField.textCursor()
        cursor.movePosition(  QTextCursor.End, QTextCursor.MoveAnchor)
        cursor.insertText(inputComplete)

        if len(hints) > 1:
            hints = hints if  len(hints) < 40 else hints[:40]
            i = 0
            str = ""
            for hintType, hint in hints:
                if i % 4 == 0:
                    str += "<br>"
                if hintType == "file":
                    str += "&nbsp;&nbsp;&nbsp;&nbsp;<span class=\"filename\">"
                else:
                    str += "&nbsp;&nbsp;&nbsp;&nbsp;<span class=\"dirname\">"
                
                str += ("%- 20s</span>" % ( hint if len(hint) < 20 else hint[:20] )).replace(" ", "&nbsp;")
                i += 1
            str += "<br>"

            cursor = self.historyField.textCursor()
            cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
            cursor.insertHtml(str)
            sb = self.historyField.verticalScrollBar()
            sb.setValue(sb.maximum())
            
    def onLinkClicked(self, url):
        self.uimanager.callCommand(url.toString())

    def onInputKeyRelease(self,event):
        text = self.inputField.toPlainText()
        if text == "\n":
            text = ""
        self.inputField.setPlainText("")
        if self.textInputRequired == False:
            if text and ( len(self.historyCmd) == 0 or ( text != self.historyCmd[0] and text != self.historyCmd[-1] ) ):
                self.historyCmd.append(text)
                if len( self.historyCmd ) > 100:
                    self.historyCmd.pop()
            self.uimanager.callCommand(text)
        else:
            self.textInputRequired = False
            self.uimanager.textInputComplete(text)
            self.inputField.setEnabled(False)

    def outputLine(self, str):
        if not str:
            return
        if self.completedParagraph:
            self.completedParagraph = str[-1] == "\n"
            str = "<pre>" + str + "</pre>"
            self.historyField.append(str)
        else:
             self.historyField.moveCursor(QTextCursor.End)
             pos = str.find("\n")
             if pos != -1:
                self.historyField.insertHtml(str[0:pos])
                self.completedParagraph = True
                if str[pos:] != "\n":
                    self.outputLine(str[pos:])
             else:
                self.historyField.insertHtml(str)

        
    def onOutputFormatted(self, str):

        self.historyField.setUpdatesEnabled(False)

        self.outputLine(str)

        sb = self.historyField.verticalScrollBar()
        sb.setValue(sb.maximum())
        sb = self.historyField.horizontalScrollBar()
        sb.setValue(sb.minimum())

        self.historyField.setUpdatesEnabled(True)

    @async
    def onCommandRequired(self):
        prompt = yield( self.uimanager.debugClient.getPromptAsync() )
        self.promptLabel.setText(prompt)
        self.inputField.setEnabled(True)
        self.inputField.setFocus()

    def onCommandInProgress(self):
        self.inputField.setEnabled(False)
        self.promptLabel.setText("BUSY")

    def onInputRequired(self):
        self.promptLabel.setText("IN>")
        self.inputField.setEnabled(True)
        self.inputField.setFocus()
        self.textInputRequired = True

    def historyForward(self):
        if len(self.historyCmd):
            cmd = self.historyCmd[-1]
            self.historyCmd.pop()
            self.historyCmd.insert( 0, cmd )

    def historyBack(self):
        if len(self.historyCmd):
            cmd = self.historyCmd[0]
            self.historyCmd.pop(0)
            self.historyCmd.append( cmd )

    def getHistory(self,index):
        return self.historyCmd[index] if index < len(self.historyCmd) else ""
