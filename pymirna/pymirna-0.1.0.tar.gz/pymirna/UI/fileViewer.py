
from PyQt5 import QtWidgets as w


class FileViewer (w.QWidget):


    def __init__(self, file, p):
        super().__init__()

        self.__file = file
        self.__unsaved = False
        self.__initUI__()



    def __initUI__(self):

        # INIT LAYOUT
        self.__layout = w.QVBoxLayout(self)


        # INIT TEXT EDITOR
        self.__textEdit = w.QTextEdit(self)
        self.__textEdit.setStyleSheet('background-color:white; color:black;')
        self.__textEdit.setFrameStyle(0)
        self.__textEdit.setDisabled(True)

        # SET CONTENT IN THE FILE
        with open(self.__file) as f:
            self.__textEdit.setText(f.read())

        self.__textEdit.textChanged.connect(self.__textChanged)
        self.__textEdit.show()

        self.setStyleSheet("background-color: white;")

        self.__layout.setContentsMargins(0,0,0,0)
        self.__layout.addWidget(self.__textEdit)
        self.setLayout(self.__layout)

        self.show()

    def getText(self):
        return self.__textEdit.toPlainText()

    def __textChanged(self):
        self.__unsaved = True

    def isUnsaved(self):
        return self.__unsaved

    def getFile(self):
        return self.__file