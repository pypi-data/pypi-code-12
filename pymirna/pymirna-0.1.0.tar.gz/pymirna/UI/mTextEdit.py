from PyQt5.QtWidgets import *


class mTextEdit(QTextEdit):
    def __init__(self):
        super(mTextEdit, self).__init__()

    def getData(self):
        return QTextEdit.toPlainText()

    def setData(self, data):
        if(type(data) == str):
            self.setText(data)