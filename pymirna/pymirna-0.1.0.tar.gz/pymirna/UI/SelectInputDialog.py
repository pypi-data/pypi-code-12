from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from pymirna.Utility.FileReader import *

MODE_MULTI_SELECT = 0
MODE_SINGLE_SELECT = 1

class SelectInputDialog(QDialog):
    def __init__(self, p, mode):
        super(SelectInputDialog, self).__init__()
        self.__parent = p
        self.__initAttribute()
        self.__mode = mode
        self.__initScroll()
        self.__initUI()
        self.setMaximumSize(640, 480)
        self.setMinimumSize(320, 480)

    def __initAttribute(self):
        self.__scrollArea = None
        self.__scrollContent = None
        self.__scrollLayout = None

        self.__layout = None
        self.__okButton = None
        self.__cancelButton = None

        self.__filelist = []
        self.__selectFile = 0
        self.__mode = MODE_MULTI_SELECT

    def __initScroll(self):
        self.__scrollArea = QScrollArea(self)
        self.__scrollArea.setWidgetResizable(True)

        self.__scrollContent = QWidget(self.__scrollArea)

        self.__scrollArea.setWidget(self.__scrollContent)
        self.__scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.__scrollLayout = QVBoxLayout(self.__scrollContent)
        self.__scrollLayout.setAlignment(Qt.AlignTop)
        self.__scrollLayout.setSpacing(5)

    def __initUI(self):
        self.__layout = QVBoxLayout(self)
        widget = QWidget()
        layout = QHBoxLayout(widget)
        widget.setLayout(layout)

        self.__okButton = QPushButton()
        self.__okButton.setText("OK")
        self.__okButton.clicked.connect(self.__okPressed)

        self.__cancelButton = QPushButton()
        self.__cancelButton.setText("Cancel")
        self.__cancelButton.clicked.connect(self.__cancelPressed)

        layout.addWidget(self.__okButton)
        layout.addWidget(self.__cancelButton)

        self.__layout.addWidget(self.__scrollArea)
        self.__layout.addWidget(widget)




    def addChoice(self, fileurl):
        newChoice = ChoiceBlock(fileurl, self)
        newChoice.setParent(self.__scrollContent)
        self.__scrollLayout.addWidget(newChoice)
        self.__filelist.append(newChoice)

    def getInputList(self):
        lis = []
        if(self.__mode == MODE_SINGLE_SELECT and self.__selectFile != None):
            return self.__selectFile.split('*')[0]

        for i in self.__filelist:
            if(i.isCheck()):
                lis.append(i.getFileURL().split('*')[0])
        return lis

    def __okPressed(self):
        self.__parent.getInputFromDialog(self)
        self.close()

    def __cancelPressed(self):
        self.__parent.getInputFromDialog(None)
        self.close()

    def elementChecked(self, cb):
        if(self.__mode == MODE_MULTI_SELECT):
            return
        if(self.__selectFile == 0):
            self.__selectFile = cb.getFileURL()
            return
        if(type(self.__selectFile) != ChoiceBlock):
            return
        self.__selectFile.setState(False)
        self.__selectFile = cb

class ChoiceBlock(QWidget):
    def __init__(self, fileurl, p):
        super(ChoiceBlock, self).__init__()

        self.__fileurl = fileurl
        self.__p = p
        self.__initUI()

    def __initUI(self):
        self.__layout = QHBoxLayout(self)
        self.__checkbox = QCheckBox()
        self.__label = QLabel(self.__fileurl)

        self.__layout.setAlignment(Qt.AlignLeft)
        self.__layout.setContentsMargins(0,0,0,0)
        self.__layout.setSpacing(5)
        self.__layout.addWidget(self.__checkbox)
        self.__layout.addWidget(self.__label)
        self.__checkbox.stateChanged.connect(self.__checked)

        self.setLayout(self.__layout)

    def isCheck(self):
        return self.__checkbox.isChecked()

    def getFileURL(self):
        return self.__fileurl

    def __checked(self):
        self.__p.elementChecked(self)

    def setState(self, state):
        self.__checkbox.setCheckState(state)