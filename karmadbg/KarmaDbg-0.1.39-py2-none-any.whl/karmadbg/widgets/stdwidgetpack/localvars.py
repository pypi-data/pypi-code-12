from PySide.QtGui import *
from PySide.QtCore import *
from karmadbg.uicore.async import async
from karmadbg.uicore.basewidgets import NativeDataViewWidget, AutoQMutex

from karmadbg.dbgcore.varprint import getLocalsCount, getLocal, getTypedVar

class VarItem(QStandardItem):

    def __init__(self, name, varName, subkey):
        super(VarItem,self).__init__(name)
        self.name = name
        self.varName = varName
        self.varSubKey = subkey
        #self.fullName = "%s.%s" % (parentName, varName)

class LocalVarsWidget(NativeDataViewWidget):

    def __init__(self, widgetSettings, uimanager):
        super(LocalVarsWidget, self).__init__(uimanager)
        self.uimanager = uimanager

        self.treeModel = QStandardItemModel(0,4)
        self.buildHeader()

        self.treeView = QTreeView()
        self.treeView.setModel(self.treeModel)

        self.treeView.expanded.connect(self.onExpandItem)

        self.setWidget(self.treeView)
        self.setWindowTitle(widgetSettings.title)
        self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea, self)
        self.updateMutex = QMutex()

    def dataUnavailable(self):
        self.treeModel.clear()
        self.buildHeader()

    def buildHeader(self):
        for section, title in { 0 : "Name", 1 : "Value", 2 : "Type", 3 : "Location"}.items():
            self.treeModel.setHorizontalHeaderItem( section, QStandardItem(title) )


    @async
    def dataUpdate(self):

        yield( self.uimanager.debugClient.lockMutexAsync(self.updateMutex) )

        with AutoQMutex(self.updateMutex) as autoMutex:

            self.treeModel.clear()
            self.buildHeader()

            localsCount = yield( self.uimanager.debugClient.callServerAsync(getLocalsCount) )

            for localIndex in xrange(localsCount):
                varName, varType, varLocation, shortValue, subitems = yield( self.uimanager.debugClient.callServerAsync(getLocal, localIndex, () ) )
                treeItem = VarItem(varName, localIndex, ())
                self.treeModel.appendRow( [treeItem, QStandardItem(shortValue), QStandardItem(varType), QStandardItem(varLocation)] )

                for subitemName, subitemKey in subitems:
                    subItemRow = [ VarItem(subitemName, localIndex, (subitemKey,) ) ]
                    treeItem.appendRow(subItemRow)

            self.treeView.resizeColumnToContents(0) 

    @async
    def onExpandItem(self, modelIndex):

        yield( self.uimanager.debugClient.lockMutexAsync(self.updateMutex) )

        with AutoQMutex(self.updateMutex) as autoMutex:

            expandedItem = self.treeModel.itemFromIndex(modelIndex)
            for r in range(expandedItem.rowCount()):
                childItem = expandedItem.child(r)
                varName, varType, varLocation, shortValue, subitems = yield( self.uimanager.debugClient.callServerAsync(getLocal, childItem.varName, childItem.varSubKey) )
                expandedItem.setChild( r, 1, QStandardItem(shortValue) )
                expandedItem.setChild( r, 2, QStandardItem(varType) )
                expandedItem.setChild( r, 3, QStandardItem(varLocation) )

                if not childItem.hasChildren():
                    for subitemName, subItemkey in subitems:
                      subItemRow = [ VarItem(subitemName, childItem.varName, childItem.varSubKey + (subItemkey,)) ]
                      childItem.appendRow(subItemRow)

            self.treeView.resizeColumnToContents(0)


class WatchWidget(NativeDataViewWidget):
    def __init__(self, widgetSettings, uimanager):
        super(WatchWidget, self).__init__(uimanager)
        self.uimanager = uimanager

        self.treeModel = QStandardItemModel(0,4)
        self.buildHeader()

        self.treeModel.itemChanged.connect(self.onItemChanged)

        self.treeView = QTreeView()
        self.treeView.setModel(self.treeModel)
        self.treeView.expanded.connect(self.onExpandItem)

        self.emptyItem = QStandardItem("")
        self.treeModel.appendRow(self.emptyItem)

        self.setWidget(self.treeView)
        self.setWindowTitle(widgetSettings.title)
        self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea, self)
        self.updateMutex = QMutex()
        
    def onItemChanged(self,item):
        if item is self.emptyItem:
            self.emptyItem = QStandardItem("")
            self.treeModel.appendRow(self.emptyItem)
            self.dataUpdate()
        elif item.column() == 0 and item.text() == "":
            self.treeModel.removeRow(item.row())

    def dataUnavailable(self):
        pass

    def buildHeader(self):
        for section, title in { 0 : "Name", 1 : "Value", 2 : "Type", 3 : "Location"}.items():
            self.treeModel.setHorizontalHeaderItem( section, QStandardItem(title) )

    @async
    def dataUpdate(self):

        yield( self.uimanager.debugClient.lockMutexAsync(self.updateMutex) )

        with AutoQMutex(self.updateMutex) as autoMutex:

            for r in range(self.treeModel.rowCount() - 1):
                treeItem = self.treeModel.item(r)
                varName = treeItem.text()
                varName, varType, varLocation, shortValue, subitems = yield( self.uimanager.debugClient.callServerAsync(getTypedVar, varName, () ) )
                treeItem = VarItem(varName, varName, ())
                self.treeModel.setItem( r, 0, treeItem )
                self.treeModel.setItem( r, 1, QStandardItem(shortValue) )
                self.treeModel.setItem( r, 2, QStandardItem(varType) )
                self.treeModel.setItem( r, 3, QStandardItem(varLocation) )

                for subitemName, subitemKey in subitems:
                    subItemRow = [ VarItem(subitemName, varName, (subitemKey,) ) ]
                    treeItem.appendRow(subItemRow)

            self.treeView.resizeColumnToContents(0) 

    @async
    def onExpandItem(self, modelIndex):

        yield( self.uimanager.debugClient.lockMutexAsync(self.updateMutex) )

        with AutoQMutex(self.updateMutex) as autoMutex:

            expandedItem = self.treeModel.itemFromIndex(modelIndex)
            for r in range(expandedItem.rowCount()):
                childItem = expandedItem.child(r)
                varName, varType, varLocation, shortValue, subitems = yield( self.uimanager.debugClient.callServerAsync(getTypedVar, childItem.varName, childItem.varSubKey) )
                expandedItem.setChild( r, 1, QStandardItem(shortValue) )
                expandedItem.setChild( r, 2, QStandardItem(varType) )
                expandedItem.setChild( r, 3, QStandardItem(varLocation) )

                if not childItem.hasChildren():
                    for subitemName, subItemkey in subitems:
                      subItemRow = [ VarItem(subitemName, childItem.varName, childItem.varSubKey + (subItemkey,)) ]
                      childItem.appendRow(subItemRow)

            self.treeView.resizeColumnToContents(0)
 