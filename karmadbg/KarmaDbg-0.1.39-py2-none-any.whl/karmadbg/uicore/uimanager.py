import sys
import os
import cgi

from PySide.QtCore import QObject, Signal, QThreadPool, QRunnable, QMutex, QWaitCondition, QSettings
from PySide.QtGui import QMainWindow,  QAction, QKeySequence, QShortcut, QFileDialog

from karmadbg.dbgcore.settings import DbgSettings
from karmadbg.uicore.defaultstyle import defaultStyle, defaultCss
from karmadbg.uicore.dbgclient import DebugClient
from karmadbg.uicore.async import async

UI_VERSION = 1  #used as gui layout version

class UIManager(QObject):

    textOutputted = Signal(str)
    textFormattedOutputted  = Signal(str)
    textInputRequired = Signal()
    debugOutputRequired = Signal(str)
    readyForCommand = Signal()
    commandInProgress = Signal()
    commandProvided = Signal(str)
    showSourceRequired = Signal(str, int)

    def __init__(self, app):
        super(UIManager,self).__init__()

        self.app = app
        
        import karmadbg
        projdir =  os.path.dirname(karmadbg.__file__)
        defaultSettingFile =  os.path.join(projdir, "settings", "default.xml")

        homedir = os.getenv("KARMADBG_CONFIG", None)
        if not homedir :
            projectSettingFile =  os.path.join(projdir, "default.xml")
            if os.path.exists(projectSettingFile) :
                homedir = projdir

        if not homedir :
            homedir = os.path.join(  os.path.expandvars("$USERPROFILE"), ".karmadbg")

        userSettingsFile = os.path.join(homedir, "default.xml")

        self.dbgSettings = DbgSettings()
        self.dbgSettings.loadDefaultSettings(defaultSettingFile)
        self.dbgSettings.loadCustomSettings(userSettingsFile)

        # application stylesheet
        self.app.setStyleSheet(defaultStyle)
        if self.dbgSettings.style:
            if self.dbgSettings.style.fileName:
                if os.path.isabs(self.dbgSettings.style.fileName):
                    fileName = self.dbgSettings.style.fileName
                else:
                    filename = r"file:///" + os.path.join( projdir, self.dbgSettings.style.fileName )
                self.app.setStyleSheet(filename);

        
        self.docCss = defaultCss
        try:
            if self.dbgSettings.doccss:
                if self.dbgSettings.doccss.fileName:
                    if os.path.isabs(self.dbgSettings.doccss.fileName):
                        fileName = self.dbgSettings.doccss.fileName
                    else:
                        filename = os.path.join( projdir, self.dbgSettings.doccss.fileName )
                    with open(filename) as cssfile:
                        self.docCss = reduce( lambda x,y: x + y, cssfile)
        except:
            pass

        # setup and start debug engine
        self.debugClient = DebugClient(self, self.dbgSettings)
        self.debugClient.outputPlainReady.connect(self.onOutputPlainReady)
        self.debugClient.outputFormattedReady.connect(self.onOutputFormattedReady)

        # setup UI elements
        self.mainwnd = MainForm(self.dbgSettings)
        self.actions = ActionManager(self.dbgSettings, self)
        self.widgets = WidgetManager(self.dbgSettings, self)
        self.dialogs = DialogManager(self.dbgSettings, self)
        self.mainMenu = getMainMenuManager(self.dbgSettings.mainMenu, self)

        self.mainwnd.restoreLayout(None)

        sys.stdout = self

        #setup application event handler
        self.app.aboutToQuit.connect(self.onQuit)
        self.app.focusChanged.connect(self.onFocusChanged)

        self.debugClient.start()

        #setup and start command loop
        self.commandThread = QThreadPool()
        self.commandThread.setMaxThreadCount(1)
        self.dbgLoop = self.__debugLoop()
        self.dbgLoop.next()
        self.inputWaiter = None
        self.commandProvided.connect(self.onCommand)

        print "KarmaDbg UI client. Version %s" % karmadbg.__version__ 
        print "load config from ", userSettingsFile

        #show main window
        self.mainwnd.show()

    def onOutputPlainReady(self):
        str = self.debugClient.getPlainOutput()
        self.textOutputted.emit(str)

    def onOutputFormattedReady(self):
        str = self.debugClient.getFormattedOutput()
        self.textFormattedOutputted.emit(str)

    def textOutput(self, str):
        self.textOutputted.emit(str)
        self.textFormattedOutputted.emit(str)

    def debugOutput(self,str):
        self.debugOutputRequired.emit(str)

    def textInput(self):
        self.textInputRequired.emit()
        self.inputWaiter = InputWaiterSync()
        str = self.inputWaiter.wait()
        self.inputWaiter = None
        return str

    def textInputComplete(self, str):
        self.textOutput(str+"\n")
        if str == "":
            str = "\n"
        if self.inputWaiter:
            self.inputWaiter.inputComplete(str)

    def callCommand(self, str):
        self.commandProvided.emit(str)

    def showSourceFile(self,fileName, lineno=0):
        self.showSourceRequired.emit(fileName, lineno)

    def onQuit(self):
        self.debugClient.stop()
        self.commandThread.waitForDone()

    def onFocusChanged(self, oldWidget, newWidget):
        findAction = self.getAction("FindAction")
        if findAction:
            findAction.setEnabled(hasattr(newWidget,"find"))

    def write(self,str):
        self.textOutput(str)

    def getWidget(self, name):
        if name in self.widgets:
            return self.widgets[name]

    def getDialog(self, name):
        if name in self.dialogs:
            return self.dialogs[name](self.dbgSettings,self)

    def getAction(self,name):
        if name in self.actions:
            return self.actions[name]

    def toggleWidget(self, name):
        widget = self.getWidget(name)
        if widget:
            widget.setVisible( widget.isVisible() == False )

    def showDialogModal(self,name):
        self.findTarget = self.app.focusWidget()
        dlg = self.getDialog(name)
        if dlg: dlg.exec_()

    def quit(self):
        self.mainwnd.close()

    def find(self, text, fromStart = False):
        if hasattr(self.findTarget, "find"):
            self.findTarget.find(text, fromStart)

    def __debugLoop(self):

         while True:

            # input required
            self.readyForCommand.emit()

            cmdStr = yield

            # ui command parser
            if self.uiCommand(cmdStr):
                self.debugClient.callServerCommand("")
                continue

            #command handling
            self.debugClient.callServerCommand(cmdStr)

    @async
    def onCommand(uimanager, commandStr):
        
        class CommandAsync(QRunnable):

            def run(self):
                uimanager.dbgLoop.send(commandStr)

        uimanager.commandInProgress.emit()
        prompt = yield( uimanager.debugClient.getPromptAsync() )
        uimanager.textOutput(prompt)

        #echo
        uimanager.textOutput(str = cgi.escape(commandStr)+"\n")
        uimanager.commandThread.start( CommandAsync() )

    def uiCommand(self, commandStr):

        if commandStr == "":
            return False

        tokens = commandStr.split()
        cmd = tokens[0]
        args = [] if len(tokens) < 2 else tokens[1:]
        if cmd== ".open":
            self.debugClient.openSourceCmd(args)
            return True

        return False

