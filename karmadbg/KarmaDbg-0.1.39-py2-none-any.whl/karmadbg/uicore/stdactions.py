
from PySide.QtGui import QFileDialog

def onQuitAction(uimanager, action):
    uimanager.quit()

def onOpenProcessAction(uimanager, action):

    dlg = uimanager.getDialog("OpenProcess")
    if dlg:
        processName = dlg.getProcessName()
    else:
        processName = QFileDialog().getOpenFileName()[0]

    if processName:
        cmd = "startProcess(r\"" +  processName + "\")"
        uimanager.callCommand(cmd)


def onOpenDumpAction(uimanager, action):

    dlg = uimanager.getDialog("OpenDump")
    if dlg:
        dumpName = dlg.getDumpName()
    else:
        dumpName = QFileDialog().getOpenFileName()[0]

    if dumpName:
        cmd = "loadDump(r\"" + dumpName + "\")"
        uimanager.callCommand(cmd)


def onGoAction(uimanager, action):
    uimanager.callCommand("g")

def onBreakAction(uimanager, action):
    uimanager.debugClient.breakin()

def onNextAction(uimanager, action):
    uimanager.callCommand("t")

def onStepAction(uimanager, actionr):
    uimanager.callCommand("p")

def onStepOutAction(uimanager, action):
    uimanager.callCommand("gu")

def onDetachAction(uimanager, action):
    uimanager.callCommand("detachProcess()")

def onStopAction(uimanager, action):
    uimanager.callCommand("killProcess()")

def onCloseDumpAction(uimanager, action):
    uimanager.callCommand("closeDump()")

def onOpenAction(uimanager, action):
    dlg = uimanager.getDialog("OpenSource")
    if dlg:
        fileName = dlg.getFileName()
    else:
        fileName = QFileDialog().getOpenFileName()[0]

    if fileName:
        uimanager.showSourceFile(fileName)

def onStepSourceAction(uimanager, action):
    sourceMode = uimanager.debugClient.stepSourceMode
    uimanager.debugClient.setStepSourceMode(False)
        
        #not sourceMode)

def onSaveLayout(uimanager, action):
    uimanager.mainwnd.saveLayout(None)

def onSaveLayoutAsFile(uimanager, action):
    uimanager.mainwnd.saveLayoutAsFile()

def onLoadLayoutFromFile(uimanager, action):
    uimanager.mainwnd.loadLayoutFromFile()
