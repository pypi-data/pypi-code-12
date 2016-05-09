from PyQt5.QtWidgets import *
from pymirna.UI.mComboBox import *
from pymirna.UI.CutadaptUI import *

PREPROCESSING = 1
DISCOVERY = 2
TARGETPREDICTION = 3

class ToolBlock(QFrame):
    def __init__(self, ppui, count):
        super(ToolBlock, self).__init__()
        self.__ppui = ppui
        self.__initAttribute(count)
        self.__initUI()

    def __initAttribute(self, count):
        self.__algorithmBlock = None
        self._algorithmCombobox = None
        self.__profileBlock = None
        self.__profileCombobox = None
        self.__saveProfileButton = None
        self.__deleteButtonWidget = None
        self.__deleteToolButton = None
        self._vboxlayout = None
        self.__ID = count[0]
        self.__count = count[1]
        self._curalgo = None
        self._workflowStep = PREPROCESSING

    def __initUI(self):
        self.__initAlgorithm()
        self.__initProfile()

        self.__deleteButtonWidget = QWidget()
        self.__deleteButtonWidget.setMinimumHeight(70)
        layout = QHBoxLayout(self.__deleteButtonWidget)
        self.__deleteToolButton = QPushButton()
        self.__deleteToolButton.setText("Remove")
        self.__deleteToolButton.setFixedSize(100, 50)
        self.__deleteToolButton.clicked.connect(self.__deleteSelf)

        self.__saveProfileButton = QPushButton()
        self.__saveProfileButton.setText("Save Profile")
        self.__saveProfileButton.setFixedSize(100, 50)
        self.__saveProfileButton.clicked.connect(self.__saveProfile)

        layout.addWidget(QLabel("ID "+str(self.__ID)))
        layout.addWidget(self.__deleteToolButton)
        layout.addWidget(self.__saveProfileButton)
        self.__deleteButtonWidget.setLayout(layout)

        self.setFrameStyle(1)
        self.__initLayout()

    def __initAlgorithm(self):
        self.__algorithmBlock = QWidget()
        layout = QHBoxLayout(self.__algorithmBlock)
        self._algorithmCombobox = mComboBox()
        self._algorithmCombobox.addItem("None")
        self._algorithmCombobox.currentIndexChanged.connect(self.ChangeWidget)

        layout.addWidget(QLabel("Program"))
        layout.addWidget(self._algorithmCombobox)
        self.__algorithmBlock.setLayout(layout)

    def __initProfile(self):
        self.__profileBlock = QWidget()
        layout = QHBoxLayout(self.__profileBlock)
        self.__profileCombobox = mComboBox()
        self.__profileCombobox.addItem("None")

        layout.addWidget(QLabel("Profile"))
        layout.addWidget(self.__profileCombobox)
        self.__profileBlock.setLayout(layout)

    def __initLayout(self):
        self._vboxlayout = QVBoxLayout(self)

        self._vboxlayout.addWidget(self.__algorithmBlock)
        self._vboxlayout.addWidget(self.__profileBlock)
        self._vboxlayout.addWidget(self.__deleteButtonWidget)

        self._vboxlayout.addWidget(QWidget())

        self.setLayout(self._vboxlayout)

    def __deleteSelf(self):
        print("__deleteSelf")
        self.__ppui.deleteTool(self)
        self.setVisible(False)
        self = None

    def ChangeWidget(self):
        print("Overload This method")

    def __saveProfile(self):
        print("__saveProfile")
        print(self.getCommand())

    def runCommand(self):
        if(self._curalgo is not None):
            return self._curalgo.runCommand()
        return 0

    def getID(self):
        return self.__ID

    def getRank(self):
        return self.__count

    def requestProjectDirectory(self):
        return self.__ppui.requestProjectDirectory()

    def requestExpectedOutput(self):
        return self.__ppui.requestExpectedOutput( self._workflowStep, self.__ID)

    def requestFileList(self):
        return self.__ppui.requestFileList()

    def getExpectedOutput(self):
        return self._curalgo.getExpectedOutput()

    def getWorkflow(self):
        return self._workflowStep