class MainForm(QMainWindow):

    def __init__(self, settings):
        super(MainForm, self).__init__(None)

        self.settings = settings

        self.resize(settings.mainWindow.width, settings.mainWindow.height)
        self.setWindowTitle(settings.mainWindow.title)
        self.setDockNestingEnabled(True)

        if settings.guilayout.fileName <> None or len(settings.guilayout.fileName) > 0 :
            self.guiSettings = QSettings(settings.guilayout.fileName, QSettings.IniFormat)
            if self.guiSettings.value("geometry") <> None :
                self.restoreGeometry(self.guiSettings.value("geometry"))
                self.restoreState(self.guiSettings.value("state"), UI_VERSION) 

    def closeEvent(self, event) :
        if self.settings.guilayout.saveOnClose == True :
            self.saveLayout(self.guiSettings)
        event.accept()

    def restoreLayout(self, guiSettings) :
        if guiSettings == None :
            guiSettings = self.guiSettings

        if guiSettings <> None :
            if guiSettings.value("geometry") <> None :
                self.restoreGeometry(guiSettings.value("geometry"))
                self.restoreState(guiSettings.value("state"), UI_VERSION) 

            for widget in self.children():
                if hasattr(widget, "restoreLayout") :
                    widget.restoreLayout(guiSettings)

    def saveLayout(self, guiSettings) :
        if guiSettings == None :
            guiSettings = self.guiSettings

        if guiSettings <> None :
            guiSettings.setValue("geometry", self.saveGeometry())
            guiSettings.setValue("state", self.saveState(UI_VERSION))
            for widget in self.children():
                if hasattr(widget, "saveLayout") :
                      widget.saveLayout(guiSettings)
            
            guiSettings.sync()

    def saveLayoutAsFile(self) :
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select file")
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setFilters([("Layout file (*.ini)")])
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dialog.setConfirmOverwrite(True)

        if dialog.exec_() :
            fileNames = dialog.selectedFiles()
            fileName = fileNames[0]
            guiSettings = QSettings(str(fileName), QSettings.IniFormat)
            self.saveLayout(guiSettings)
    
    def loadLayoutFromFile(self) :
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select file")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setFilters([("Layout file (*.ini)")])
        
        if dialog.exec_() :
            fileNames = dialog.selectedFiles()
            fileName = fileNames[0]
            guiSettings = QSettings(str(fileName), QSettings.IniFormat)
            restoreLayout(guiSettings)

