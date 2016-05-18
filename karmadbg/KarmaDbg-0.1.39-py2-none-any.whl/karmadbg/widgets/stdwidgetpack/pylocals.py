
from PySide.QtCore import Qt, QMutex
from PySide.QtGui import QStandardItemModel, QStandardItem, QTreeView, QHeaderView

from karmadbg.uicore.async import async
from karmadbg.uicore.basewidgets import PythonDataViewWidget

class VarItem(QStandardItem):

    def __init__(self, name, subkey):
        super(VarItem,self).__init__(name)
        self.name = name
        self.subkey = subkey

class PythonLocalsWidget(PythonDataViewWidget):

    def __init__(self, widgetSettings, uimanager): 
        super(PythonLocalsWidget,self).__init__(uimanager)

        self.uimanager = uimanager

        self.treeModel = QStandardItemModel(0,2)

        self.treeView = QTreeView()
        self.treeView.setModel(self.treeModel)
        self.treeView.expanded.connect(self.onExpandItem)

        self.treeView.header().setDefaultSectionSize(120)
        self.treeView.header().setResizeMode(0, QHeaderView.Interactive)
        self.treeView.header().setResizeMode(1, QHeaderView.Interactive)
        self.treeView.header().setResizeMode(2, QHeaderView.Stretch)

        self.treeView.setEditTriggers(QTreeView.NoEditTriggers)
        self.treeView.setSelectionMode(QTreeView.NoSelection)

        self.buildHeader()

        self.setWidget(self.treeView)

        self.uimanager.debugClient.pythonStackFrameChanged.connect(self.dataUpdate)

        self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea, self)

        self.updateMutex = QMutex()

    def dataUnavailable(self):
        self.treeModel.setRowCount(0)

    def buildHeader(self):
        for section, title in { 0 : "Name", 1 : "Type", 2 : "Value"}.items():
             self.treeModel.setHorizontalHeaderItem(section, QStandardItem(title))

    @async
    def dataUpdate(self):

        yield( self.uimanager.debugClient.lockMutexAsync(self.updateMutex) )

        try :

            self.treeModel.setRowCount(0)
            localvars= yield( self.uimanager.debugClient.getPythonLocalsAsync( () ) )

            for name, key, value, typename, subitems in localvars:
                rootItem = VarItem(name, (key,))
                row = [rootItem, QStandardItem(typename), QStandardItem(self.valueToStr(value))]
                self.treeModel.appendRow(row)
                for subitemName, subitemKey in subitems:
                    subitem = QStandardItem(subitemName)
                    rootItem.appendRow(subitem)
            self.treeView.resizeColumnToContents(0)
            self.treeView.setColumnWidth( 0, self.treeView.columnWidth(0) + 10 )

        except Exception as ex:
            pass

        self.updateMutex.unlock()

    @async
    def onExpandItem(self, modelIndex):

        yield( self.uimanager.debugClient.lockMutexAsync(self.updateMutex) )

        try :

            expandedItem = self.treeModel.itemFromIndex(modelIndex)
            subvars = yield(self.uimanager.debugClient.getPythonLocalsAsync(expandedItem.subkey))
            for r in range(expandedItem.rowCount()):
                childItem = expandedItem.child(r)
                name, key, value, typename, subitems = subvars[r]
                var = VarItem(name, expandedItem.subkey + (key,))
                expandedItem.setChild( r, 0, var)
                expandedItem.setChild( r, 1, QStandardItem(typename) )
                expandedItem.setChild( r, 2, QStandardItem(self.valueToStr(value)))
                for subitemName, subitemKey in subitems:
                    subitem = QStandardItem(subitemName)
                    var.appendRow(subitem)

            self.treeView.resizeColumnToContents(0)
            self.treeView.setColumnWidth( 0, self.treeView.columnWidth(0) + 10 )

        except Exception as ex:
            pass

        self.updateMutex.unlock()

    def valueToStr(self, value):
        s =  str(value)
        s = s.replace("\n", "\\n")
        s = s.replace("\r", "\\r")
        s = s.replace("\t", "\\t")
        return s
 