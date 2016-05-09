from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from pymirna.UI.SettingBlock import *
from pymirna.UI.mComboBox import *
from pymirna.UI.mTextEdit import *
from pymirna.UI.SelectInputDialog import *
from pymirna.UI.GlobalVariable import *
import os
import subprocess as sub


ERROR_RATE_DEFAULT = 0.1
REMOVE_N_DEFAULT = 1

class CutadaptUI(QWidget):
    def __init__(self, p, id):
        super(CutadaptUI, self).__init__()
        self.__parent = p
        self.__initAttribute__()
        self.__initUI()
        self.__ID = id
        self.setVisible(True)


    def __initAttribute__(self):
        self.__vboxlayout       = None
        self.__primeCombobox    = None
        self.__adapterTextEdit  = None
        self.__inputButton = None
        self.__errorRateTextEdit = None
        self.__removenTextEdit = None
        self.__expectedoutput = None
        self.__inputFile = []
        self.__inputSetting = None

    def __initUI(self):
        self.__initFrame()
        self.__initLayout()

    def __initFrame(self):
        self.__inputButton = QPushButton("Select Input File")
        self.__inputButton.setMaximumHeight(30)
        self.__inputButton.clicked.connect(self.__inputButtonPressed)

        self.__primeCombobox = mComboBox()
        self.__primeCombobox.addItem("3'")
        self.__primeCombobox.addItem("5'")

        self.__adapterTextEdit = mTextEdit()
        self.__adapterTextEdit.setMaximumHeight(30)

        self.__errorRateTextEdit = mTextEdit()
        self.__errorRateTextEdit.setMaximumHeight(30)

        self.__removenTextEdit = mTextEdit()
        self.__removenTextEdit.setMaximumHeight(30)

    def __initLayout(self):
        self.__vboxlayout = QVBoxLayout(self)
        self.__vboxlayout.setAlignment(Qt.AlignTop)
        self.__inputSetting = SettingBlock("Input File*", self.__inputButton)
        self.__vboxlayout.addLayout(self.__inputSetting)
        self.__vboxlayout.addLayout(SettingBlock("Type of Adapter", self.__primeCombobox))
        self.__vboxlayout.addLayout(SettingBlock("Adapter Sequence*", self.__adapterTextEdit))
        self.__vboxlayout.addLayout(SettingBlock("Maxximum error Rate (Default = 0.1)", self.__errorRateTextEdit))
        self.__vboxlayout.addLayout(SettingBlock("Remove up to n adapters from each read (Default = 1)", self.__removenTextEdit))

        self.setLayout(self.__vboxlayout)

    def runCommand(self):
        lis = []
        if(len(self.__inputFile) == 0):
            QMessageBox.question(QWidget(), "Alert", "No input file selected for Cutadapt ID: " + str(self.__ID+1), QMessageBox.Ok)
            return 0
        elif(len(self.__adapterTextEdit.toPlainText()) == 0):
            QMessageBox.question(self, "Alert", "No adapter sequence enter for Cutadapt ID: " + str(self.__ID+1), QMessageBox.Ok)
            return 0
        os.system("mkdir -p "+self.__parent.requestProjectDirectory()+"Result/PreProcessing/cutadapt/")
        for i in self.__inputFile:
            ret = "python3 algorithm/preprocess/cutadapt/cutadapt "
            if(self.__primeCombobox.getData() == "3'"):
                ret += "-a "
            else:
                ret += "-g "
            if(len(self.__adapterTextEdit.toPlainText()) > 0):
                ret += self.__adapterTextEdit.toPlainText()+" "

            if(len(self.__errorRateTextEdit.toPlainText()) > 0):
                ret += "-e "+self.__errorRateTextEdit.toPlainText()+" "

            if(len(self.__removenTextEdit.toPlainText()) > 0):
                ret += "-n "+self.__removenTextEdit.toPlainText()+" "

            ret += "-o "+self.__parent.requestProjectDirectory()+"Result/PreProcessing/cutadapt/"+getFilenameWithoutExtension(i)+"_Cutadapt_"+str(self.__ID)+"."+getFileExtension(i)+" "

            ret += " "+i
        if(DEBUGGING):
            print(ret)

        log = os.popen(ret)
        if(len(log) > 0):
            ol = open(self.__parent.requestProjectDirectory()+"Result/PreProcessing/cutadapt/"+getFilenameWithoutExtension(i)+"_Cutadapt_"+str(self.__ID)+".log", 'w')
            ol.writelines(log)
            ol.close()


    def getExpectedOutput(self):
        lis = []
        print("INPUT FILE : ", end='')
        print(self.__inputFile)
        if(type(self.__inputFile) is not type([])):
            return []
        for file in self.__inputFile:
            print(file)
            lis.append(self.__parent.requestProjectDirectory()+"Result/PreProcessing/"+getFilenameWithoutExtension(file)+"_Cutadapt_"+str(self.__ID)+getFileExtension(file))
        return lis

    def __inputButtonPressed(self):
        print("Select input button pressed")
        selectinput = SelectInputDialog(self, MODE_MULTI_SELECT)
        lis = self.__parent.requestFileList()
        if(type(lis) == type([])):
            filelist = lis
        lis = self.__parent.requestExpectedOutput()
        if(type(lis) == type([])):
            filelist += lis
        for i in filelist:
            if(i[len(i)-1] == '*'):
                if(getFileExtension(i[0:len(i)-1])):
                    selectinput.addChoice(i)
                    continue
            if(getFileExtension(i) == "fasta" or getFileExtension(i[0:len(i)-1]) == "fastq"):
                selectinput.addChoice(i)
        selectinput.exec_()
        # selectinput.show()

    def getInputFromDialog(self, inputDialog):
        if(inputDialog == None):
            return

        self.__inputFile = inputDialog.getInputList()
        if(len(self.__inputFile) == 0):
            self.__inputSetting.changeIdentity("Input File*")
        else:
            self.__inputSetting.changeIdentity("Input File")
