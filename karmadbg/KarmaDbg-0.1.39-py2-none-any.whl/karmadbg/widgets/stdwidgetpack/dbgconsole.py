
from PySide.QtGui import *
from PySide.QtCore import *

class DebugConsoleWidget(QDockWidget):

    def __init__(self, widgetSettings, uimanager):
        super(DebugConsoleWidget, self).__init__()
        self.uimanager = uimanager
        self.uimanager.debugOutputRequired.connect(self.onDebugOutput)

        self.textView = QTextEdit(self)
        self.textView.setReadOnly(True)
        self.textView.setLineWrapMode(QTextEdit.NoWrap)
        self.textView.setAcceptDrops(False)
        self.setWidget(self.textView)

        self.uimanager.mainwnd.addDockWidget(Qt.BottomDockWidgetArea, self)

    def onDebugOutput(self, str):
        self.textView.append(str)
