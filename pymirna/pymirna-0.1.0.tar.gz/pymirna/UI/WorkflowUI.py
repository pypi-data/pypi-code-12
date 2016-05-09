import PyQt5.QtWidgets as w
from PyQt5.QtCore import *
import pymirna.UI.SettingBlock as s
from pymirna.UI.mComboBox import *
from pymirna.UI.GlobalVariable import *

from pymirna.UI.PreProcessingToolBlock import *
import os
import sys

class WorkflowUI(w.QWidget):

    def __init__(self, p):
        super(WorkflowUI, self).__init__()
        self.__mainpage = p
        self.__initAttribute()
        self.__initScrolContent()
        self.__initCommencingBlock()
        self.__initLayout__()
        self.setVisible(True)
        self.setContentsMargins(0,0,0,0)
        self.count = 0
        self.__saveProfileButton.setVisible(False)

    def __initAttribute(self):
        self.__commencingBlock = None
        self.__autoCheckBox = None
        self.__startButton = None
        self.__saveProfileButton = None
        self.__addAlgoButton = None
        self._vboxlayout = None
        self.__vscrollArea = None
        self._vscrollContent = None
        self._vscrollLayout = None
        self._toolQueue = []
        self._toolcount = 0
        self.__projectmanager = None
        self._initID = 0

    def __initLayout__(self):
        self._vboxlayout = w.QVBoxLayout(self)
        self._vscrollLayout = w.QVBoxLayout(self._vscrollContent)
        self._vscrollLayout.setContentsMargins(2,2,2,2)
        self._vscrollLayout.setSpacing(2)

        self._vboxlayout.addWidget(self.__vscrollArea)
        self._vboxlayout.addWidget(self.__commencingBlock)
        self._vboxlayout.setAlignment(Qt.AlignBottom)
        self._vscrollLayout.setAlignment(Qt.AlignTop)
        self._vboxlayout.setContentsMargins(0,0,0,0)
        self._vboxlayout.setSpacing(3)

    def __initScrolContent(self):
        self.__vscrollArea = QScrollArea(self)
        self.__vscrollArea.setWidgetResizable(True)
        self._vscrollContent = QWidget(self.__vscrollArea)
        self._vscrollContent.setGeometry(QRect(0, 0, 600, 300))

        self.__vscrollArea.setWidget(self._vscrollContent)
        self.__vscrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)




    def __initCommencingBlock(self):

        self.__commencingBlock = w.QWidget()
        layout = w.QHBoxLayout(self.__commencingBlock)

        checkwidget = QWidget()
        checklayout = QHBoxLayout(checkwidget)
        checklayout.setAlignment(Qt.AlignCenter)
        self.__autoCheckBox = w.QCheckBox()
        self.__autoCheckBox.setChecked(False)
        self.__autoCheckBox.stateChanged.connect(self.__checkBoxChanged)
        checklayout.addWidget(self.__autoCheckBox)

        checklayout.addWidget(QLabel("Perform all task in the workflow"))
        layout.addWidget(checkwidget)

        self.__startButton = w.QPushButton()
        self.__startButton.setText("Start")
        self.__startButton.setFixedSize(100,50)
        self.__startButton.clicked.connect(self.__startPressed)
        layout.addWidget(self.__startButton)

        self.__saveProfileButton = w.QPushButton()
        self.__saveProfileButton.setText("Save Profile")
        self.__saveProfileButton.setFixedSize(100,50)
        layout.addWidget(self.__saveProfileButton)

        self.__addAlgoButton = w.QPushButton()
        self.__addAlgoButton.setText("Add Tools")
        self.__addAlgoButton.setFixedSize(100, 50)
        self.__addAlgoButton.clicked.connect(self._addTool)
        layout.addWidget(self.__addAlgoButton)

        layout.setAlignment(Qt.AlignCenter)
        self.__commencingBlock.setLayout(layout)

    def _addTool(self):
        print("Overload this one")


    def deleteTool(self, widget):
        self._toolQueue.remove(widget)
        self._vboxlayout.removeWidget(widget)


    def setAutoWorkflow(self, param):
        if(type(param) is not type(True)):
            return
        self.__autoCheckBox.setChecked(param)

    def __startPressed(self):
        if(DEBUGGING):
            print("StartPressed\n")


        if(self.__autoCheckBox.isChecked()):
            self.__mainpage.runWorkflow()
            self.__mainpage.updateProject()
            return

        for i in self._toolQueue:
            cmd = i.runCommand()
        self.__mainpage.updateProject()



    def setProjectManager(self, manager):
        self.__projectmanager = manager

    def requestProjectDirectory(self):
        return self.__projectmanager.getDirectory()

    def requestFileList(self):
        return self.__projectmanager.getFileList()

    def __checkBoxChanged(self):
        self.__mainpage.checkBoxChanged(self.__autoCheckBox.isChecked())

    def getToolQueue(self):
        return self._toolQueue

    def requestExpectedOutput(self, wf, id):
        return self.__mainpage.requestExpectedOutput(wf, id, self._toolQueue)

    def setWidgetEnable(self, state):
        if(type(state) != type(True)):
            return
        self.__startButton.setEnabled(True)

    def setInitialID(self, id):
        self._initID = id

    def getInitialID(self):
        return self._initID