def getMainMenuManager(dbgsettings,uimanager):
    module = __import__( dbgsettings.module, fromlist=[dbgsettings.className])
    classobj = getattr(module, dbgsettings.className)
    return classobj(dbgsettings, uimanager)

class WidgetManager(QObject) :

    def __init__(self, dbgsettings, uimanager):
        
        super(WidgetManager,self).__init__()

        self.uimanager = uimanager
        self.widgets = {}

        for widgetSetting in dbgsettings.widgets:
            self.widgets[ widgetSetting.name ] = self.constructWidget(widgetSetting)

    def constructWidget(self, widgetSettings):
        module = __import__( widgetSettings.module, fromlist=[widgetSettings.className])
        classobj = getattr(module, widgetSettings.className)
        obj = classobj(widgetSettings, self.uimanager)
        obj.behaviour = widgetSettings.behaviour
        obj.setObjectName(widgetSettings.name)

        if not widgetSettings.invisible:
            obj.setVisible(widgetSettings.visible)

        if hasattr(obj, "constructDone"): obj.constructDone()
        if widgetSettings.title:
            obj.setWindowTitle(widgetSettings.title)

        return obj

    def __getitem__(self,name):
        return self.widgets[name]

    def __contains__(self,name):
        return name in self.widgets

    def values(self):
        return self.widgets.values()


class DialogManager(QObject):

    def __init__(self, dbgsettings, uimanager):
        
        super(DialogManager,self).__init__()

        self.uimanager = uimanager
        self.dialogs = {}

        for dialogSetting in dbgsettings.dialogs:
            self.dialogs[ dialogSetting.name ] = self.constructDialog(dialogSetting)

    def constructDialog(self, dialogSetting):
        module = __import__( dialogSetting.module, fromlist=[dialogSetting.className])
        classobj = getattr(module, dialogSetting.className)
        return classobj

    def __getitem__(self,name):
        return self.dialogs[name]

    def __contains__(self,name):
        return name in self.dialogs

class ActionManager(QObject):

    def __init__(self,dbgsettings, uimanager):
        super(ActionManager, self).__init__()
        self.uimanager = uimanager
        self.actions = {}

        for actionSetting in dbgsettings.actions:
            self.actions[ actionSetting.name ] = self.constructAction(actionSetting)

    def __getitem__(self,name):
        if name in self.actions:
            return self.actions[name]
        return QAction(name,self.uimanager.mainwnd)

    def __contains__(self,name):
        return name in self.actions

    def constructAction(self,actionSetting):
        
        action = QAction(actionSetting.displayName,self.uimanager.mainwnd)
        if actionSetting.shortcut: 
            action.setShortcut(QKeySequence(actionSetting.shortcut))

        if actionSetting.module and actionSetting.funcName:
            module = __import__(actionSetting.module, fromlist=[actionSetting.funcName])
            funcobj = getattr(module, actionSetting.funcName)
            action.triggered.connect(lambda : funcobj(self.uimanager, action) )

        if actionSetting.toggleWidget:
            action.triggered.connect(lambda : self.uimanager.toggleWidget(actionSetting.toggleWidget))

        if actionSetting.showDialog:
            action.triggered.connect(lambda : self.uimanager.showDialog(actionSettings.showDialog))

        if actionSetting.showModal:
            action.triggered.connect(lambda : self.uimanager.showDialogModal(actionSetting.showModal))

        if actionSetting.checkable:
            action.setCheckable(True)

        return action

#class CommandManager(QObject):

#    def __init__(self, uimanager, dbgsettings):
#        super(QObject,self).__init__()
#        self.uimanager = uimanager
#        self.uimanager.commandProvided.connect(self.onCommand)

#    def start(self):
#        self.commandThread = QThreadPool()
#        self.commandThread.setMaxThreadCount(1)
#        self.dbgLoop = self.debugLoop()
#        self.dbgLoop.next()

#    def stop(self):
#        self.commandThread.waitForDone()

#    def onCommand(commandManager,commandStr):
        
#        class CommandAsync(QRunnable):
#            def run(self):
#                commandManager.dbgLoop.send(commandStr)

#        commandManager.commandThread.start( CommandAsync() )

#    def debugLoop(self):


#        while True:
#            # input required
#            self.uimanager.readyForCommand.emit()

#            cmdStr = yield

#            #echo
#            self.uimanager.textOutput(cmdStr+"\n")

#            # ui command parser

#            #command handling
#            self.uimanager.debugClient.callServerCommand(cmdStr)


class InputWaiterSync(QObject):

    def __init__(self):
        self.inputMutex = QMutex()
        self.inputCompleted = QWaitCondition()
        self.inputBuffer = ""
        self.inputMutex.lock()

    def inputComplete(self,str):
        self.inputMutex.lock()
        self.inputBuffer = str
        self.inputCompleted.wakeAll()
        self.inputMutex.unlock()
            
    def wait(self):
        self.inputCompleted.wait(self.inputMutex)
        self.inputMutex.unlock()
        return self.inputBuffer
