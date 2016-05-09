__author__ = 'haru'

from PyQt5 import QtWidgets as w
from PyQt5 import QtGui as g
from PyQt5 import QtCore as c

from pymirna.UI.PreProcessUI import *
from pymirna.UI.TargetPrediction import *
from pymirna.UI.fileViewer import *
from pymirna.Utility.ProjectUtility import *
from pymirna.UI.mTreeWidgetItem import *
from pymirna.UI.Discovery import *
from pymirna.UI.GlobalVariable import *

OUTPUT_TAB_ID = 3
DEBUGGING = True

class MainPage(w.QMainWindow):
    def __init__(self, title = "miRWB", width = 1920, height = 1080):
        super(MainPage, self).__init__()
        self.setWindowTitle(title)
        self.setMaximumSize(width, height)

        geo = QDesktopWidget().screenGeometry()
        self.setGeometry(0,0,geo.width() * 0.7, geo.height()*(0.7))
        self.__initAttribute__()
        self.__initUI__()

        self.show()

    def __initAttribute__(self):
        self.__menubar                = None
        self.__fileMenu             = None
        self.__toolMenu             = None
        self.__exitAction           = None
        self.__removeFileAction     = None
        self.__algoCompareAction    = None
        self.__createProjectAction  = None
        self.__addFileAction        = None
        self.__openProjectAction    = None
        self.__closeProjectAction   = None
        self.__leftContainer        = None
        self.__leftScrollArea       = None
        self.__leftVContainer       = None
        self.__leftVLayout          = None
        self.__outputContainer      = None
        self.__centerVContainer     = None
        self.__rightContainer       = None
        self.__rightVContainer      = None
        self.__preTab               = None
        self.__discoveryTab         = None
        self.__predictTab           = None
        self.__outputTab            = None
        self.__outputLayout         = None
        self.__projectUtility       = None
        self.__projectmanager       = None
        self.__isOpenProject        = False
        self.__initPreID            = 0
        self.__initPredictID        = 0
        self.__initDiscoveryID      = 0


    def __initUI__(self):

        self.__initAction__()
        self.__initMenuBar__()
        self.__initContainer__()
        self.__initLayout__()
        self.__initList__()
        self.__projectUtility = ProjectManager()
        self.__preTab.setProjectManager(self.__projectUtility)
        self.__preTab.setInitialID(self.__initPreID)
        self.__discoveryTab.setProjectManager(self.__projectUtility)
        self.__discoveryTab.setInitialID(self.__initDiscoveryID)
        self.__predictTab.setProjectManager(self.__projectUtility)
        self.__predictTab.setInitialID(self.__initPredictID)



    def __initMenuBar__(self):
        # self.statusBar()

        # ADD ELEMENT TO MENU BAR
        self.__menubar = w.QMenuBar()

        self.__fileMenu = self.__menubar.addMenu('&File')
        self.__toolMenu = self.__menubar.addMenu('&Tool')

        # ADD ACTION TO MENU BAR
        self.__fileMenu.addAction(self.__createProjectAction)
        self.__fileMenu.addAction(self.__openProjectAction)
        self.__fileMenu.addAction(self.__addFileAction)
        self.__fileMenu.addAction(self.__removeFileAction)
        self.__fileMenu.addAction(self.__closeProjectAction)
        self.__fileMenu.addAction(self.__exitAction)
        self.__toolMenu.addAction(self.__algoCompareAction)

    def __initAction__(self):
        self.__exitAction = w.QAction('Exit', self)
        self.__exitAction.triggered.connect(self.close)

        self.__algoCompareAction = w.QAction('Performance Comparison', self)

        self.__createProjectAction = w.QAction('Create Project', self)
        self.__createProjectAction.triggered.connect(self.__createProject)

        self.__openProjectAction = w.QAction('Open Project', self)
        self.__openProjectAction.triggered.connect(self.__openProject)

        self.__closeProjectAction = w.QAction('Close Project', self)
        self.__closeProjectAction.triggered.connect(self.__closeProject)
        self.__closeProjectAction.setDisabled(True)

        self.__addFileAction = w.QAction('Add File', self)
        self.__addFileAction.triggered.connect(self.__addFileTriggered)
        self.__addFileAction.setDisabled(True)

        self.__removeFileAction = w.QAction('Remove File', self)
        self.__removeFileAction.triggered.connect(self.__removeFileTriggered)
        self.__removeFileAction.setDisabled(True)


    def __initContainer__(self):

        # INITIALIZE LEFT CONTAINER
        self.__leftContainer = w.QTabWidget()
        self.__leftContainer.setMaximumWidth(self.width() * 0.22)

        # INITIALIZE RIGHT VERTICLE CONTAINER
        self.__rightVContainer = w.QVBoxLayout(self.__rightContainer)

        # CREATE WORKFLOW TAB
        self.__preTab = PreProcessUI(self)
        self.__discoveryTab = Discovery(self)
        self.__predictTab = TargetPrediction(self)
        self.__outputTab = w.QWidget()
        self.__outputTab.setStyleSheet("background-color: white;")

        # INITIALIZE LEFT VERTICLE CONTAINER
        self.__leftVContainer = w.QWidget()
        self.__leftScrollArea = w.QScrollArea()
        self.__leftScrollArea.setWidget(self.__leftVContainer)
        self.__leftContainer.addTab(self.__leftVContainer, "Project Manager")

        # INITIALIZE RIGHT CONTAINER
        self.__rightContainer = w.QTabWidget()
        self.__rightContainer.setElideMode(3)
        self.__rightContainer.setUsesScrollButtons(True)


        # INITIALIZE CENTRAL CONTAINER
        self.__centralContainer = w.QWidget()
        self.setCentralWidget(self.__centralContainer)

        # ADD WORKFLOW TAB TO RIGHT CONTAINER
        self.__rightContainer.addTab(self.__preTab, "Pre-Processing")
        self.__rightContainer.addTab(self.__discoveryTab, "miRNA Discovery")
        self.__rightContainer.addTab(self.__predictTab, "Target Prediction")
        self.__rightContainer.addTab(self.__outputTab, "Output")

        # INITIALIZE CENTER CONTAINER

        self.__outputContainer = w.QTabWidget()
        self.__outputContainer.setStyleSheet("background-color: white;")
        self.__outputLayout = QVBoxLayout(self.__outputTab)
        self.__outputLayout.setAlignment(Qt.AlignTop)
        self.__outputLayout.setContentsMargins(0,0,0,0)
        self.__outputLayout.setSpacing(0)
        self.__outputContainer.setTabsClosable(True)
        self.__outputContainer.tabCloseRequested.connect(self.__closeCenterTab)
        #
        # # INITIALIZE CENTER VERTICLE CONTAINER
        # self.__centerVContainer = w.QVBoxLayout()
        # self.__centerVContainer.addChildWidget(self.__outputContainer)



    def __initLayout__(self):
        layout = w.QHBoxLayout(self.__centralContainer)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(1)
        layout.addWidget(self.__leftContainer)
        layout.addWidget(self.__rightContainer)
        # self.__outputTab.setLayout(self.__centerVContainer)
        self.__outputLayout.addWidget(self.__outputContainer)


    #TODO Working on here
    def __initList__(self):

        self.__leftVLayout = QVBoxLayout(self.__leftVContainer)
        self.__projectmanager = w.QTreeWidget()
        self.__projectmanager.setFocusPolicy(0)
        self.__projectmanager.header().close()
        self.__projectmanager.setTextElideMode(c.Qt.ElideNone)
        self.__projectmanager.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.__projectmanager.header().setSectionResizeMode(w.QHeaderView.ResizeToContents)
        self.__projectmanager.header().setStretchLastSection(False)
        self.__projectmanager.setSortingEnabled(True)
        self.__projectmanager.itemSelectionChanged.connect(self.__selectFile)
        self.__leftVLayout.addWidget(self.__projectmanager)
        self.__leftVLayout.setContentsMargins(0,0,0,0)
        self.__leftVLayout.setAlignment(Qt.AlignTop)

        self.__leftVContainer.setLayout(self.__leftVLayout)

        # # #Test Add Item
        # par = w.QTreeWidgetItem(self.__projectmanager, ["Folder1"])
        # self.__projectmanager.addTopLevelItem(par)
        # chi = w.QTreeWidgetItem(par, ["File1.fasdfasdfasdfasta".format(1)])
        # self.__projectmanager.addTopLevelItem(chi)
        # par.addChild(chi)
        # test = w.QTreeWidgetItem(chi, ["File2asdfasdfasd.fasta".format(1)])
        # self.__projectmanager.addTopLevelItem(test)
        # par.addChild(test)

        self.__projectmanager.doubleClicked.connect(self.__DoubleClickTreeItem)

    #TODO THIS ONE IS USABLE
    def __DoubleClickTreeItem(self, index):
        if(DEBUGGING):
            print("Type of Index"+str(type(index)))
            print("Double Click: " + str(self.__outputContainer.count()), end="")
            print(index.data())
        if(index.data() == self.__projectUtility.getProjectName()): #CHECK IF USER DOUBLE CLICK THE PROJECT NAME
            return

        item = self.__projectmanager.findItems(index.data(), c.Qt.MatchExactly | c.Qt.MatchRecursive)
        index = item[0]

        if(isFolder(index.getFilePath())):
            return False

        #Check if the file is already open
        if(self.__outputContainer.count() is 0):
            self.__rightContainer.setCurrentIndex(OUTPUT_TAB_ID)
            self.__outputContainer.addTab(FileViewer(index.getFilePath(), self.__outputContainer), index.getName())
            return

        for i in range (0,self.__outputContainer.count() ):
            if(self.__outputContainer.widget(i).getFile() == index.getFilePath()):
                self.__rightContainer.setCurrentIndex(OUTPUT_TAB_ID)
                self.__outputContainer.setCurrentIndex(i)
                return

        self.__outputContainer.addTab(FileViewer(index.getFilePath(), self.__outputContainer), index.getName())
        self.__rightContainer.setCurrentIndex(OUTPUT_TAB_ID)
        self.__outputContainer.setCurrentIndex(self.__outputContainer.count()-1)

    #TODO THIS ONE DOING FINE
    def __closeCenterTab(self, index):
        print("Index : " + str(index))
        if( self.__outputContainer.widget(index).isUnsaved() ):
            print("All unsaved data will be loss. ")
        else:
            print("You are fine")
        self.__outputContainer.removeTab(index)

    def __createProject(self):
        path = w.QFileDialog.getSaveFileName(self, "Select Directory")
        if(len(path[0]) <= 0):
            return
        name = getFileName(path[0])
        self.__projectUtility.createProject(path[0][0:len(path[0])-len(name)], name)
        print(self.__projectUtility.getProjectName())
        print(self.__projectUtility.getDirectory())

        self.__initProjectManager()
        self.__toggleWidget()

    def __openProject(self):
        path = str(w.QFileDialog.getOpenFileUrl(self, "Select Project", "/", self.tr("Project file (*.pmi)")))

        lis = path.split("'")
        path = lis[1][7:len(lis[1]):]
        if(len(path) <= 0):
            if(DEBUGGING):
                print("No file selected")
            return

        print("Path : "+path)
        self.__projectUtility.openProject(path)

        if(DEBUGGING):
            print("Open project: project name: "+self.__projectUtility.getProjectName())
        self.__preTab.setInitialID(self.__projectUtility.getInitialID()[0])
        self.__discoveryTab.setInitialID(self.__projectUtility.getInitialID()[1])
        self.__predictTab.setInitialID(self.__projectUtility.getInitialID()[2])
        self.__initProjectManager()
        self.__toggleWidget()

        if(DEBUGGING):
            print("Open project: project directory: "+self.__projectUtility.getDirectory())

    def __closeProject(self):
        print("Close Project")
        self.__initAttribute__()
        self.__initUI__()
        self.__toggleWidget()
        self.__isOpenProject = False

    def __addFileTriggered(self):
        path = str(w.QFileDialog.getOpenFileName(self, "Select File"))

        if(len(path) == 0):
            return

        lis = path.split("'")
        ismove = QMessageBox.question(self, "Message", "Do you want to move selected file to filelist folder in project directory ?", QMessageBox.Yes , QMessageBox.No)
        if(ismove == QMessageBox.Yes):
            cmd = "cp "+lis[1]+" "+self.__projectUtility.getDirectory()+"file_list/"+getFileName(lis[1])
            os.system(cmd)
            lis = self.__projectUtility.getDirectory()+"file_list/"+getFileName(lis[1])

        self.__projectUtility.addFile(lis)
        self.__projectUtility.saveProject()
        if(DEBUGGING):
            print(lis)
            print("addFileTriggered : File List : ", end = '')
            print(self.__projectUtility.getFileList())
        previousItem = self.__projectmanager.findItems(self.__projectUtility.getProjectName(), c.Qt.MatchRecursive | c.Qt.MatchExactly)[0]
        dirlist = getDirectoryList(lis)
        startindex = 0
        for i in range(0, len(dirlist)):
            if(dirlist[i] == self.__projectUtility.getProjectName()):
                startindex = i+1
                break
            elif(dirlist[i] == "file_list"):
                startindex = i
                break
        for i in range(startindex, len(dirlist)):
            item = self.__projectmanager.findItems(dirlist[i], c.Qt.MatchRecursive | c.Qt.MatchExactly)
            if(len(item) == 0):
                i = mTreeWidgetItem(previousItem, [dirlist[i]], '', FOLDER)
                previousItem = i
            else:
                previousItem = item[0]


        i = mTreeWidgetItem(previousItem, [getFileName(lis)], lis[0:len(lis) - len(getFileName(lis)):], FILE )
        self.__projectmanager.addTopLevelItem(i)

    def __initProjectManager(self):
        self.__projectmanager.clear()

        proj = mTreeWidgetItem(self.__projectmanager, [self.__projectUtility.getProjectName()], '', PROJECT)
        self.__projectmanager.addTopLevelItem(proj)
        a = self.__projectUtility.getFileList()
        for i in getFileList(self.__projectUtility.getDirectory()):
            if(i not in a):
                a.append(i)

        for i in a:
            if(len(self.__projectmanager.findItems(getFileName(i), c.Qt.MatchRecursive | c.Qt.MatchExactly) ) > 0):
                continue

            previousItem = self.__projectmanager.findItems(self.__projectUtility.getProjectName(), c.Qt.MatchRecursive | c.Qt.MatchExactly)[0]
            dirlist = getDirectoryList(i)
            startindex = 0
            for j in range(0, len(dirlist)):
                if(dirlist[j] == self.__projectUtility.getProjectName()):
                    startindex = j+1
                    break
                elif(dirlist[j] == "file_list"):
                    startindex = j
                    break
                elif(j == len(dirlist)-1):
                    startindex = len(dirlist)
            for j in range(startindex, len(dirlist)):
                item = self.__projectmanager.findItems(dirlist[j], c.Qt.MatchRecursive | c.Qt.MatchExactly)
                if(len(item) == 0):
                    item = mTreeWidgetItem(previousItem, [dirlist[j]], '', FOLDER)
                    previousItem = item
                else:
                    previousItem = item[0]

            inItem = mTreeWidgetItem(previousItem, [getFileName(i)], i[0:len(i)-len(getFileName(i))], FILE)

    def __toggleWidget(self):
        self.__addFileAction.setDisabled(self.__isOpenProject)
        self.__closeProjectAction.setDisabled(self.__isOpenProject)
        self.__preTab.setWidgetEnable(self.__isOpenProject)

    def __selectFile(self):
        index = self.__projectmanager.selectedIndexes()
        if(len(index) > 0):
            index = index[0]
            item = self.__projectmanager.itemFromIndex(index)
            if(item.childCount() == 0):
                self.__removeFileAction.setEnabled(True)
            elif(item.childCount() != 0):
                self.__removeFileAction.setEnabled(False)


    def __removeFileTriggered(self):
        index = self.__projectmanager.selectedIndexes()[0]
        if(DEBUGGING):
            print("Remove File : "+index.data())
        item = self.__projectmanager.itemFromIndex(index)
        item.parent().removeChild(item)

    def checkBoxChanged(self, param):
        self.__preTab.setAutoWorkflow(param)
        self.__predictTab.setAutoWorkflow(param)
        self.__discoveryTab.setAutoWorkflow(param)

    def updateProject(self):
        self.__initProjectManager()
        self.__projectUtility.setInitialID([self.__preTab.getInitialID(), self.__discoveryTab.getInitialID(), self.__predictTab.getInitialID()])
        self.__projectUtility.saveProject()

    def runWorkflow(self):
        if(DEBUGGING):
            print("runWorkflow")
        toolqueue = self.__preTab.getToolQueue()
        toolqueue += self.__discoveryTab.getToolQueue()
        toolqueue += self.__predictTab.getToolQueue()
        for i in toolqueue:
            i.runCommand()
        #TODO INIT PROGRESS DIALOG

        #TODO COLLECT ALL COMMAND

        #TODO SEND COMMANDS TO DIALOG

        #LET DIALOG DO THE JOB

    def requestExpectedOutput(self, wf, id, q):
        toolQueue = q
        lis = []
        if(DEBUGGING):
            print("toolQueue : ", end='')
            print(toolQueue)

        if(toolQueue == None):
            return
        for i in toolQueue:
            if(i.getWorkflow() > wf):
                break
            if(i.getID() >= id):
                continue
            lis += i.getExpectedOutput()
        return lis
