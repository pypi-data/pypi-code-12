import string

from PySide.QtGui import *
from PySide.QtCore import *
from karmadbg.uicore.async import async
from karmadbg.uicore.basewidgets import NativeDataViewWidget


def getWord(bytes):
    b1 = bytes.next()
    b2 = bytes.next()
    if b1 != None and b2 != None:
        return b1 + (b2<<8)
    else:
        return None

def getDWord(bytes):
    w1 = getWord(bytes)
    w2 = getWord(bytes)
    if w1 != None and w2 != None:
        return w1 + (w2 << 16)
    return None


def getQWord(bytes):
    dw1 = getDWord(bytes) 
    dw2 = getDWord(bytes)
    if dw1 != None and dw2 != None:
        return dw1 + (dw2 << 32)
    return None

class DumpView(QTextEdit):

    offsetFormats = [
        "Not Visible", "Absolute" , "Relative"  #, "Symbol"
        ]

    formats = [
        "Not Visible", "Byte Hex", "Word Hex", "Dword Hex", "QWord Hex", "Text"
        ]

    def __init__(self, uimanager, parent = None):
        super(DumpView, self).__init__(parent)
        self.uimanager = uimanager
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setAcceptDrops(False)
        #self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setReadOnly(True)
        self.leftFormatIndex = self.getFormatIndex("Byte Hex")
        self.rightFormatIndex = self.getFormatIndex("Text")
        self.offsetFormatIndex = self.getOffsetFormatIndex("Absolute")
        self.lineCount = 0
        self.startOffset = 0
        self.currentOffset = 0

    def getFormatIndex(self, format):
        return self.formats.index(format)

    def getOffsetFormatIndex(self, format):
        return self.offsetFormats.index(format)

    def getVisibleLineCount(self):
        cursor = self.textCursor()
        fontMetric = QFontMetrics( cursor.charFormat().font()) 
        lineHeight = fontMetric.height()
        return self.height() / lineHeight

    def getByteHexLine(self, bytes):
        text = ""
        for b in bytes:
            if text != "":
               text += " "
            text += '##' if b == None else "%02x" % b
        return text

    def getWordHexLine(self, bytes):
        text = ""
        byteiter = iter(bytes)
        for i in range(8):
            if text != "":
                text += " "
            w = getWord(byteiter)
            text += '##'*2 if w == None else "%04x" % w
        return text

    def getDWordHexLine(self, bytes):
        text = ""
        byteiter = iter(bytes)
        for i in range(4):
            if text != "":
                text += " "
            dw = getDWord(byteiter)
            text += '##'*4 if dw == None else "%08x" % dw
        return text

    def getQWordHexLine(self, bytes):
        text = ""
        byteiter = iter(bytes)
        for i in range(2):
            if text != "":
                text += " "
            qw = getQWord(byteiter)
            text += '##'*8 if qw == None else "%016x" % qw
        return text


    def getTextLine(self, bytes):
        text = ""
        for b in bytes:
            c = '?' if b == None else chr(b)
            if c in string.printable and not c in string.whitespace:
                text += c
            else:
                text += "."
        return text

    def getOffsetText(self, offset, line):
        return {0 : lambda x, y: "",  1 : lambda x, y: "%0x" % (offset + line*16), 2 : lambda x, y: "%04x" % (offset - self.startOffset + line*16) }[self.offsetFormatIndex](offset, line)

    def getLeftPaneText(self, memdmp, line):
        return {
            0 : lambda x: "", 
            1 : self.getByteHexLine,
            2 : self.getWordHexLine,
            3 : self.getDWordHexLine,
            4 : self.getQWordHexLine,
            5 : self.getTextLine 
        }[self.leftFormatIndex](memdmp[ line*16 : ( line+1)*16 ]) 

    def getRightPaneText(self, memdmp, line):
        return {
            0 : lambda x: "", 
            1 : self.getByteHexLine,
            2 : self.getWordHexLine,
            3 : self.getDWordHexLine,
            4 : self.getQWordHexLine,
            5 : self.getTextLine 
        }[self.rightFormatIndex](memdmp[ line*16 : ( line+1)*16 ])

    @async
    def dataUpdate(self, expression):

        self.startOffset = yield( self.uimanager.debugClient.getExpressionAsync(expression) )
        self.currentOffset =  self.startOffset 

        if not self.isVisible():
            return

        self.lineCount = self.getVisibleLineCount() 

        self.viewUpdate()

    @async
    def viewUpdate(self):

        if self.currentOffset == 0:
            return

        rangeLength = self.lineCount * 16
        if rangeLength == 0:
            return

        memdmp = yield( self.uimanager.debugClient.getMemoryAsync(offset = self.currentOffset, length=rangeLength) )

        text = ""

        for line in xrange(self.lineCount):

            offsetText = self.getOffsetText(self.currentOffset, line)
            leftText = self.getLeftPaneText(memdmp, line)
            rightText = self.getRightPaneText(memdmp, line)

            lineText = offsetText
            if lineText != "":
                if  leftText != "":
                    lineText += " | " + leftText
            else:
                lineText = leftText


            if lineText != "":
                if rightText != "":
                    lineText += " | " + rightText
            else:
                lineText = rightText

            text += lineText + "\n"

        self.setPlainText(text)


    def resizeEvent (self, resizeEvent):

        super(DumpView, self).resizeEvent(resizeEvent)

        lineCount = self.getVisibleLineCount() 

        if self.lineCount != lineCount:
           self.lineCount = lineCount
           self.viewUpdate()

    def showEvent(self, event):

        super(DumpView, self).showEvent(event)

        lineCount = self.getVisibleLineCount() 

        if self.lineCount != lineCount:
           self.lineCount = lineCount
           self.viewUpdate()

    def keyPressEvent(self,event):

        lineCount = self.getVisibleLineCount()

        if event.key() == Qt.Key_Up:
            self.currentOffset -= 0x10
            self.viewUpdate()
            return

        if event.key() == Qt.Key_Down:
            self.currentOffset += 0x10
            self.viewUpdate()
            return

        if event.key() == Qt.Key_PageUp:
            self.currentOffset = ( self.currentOffset + 0x1000 ) // 0x1000 * 0x1000
            self.viewUpdate()
            return

        if event.key() == Qt.Key_PageDown:
            self.currentOffset = ( self.currentOffset - 0x1000 ) // 0x1000 * 0x1000
            self.viewUpdate()
            return

        super(DumpView, self).keyPressEvent(event)

    def wheelEvent( self, wheelEvent ):
        numSteps = wheelEvent.delta() / 0x10
        self.currentOffset -= numSteps * 0x10
        self.viewUpdate()


    def setLeftPaneFormat(self, index):
        self.leftFormatIndex = index
        self.viewUpdate()

    def setRightPaneFormat(self, index):
        self.rightFormatIndex = index
        self.viewUpdate()

    def setOffsetPaneFormat(self, index):
        self.offsetFormatIndex = index
        self.viewUpdate()


