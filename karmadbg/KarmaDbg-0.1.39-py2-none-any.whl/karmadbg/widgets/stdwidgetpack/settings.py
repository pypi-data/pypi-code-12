
from PySide.QtGui import QDockWidget
from PySide.QtGui import QTreeView, QStandardItemModel, QStandardItem
from PySide.QtCore import Qt

from operator import attrgetter

class QReadOnlyItem(QStandardItem):
    def __init__(self, *args, **kwargs):
        super(QReadOnlyItem,self).__init__(*args, **kwargs)
        self.setEditable(False)

class SettingsWidget(QDockWidget):

    def __init__(self, widgetSettings, uimanager):
        super(SettingsWidget, self).__init__()
        self.uimanager = uimanager
        self.uimanager.mainwnd.addDockWidget(Qt.LeftDockWidgetArea,self)

        self.treeView = QTreeView()
        self.treeView.setHeaderHidden(True)
        self.treeModel = QStandardItemModel(0,1)
        self.treeModel.itemChanged.connect(self.onItemChanged)
        self.treeView.setModel(self.treeModel)

        self.loadModel()

        self.setWidget(self.treeView)

    def loadModel(self):
        self.loadMainWindow()
        self.loadWidgets()
        self.loadExt()
        self.treeView.resizeColumnToContents(0)
        self.treeView.setColumnWidth( 0, 250 ) 


    def loadWidgets(self):
        rootNode = QReadOnlyItem("Widgets")
        self.treeModel.appendRow( rootNode )

        for widgetSetting in sorted(self.uimanager.dbgSettings.widgets, key=attrgetter('name')):
            widgetRoot = QReadOnlyItem(widgetSetting.name)
            rootNode.appendRow(widgetRoot)
            widgetRoot.appendRow( [ QReadOnlyItem( "Module: " + widgetSetting.module) ] )
            widgetRoot.appendRow( [ QReadOnlyItem( "Class: " + widgetSetting.className) ] )
            if widgetSetting.title:
                widgetRoot.appendRow( [QReadOnlyItem("Title: " + widgetSetting.title) ] )

    def loadMainWindow(self):
        rootNode = QReadOnlyItem("Main Window")
        self.treeModel.appendRow( rootNode )

        rootNode.appendRow( [ QReadOnlyItem( "Title: " + self.uimanager.dbgSettings.mainWindow.title) ] )
        rootNode.appendRow( [ QReadOnlyItem( "Width: " + str(self.uimanager.dbgSettings.mainWindow.width)) ] )
        rootNode.appendRow( [ QReadOnlyItem( "Height: " + str(self.uimanager.dbgSettings.mainWindow.height)) ] )

    def loadExt(self):
        rootNode = QReadOnlyItem("DbgEng Extensions")
        self.treeModel.appendRow( rootNode )

        for extSettings in self.uimanager.dbgSettings.dbgEngExtensions:
            extRoot = QReadOnlyItem(extSettings.path)
            extRoot.setColumnCount(2)
            extRoot.appendRow( [ QReadOnlyItem( "Startup: " + str(extSettings.startup)) ] )
            rootNode.appendRow(extRoot)

    def onItemChanged(self, item):
        pass


    
