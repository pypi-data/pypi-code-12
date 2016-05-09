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

class FastqtoFasta(QWidget):
    def __init__(self, p, id):
        super(FastqtoFasta, self).__init__()
        self.__parent = p
        self.__initAttribute__()
        self.__initUI()
        self.__ID = id
        self.setVisible(True)


    def __initAttribute__(self):
        self.__vboxlayout       = None
        self.__inputButton = None
        self.__inputFile = []
        self.__inputSetting = None

    def __initUI(self):
        self.__initFrame()
        self.__initLayout()

    def __initFrame(self):
        self.__inputButton = QPushButton("Select Input File")
        self.__inputButton.setMaximumHeight(30)
        self.__inputButton.clicked.connect(self.__inputButtonPressed)

    def __initLayout(self):
        self.__vboxlayout = QVBoxLayout(self)
        self.__vboxlayout.setAlignment(Qt.AlignTop)
        self.__inputSetting = SettingBlock("Input File*", self.__inputButton)
        self.__vboxlayout.addLayout(self.__inputSetting)

        self.setLayout(self.__vboxlayout)

    def runCommand(self):
        lis = []
        if(len(self.__inputFile) == 0):
            QMessageBox.question(QWidget(), "Alert", "No input file selected for fastq to fasta ID: " + str(self.__ID+1), QMessageBox.Ok)
            return 0
        os.system("mkdir -p "+self.__parent.requestProjectDirectory()+"Result/PreProcessing/FastqtoFasta/")
        for i in self.__inputFile:
            ret = "algorithm/preprocess/fastxtoolkit/fastq_to_fasta "

            ret += "-i "+i+" "

            ret += "-o "+self.__parent.requestProjectDirectory()+"Result/PreProcessing/FastqtoFasta/"+getFilenameWithoutExtension(i)+str(self.__ID)+".fasta"
        if(DEBUGGING):
            print(ret)

        log = os.popen(ret).read()
        if(len(log) > 0):
            ol = open(self.__parent.requestProjectDirectory()+"Result/PreProcessing/FastqtoFasta/"+getFilenameWithoutExtension(i)+"_FastqtoFasta_"+str(self.__ID)+".log", 'w')
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
            lis.append(self.__parent.requestProjectDirectory()+"Result/PreProcessing/"+getFilenameWithoutExtension(file)+"_FastqtoFasta_" + str(self.__ID)+".fasta*")
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
            if(getFileExtension(i) == "fastq"):
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
        print(self.__inputFile)
