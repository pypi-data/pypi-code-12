
from PySide.QtGui import *
from PySide.QtCore import *

from karmadbg.uicore.basewidgets import PythonDataViewWidget, NativeDataViewWidget
from karmadbg.uicore.async import async

class StackModel(QAbstractTableModel):
    def __init__(self, parent, uimanager):
        super(StackModel,self).__init__(parent)
        self.stackData = []
        self.uimanager = uimanager
        self.currentLine = 0

    def columnCount(self, parent):
        return 3

    def rowCount(self, parent):
        return len(self.stackData)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            if index.column()==0:
                return "%08x" % self.stackData[index.row()][0]  
            if index.column()==1:
                return "%08x" % self.stackData[index.row()][1]
            return self.stackData[index.row()][2]

        #if role == Qt.BackgroundColorRole:
        #    if index.row() == self.currentLine:
        #        return QBrush(QColor(Qt.blue))


    def headerData (self, section, orientation, role):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return { 0 : "SP", 1: "RET",  2 : "IP" }[section]
            if role == Qt.TextAlignmentRole:
                return Qt.AlignLeft

        if orientation==Qt.Vertical:
            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter

        return super(StackModel,self).headerData(section,orientation,role)

    def flags(self, index):
        return (Qt.ItemIsSelectable)|(Qt.ItemIsEnabled)


class StackWidget(NativeDataViewWidget):

    def __init__(self, widgetSettings, uimanager):
        super(StackWidget, self).__init__(uimanager)
        self.uimanager = uimanager
        self.stackView = QTableView(self)
        self.stackView.verticalHeader().hide()
        self.stackView.setShowGrid(False)
        self.stackView.setSelectionBehavior(QAbstractItemView.SelectRows);
           
        self.stackModel = StackModel(self,uimanager)
        self.stackView.setModel(self.stackModel)
        self.stackView.doubleClicked.connect(self.onDoubleClicked)

        self.setWindowTitle("Target Stack")
        self.setWidget(self.stackView)

        self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea, self)

    @async
    def dataUpdate(self):
        self.stackModel.stackData = yield (self.uimanager.debugClient.getStackTraceAsync())
        self.stackModel.reset()
        #self.stackView.selectRow(self.uimanager.debugClient.getCurrentFrame())
        self.stackView.resizeColumnsToContents()
        self.stackView.resizeRowsToContents()

    def dataUnavailable(self):
        self.stackModel.stackData = []
        self.stackModel.reset()

    def onDoubleClicked(self, index):
        self.stackModel.reset()
        self.stackView.selectRow(index.row())
        self.uimanager.debugClient.setCurrentFrame(index.row())


class PythonStackWidget(PythonDataViewWidget):

    def __init__(self, widgetSettings, uimanager): 
        super(PythonStackWidget,self).__init__(uimanager)
        self.uimanager = uimanager

        self.stackModel = QStandardItemModel(0,2)
        self.buildHeader()

        self.stackView = QTableView()
        self.stackView.setModel(self.stackModel)

        self.stackView.verticalHeader().hide()
        self.stackView.setShowGrid(False)
        self.stackView.setSelectionBehavior(QAbstractItemView.SelectRows);
        self.stackView.setEditTriggers(QTreeView.NoEditTriggers)
       
        self.stackView.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)
        self.stackView.horizontalHeader().setResizeMode(0, QHeaderView.ResizeToContents)

        self.stackView.setSelectionMode(QTreeView.NoSelection)
        self.stackView.setFocusPolicy(Qt.NoFocus)
        self.stackView.setWordWrap(False)
        
        self.stackView.doubleClicked.connect(self.onDoubleClicked)
        self.uimanager.debugClient.pythonStackFrameChanged.connect(self.dataUpdate)

        self.setWindowTitle("Python Stack")
        self.setWidget(self.stackView)
        self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea, self)

    def buildHeader(self):
        for section, title in { 0 : "Function", 1 : "Module"}.items():
            self.stackModel.setHorizontalHeaderItem( section, QStandardItem(title) )

    def dataUnavailable(self):
        self.stackModel.setRowCount(0)

    @async
    def dataUpdate(self):
        self.stackModel.setRowCount(0)
        stackTrace = yield( self.uimanager.debugClient.getPythonStackTraceAsync() )
        currentFrame = yield(self.uimanager.debugClient.getPythonCurrentFrameAsync())

        for frame in stackTrace:
            func, module, line = frame
            self.stackModel.appendRow( [QStandardItem(func), QStandardItem("%s ln %d" % (module, line) ) ] )

        self.stackView.setSelectionMode(QTreeView.SingleSelection)

        self.stackView.selectRow(currentFrame)
        self.stackView.setSelectionMode(QTreeView.NoSelection)
        self.stackView.resizeRowsToContents()

    def onDoubleClicked(self, index):
        self.stackView.setSelectionMode(QTreeView.SingleSelection)
        self.stackView.selectRow(index.row())
        self.stackView.setSelectionMode(QTreeView.NoSelection)
        self.uimanager.debugClient.setPythonCurrentFrame(index.row())