class MemoryDmpWidget(NativeDataViewWidget):

    def __init__(self, widgetSettings, uimanager):
        super(MemoryDmpWidget,self).__init__(uimanager)
        self.uimanager = uimanager

        frame = QFrame(parent=self)

        vlayout = QVBoxLayout()
        hlayout = QHBoxLayout()

        self.dumpView= DumpView(uimanager)

        self.exprEdit = QLineEdit()
        self.exprEdit.setText("@$scopeip")
        self.exprEdit.returnPressed.connect(self.dataUpdate)
        hlayout.addWidget(self.exprEdit)

        label = QLabel("Offset:")
        hlayout.addWidget(label)

        self.offsetCombo = QComboBox()
        for format in DumpView.offsetFormats:
            self.offsetCombo.addItem(format)
        self.offsetCombo.setCurrentIndex(self.dumpView.offsetFormatIndex)
        self.offsetCombo.currentIndexChanged.connect(lambda x : self.dumpView.setOffsetPaneFormat( self.offsetCombo.currentIndex() ) )
        hlayout.addWidget(self.offsetCombo)

        label = QLabel("Left:")
        hlayout.addWidget(label)

        self.leftCombo = QComboBox()
        for format in DumpView.formats:
            self.leftCombo.addItem(format)
        self.leftCombo.setCurrentIndex( self.dumpView.leftFormatIndex )
        self.leftCombo.currentIndexChanged.connect(lambda x : self.dumpView.setLeftPaneFormat( self.leftCombo.currentIndex() ) )
        hlayout.addWidget(self.leftCombo)


        label = QLabel("Right:")
        hlayout.addWidget(label)

        self.rightCombo = QComboBox()
        for format in DumpView.formats:
            self.rightCombo.addItem(format)
        self.rightCombo.setCurrentIndex( self.dumpView.rightFormatIndex )
        self.rightCombo.currentIndexChanged.connect(lambda x : self.dumpView.setRightPaneFormat( self.rightCombo.currentIndex() ) )
        hlayout.addWidget(self.rightCombo)

        hlayout.setSpacing(4)
        hlayout.setContentsMargins(0,0,0,0)
        vlayout.addLayout(hlayout)
        #self.hexTextEdit.setStyleSheet("border: 0px;")
        vlayout.addWidget(self.dumpView)
        vlayout.setSpacing(4)
        vlayout.setContentsMargins(4,4,4,4)
        frame.setLayout(vlayout)
        
        self.setWindowTitle("Memory")
        self.setWidget(frame)
        self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea, self)

    def dataUpdate(self):
        self.dumpView.dataUpdate(self.exprEdit.text())

