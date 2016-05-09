from pymirna.UI.TargetPredictionToolBlock import *
from pymirna.UI.mComboBox import *
from pymirna.UI.mTextEdit import *
from pymirna.UI.mTreeWidgetItem import *
from pymirna.UI.GlobalVariable import *

ERROR_RATE_DEFAULT = 0.1
REMOVE_N_DEFAULT = 1

class MirandaUI(QWidget):
    def __init__(self, p, id):
        super(MirandaUI, self).__init__()
        self.__parent = p
        self.__initAttribute__()
        self.__initUI()
        self.__ID = id
        self.setVisible(True)


    def __initAttribute__(self):
        self.__vboxlayout       = None

        self.__inputQuery = None
        self.__inputSequences = []
        self.__inputSequencesSetting = None
        self.__inputQueryButton = None
        self.__inputQuerySetting = None
        self.__inputSequencesButton = None
        self.__scoreTextedit = None
        self.__energyTextedit = None
        self.__scalingTextedit = None
        self.__gap_openTextedit = None
        self.__gap_extendTextedit = None
        self.__inputMode = None

    def __initUI(self):
        self.__initFrame()
        self.__initLayout()



    def __initFrame(self):
        self.__inputQueryButton = QPushButton()
        self.__inputQueryButton.setText("Select input query file")
        self.__inputQueryButton.setMaximumHeight(30)
        self.__inputSequencesButton = QPushButton()
        self.__inputSequencesButton.setText("Select input sequences files")
        self.__inputSequencesButton.setMaximumHeight(30)
        self.__scoreTextedit = mTextEdit()
        self.__scoreTextedit.setMaximumHeight(30)
        self.__energyTextedit = mTextEdit()
        self.__energyTextedit.setMaximumHeight(30)
        self.__scalingTextedit = mTextEdit()
        self.__scalingTextedit.setMaximumHeight(30)
        self.__gap_extendTextedit = mTextEdit()
        self.__gap_extendTextedit.setMaximumHeight(30)
        self.__gap_openTextedit = mTextEdit()
        self.__gap_openTextedit.setMaximumHeight(30)

        self.__inputQueryButton.clicked.connect(self.__inputQueryPressed)
        self.__inputSequencesButton.clicked.connect(self.__inputSequencesPressed)

    def __initLayout(self):
        self.__vboxlayout = QVBoxLayout(self)
        self.__vboxlayout.setAlignment(Qt.AlignTop)

        self.__inputQuerySetting = SettingBlock("Input query*", self.__inputQueryButton)
        self.__inputSequencesSetting = SettingBlock("Input sequence*", self.__inputSequencesButton)

        self.__vboxlayout.addLayout(self.__inputQuerySetting)
        self.__vboxlayout.addLayout(self.__inputSequencesSetting)
        self.__vboxlayout.addLayout(SettingBlock("Score threshold (Default = 140.0)", self.__scoreTextedit))
        self.__vboxlayout.addLayout(SettingBlock("Energy threshold in kcal/mol (Default = 1.0)", self.__energyTextedit))
        self.__vboxlayout.addLayout(SettingBlock("Scaling parameter (Default = 4.0)", self.__scalingTextedit))
        self.__vboxlayout.addLayout(SettingBlock("Gap-open penalty (Default = -4.0)", self.__gap_openTextedit))
        self.__vboxlayout.addLayout(SettingBlock("Gap-extend penalty (Default = -9.0", self.__gap_extendTextedit))

        self.setLayout(self.__vboxlayout)

    def runCommand(self):
        lis = []
        os.system("mkdir -p "+self.__parent.requestProjectDirectory()+"Result/TargetPrediction/miRanda/")

        if(len(self.__inputSequences) == 0):
            QMessageBox.question(self, "Alert", "No input sequence for miRanda"+str(self.__ID+1), QMessageBox.Ok)
            return
        if(len(self.__inputQuery) == 0):
            QMessageBox.question(self, "Alert", "No input Query for miRanda"+str(self.__ID+1), QMessageBox.Ok)
            return

        for i in self.__inputSequences:
            ret = "algorithm/targetprediction/miranda/miranda "

            ret += self.__inputQuery + " "

            ret += i + " "

            if(len(self.__scoreTextedit.toPlainText()) > 0):
                ret += "-sc "+self.__scoreTextedit.toPlainText()+" "

            if(len(self.__energyTextedit.toPlainText()) > 0):
                ret += "-en "+self.__energyTextedit.toPlainText()+" "

            if(len(self.__scalingTextedit.toPlainText()) > 0):
                ret += "-scale "+self.__scalingTextedit.toPlainText()+" "

            if(len(self.__gap_extendTextedit.toPlainText()) > 0):
                ret += "-ge "+self.__gap_extendTextedit.toPlainText()+" "
            if(len(self.__gap_openTextedit.toPlainText()) > 0):
                ret += "-go "+self.__gap_openTextedit.toPlainText()+" "

            ret += "-out "+self.__parent.requestProjectDirectory()+"Result/TargetPrediction/miranda/"+getFilenameWithoutExtension(i)+"_miRanda_"+str(self.__ID)+".txt"

        if(DEBUGGING):
            print(ret)

        log = os.popen(ret)
        if(len(log) > 0):
            ol = open(self.__parent.requestProjectDirectory()+"Result/TargetPrediction/miranda/"+getFilenameWithoutExtension(i)+"_miRanda_"+str(self.__ID)+".log", 'w')
            ol.writelines(log)
            ol.close()

    def getExpectedOutput(self):
        return []

    def __inputSequencesPressed(self):
        print("Select input sequences button pressed")
        self.__inputMode = "seq"
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
            if(getFileExtension(i) == "fasta"):
                selectinput.addChoice(i)
        selectinput.exec_()
        # selectinput.show()

    def __inputQueryPressed(self):
        print("Select input query button pressed")
        self.__inputMode = "que"
        selectinput = SelectInputDialog(self, MODE_SINGLE_SELECT)
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
            if(getFileExtension(i) == "fasta"):
                selectinput.addChoice(i)
        selectinput.exec_()
        # selectinput.show()

    def getInputFromDialog(self, inputDialog):
        if(inputDialog == None):
            return
        if(self.__inputMode == "seq"):
            self.__inputSequences = inputDialog.getInputList()
            if(len(self.__inputSequences) == 0):
                self.__inputSequencesSetting.changeIdentity("Input sequence*")
                return
            else:
                self.__inputSequencesSetting.changeIdentity("Input sequence")
                return


        elif(self.__inputMode == 'que'):
            self.__inputQuery = inputDialog.getInputList()
            if(len(self.__inputQuery) == 0):
                self.__inputQuerySetting.changeIdentity("Input query*")
                return
            else:
                self.__inputQuerySetting.changeIdentity("Input query")
                return
