

from .Importer.QtCore import *
from .Importer.QtGui import *

from .AutoScroll import AutoScroll

class Find(QWidget):
    """Set of controls for searching in a TextBrowser"""
    def __init__(self, browser):
        QWidget.__init__(self)
        self.browser = browser
        self.setVisible(False)

        layout = QHBoxLayout()
        self.setLayout(layout)

        label = QLabel("Find:")
        layout.addWidget(label)

        self.find_box = QLineEdit()
        layout.addWidget(self.find_box)
        self.find_box.textEdited.connect(self.text_changed)
        self.find_box.returnPressed.connect(self.next)

        next_button = QPushButton(QIcon.fromTheme("go-down"), "Next")
        layout.addWidget(next_button)
        next_button.clicked.connect(self.next)

        prev_button = QPushButton(QIcon.fromTheme("go-up"), "Previous")
        layout.addWidget(prev_button)
        prev_button.clicked.connect(self.prev)

        self.case_box = QCheckBox("Match case")
        layout.addWidget(self.case_box)
        self.case_box.toggled.connect(self.text_changed)

        layout.addStretch()

        close_button = QPushButton(QIcon.fromTheme("window-close"), "Close")
        layout.addWidget(close_button)
        close_button.clicked.connect(self.toggle_visible)

    def toggle_visible(self):
        with AutoScroll(self.browser):
            self.setVisible(not self.isVisible())
        if self.isVisible():
            self.find_box.setFocus()
        else:
            self.find_box.setText("")

    def next(self):
        self.find(True)

    def prev(self):
        self.find(False)

    def text_changed(self):
        self.find()

    def find(self, direction=None):
        exp = self.find_box.text()
        cursor = self.browser.textCursor()
        if exp:
            # adjust cursor if the text has changed to prevent sliding forward with
            # each new letter
            if (direction is None) & (cursor.hasSelection()):
                pos = cursor.selectionStart()
                cursor.clearSelection()
                cursor.setPosition(pos)

            # set search flags
            case = QTextDocument.FindCaseSensitively if self.case_box.isChecked() else QTextDocument.FindFlag()
            dirflag = QTextDocument.FindBackward if direction == False else QTextDocument.FindFlag()

            res = self._find(exp, cursor, case | dirflag)
        else:
            res = True
            cursor.clearSelection()
            self.browser.setTextCursor(cursor)

        if not res:
            # first try looping around
            cursor.clearSelection()
            if direction == False:
                cursor.movePosition(QTextCursor.End)
            else:
                cursor.movePosition(QTextCursor.Start)
            res = self._find(exp, cursor, case | dirflag)

        if not res:
            self.find_box.setStyleSheet("""
            QLineEdit {
                background: IndianRed;
            }""")
        else:
            self.find_box.setStyleSheet("")

    def _find(self, exp, cursor, flags=QTextDocument.FindFlag()):
        # interface to the document's find function to allow use of a detached
        # cursor for finds
        res = self.browser.document().find(exp, cursor, flags)
        if res.isNull():
            return False
        else:
            self.browser.setTextCursor(res)
            self.browser.ensureCursorVisible()
            return True
