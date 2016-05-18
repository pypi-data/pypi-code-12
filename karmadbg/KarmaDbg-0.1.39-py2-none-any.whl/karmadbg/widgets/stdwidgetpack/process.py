
from PySide.QtGui import QTreeView, QStandardItemModel, QStandardItem
from PySide.QtCore import Qt, QMutex

from karmadbg.uicore.basewidgets import *
from karmadbg.uicore.async import *
from karmadbg.uicore.dbgclient import DebugAsyncCall

import karmadbg.scripts.proclist as proclist


class ThreadItem(QStandardItem):

    def __init__(self, threadInfo, uimanager):
        super(ThreadItem,self).__init__("Tid: %5x   %s" % (threadInfo.tid, threadInfo.ip))
        self.id = threadInfo.id
        self.processId = threadInfo.processId
        self.targetId = threadInfo.targetId
        self.uimanager = uimanager
        self.setEditable(False)

    @async
    def update(self, threadInfo):
        font = self.font()
        font.setBold(threadInfo.isCurrent)
        self.setFont(font)
        raise StopIteration

class ThreadRootItem(QStandardItem):

    def __init__(self, uimanager):
        super(ThreadRootItem,self).__init__("Threads: 0")
        self.uimanager = uimanager
        self.setEditable(False)

    @async
    def update(self, threadsList):

        self.setRowCount(0)

        for thread in threadsList:
            threadItem = ThreadItem(thread, self.uimanager)
            self.appendRow(threadItem)
            yield( self.uimanager.debugClient.callFunctionAsync(threadItem.update, thread ))

        self.setText("Threads: %d" % len(threadsList))

        raise StopIteration


class ProcessItem(QStandardItem):
    def __init__(self, processInfo, uimanager):
        super(ProcessItem,self).__init__("Pid: %x (%s)" % (processInfo.pid, processInfo.exeName) )
        self.id = processInfo.id
        self.uimanager = uimanager
        self.threadRoot = ThreadRootItem(self.uimanager)
        self.appendRow(self.threadRoot)
        self.setEditable(False)

    @async
    def update(self, processInfo):

        if not self.threadRoot:
            raise StopIteration

        yield ( self.uimanager.debugClient.callFunctionAsync(self.threadRoot.update, processInfo.threads) )

        font = self.font()
        font.setBold(processInfo.isCurrent)
        self.setFont(font)

        raise StopIteration

class ProcessRootItem(QStandardItem):

    def __init__(self, uimanager):
        super(ProcessRootItem,self).__init__("Processes: 0")
        self.uimanager = uimanager
        self.setEditable(False)

    @async
    def update(self, processesList):

        self.setRowCount(0)

        for process in processesList:
            processItem = ProcessItem(process, self.uimanager)
            self.appendRow(processItem)
            yield( self.uimanager.debugClient.callFunctionAsync(processItem.update, process ))

        self.setText("Processes: %d" % len(processesList))

        raise StopIteration

class TargetItem(QStandardItem):

    def __init__(self, targetInfo, uimanager):
        super(TargetItem,self).__init__(targetInfo.desc)
        self.uimanager = uimanager
        self.desc = targetInfo.desc
        self.id = targetInfo.id
        self.processRoot = None
        if hasattr(targetInfo, "processes"):
            self.processRoot = ProcessRootItem(self.uimanager)
            self.appendRow(self.processRoot)
        self.setEditable(False)

    @async
    def update(self,targetInfo):

        if not self.processRoot:
            raise StopIteration

        yield ( self.uimanager.debugClient.callFunctionAsync(self.processRoot.update, targetInfo.processes) )

        font = self.font()
        font.setBold(targetInfo.isCurrent)
        self.setFont(font)

        raise StopIteration

class ProcessExplorerWidget(NativeDataViewWidget):

    def __init__(self, widgetSettings, uimanager):
        super(ProcessExplorerWidget,self).__init__(uimanager)
        self.uimanager = uimanager

        self.treeView = QTreeView()
        self.treeView.setHeaderHidden(True)

        self.treeModel = QStandardItemModel(0,1)
        self.treeView.setModel(self.treeModel)

        self.treeView.setSelectionMode(QTreeView.NoSelection)
        self.treeView.setAllColumnsShowFocus(False)
        self.treeView.doubleClicked.connect(self.onItemDblClick)

        self.setWidget(self.treeView)

        self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea, self)
        self.updateMutex = UpdateMutex()

    def dataUnavailable(self):
        self.treeModel.clear()
       
    @async
    def dataUpdate(self):

        yield( self.uimanager.debugClient.lockMutexAsync(self.updateMutex) )

        with AutoQMutex(self.updateMutex) as autoMutex:

            self.treeModel.clear()

            targetsList = yield( self.uimanager.debugClient.callServerAsync(proclist.getTargetsList) )

            for target in targetsList:
                targetItem = TargetItem(target, self.uimanager)
                self.treeModel.appendRow(targetItem)
                yield( self.uimanager.debugClient.callFunctionAsync(targetItem.update, target ))

    @async
    def onItemDblClick(self, modelIndex):

        yield( self.uimanager.debugClient.lockMutexAsync(self.updateMutex) )

        with AutoQMutex(self.updateMutex) as autoMutex:

            item = self.treeModel.itemFromIndex(modelIndex)
            if type(item) is ThreadItem:
                self.uimanager.debugClient.callServer(proclist.setCurrentThread, item.targetId, item.processId, item.id )

