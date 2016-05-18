import pykd

class ThreadInfo(object):

    def __init__(self, targetId, processId, thread):
        self.tid = thread.systemID
        self.targetId = targetId
        self.processId = processId
        self.id = thread.id
        self.isCurrent = thread.isCurrent()
        self.ip = pykd.findSymbol(thread.ip)

class ProcessInfo(object):

    def __init__(self, targetId, process):
        self.exeName = process.exeName
        self.pid = process.systemID
        self.id = process.id
        self.targetId = targetId
        self.isCurrent = process.isCurrent()
        self.threads = [ ThreadInfo(targetId, process.id, process.getThread(i)) for i in xrange(process.getNumberThreads()) ]

class TargetInfo(object):

    def __init__(self, target):
        self.desc = target.desc
        self.id = target.id
        self.isCurrent = target.isCurrent()
        if not target.isKernelDebugging():
            self.processes = [ ProcessInfo(target.id, target.getProcess(i)) for i in xrange(target.getNumberProcesses()) ]

def getProcessList(targetId):
    target = pykd.targetSystem.getSystemById(targetId)

def getTargetsList():
    return [ TargetInfo(pykd.targetSystem(i)) for i in xrange( pykd.targetSystem.getNumber()) ]

def setCurrentThread(targetId, processId, threadId):
    pykd.targetSystem.getSystemById(targetId).getProcessById(processId).getThreadById(threadId).setCurrent()







































#class ProcessesSnapshot(object):

#    def __init__(self, currentProcess, currentThread, processList):
#        self.currentProcessID = currentProcess
#        self.currentThreadID = currentThread
#        self.processList = processList

#class ProcessInfo(object):
    
#    def __init__(self, pid, exeName, threadList, breakpointList):
#        self.pid = pid
#        self.exeName = exeName
#        self.threadList = threadList
#        self.breakpointList = breakpointList

#def getProcessThreadList():

#    procLst = []

#    currentProcess = pykd.targetProcess.getCurrent()
#    currentThread =  currentProcess.currentThread()

#    for procIndex in xrange(pykd.targetProcess.getNumber()):
#        process = pykd.targetProcess.getProcess(procIndex)
#        threadLst = []
#        breakpointLst = []
#        for threadIndex in xrange(process.getNumberThreads()):
#            thread = process.thread(threadIndex)
#            threadLst.append( (thread.systemID,) )
#        #uncomment after pykd fixed
#        #for bpIndex in xrange(process.getNumberBreakpoints()):
#        #    bp = process.breakpoint(bpIndex)
#        #    breakpointLst.append( bp.getOffset() )
#        procLst.append( ProcessInfo(process.systemID, process.exeName, threadLst, breakpointLst) )

#    return ProcessesSnapshot(currentProcess.systemID, currentThread.systemID, procLst )

#def setCurrentThread(pid, tid):

#    for procIndex in xrange(pykd.targetProcess.getNumber()):
#        process = pykd.targetProcess.getProcess(procIndex)
#        if process.systemID != pid:
#            continue

#        for threadIndex in xrange(process.getNumberThreads()):
#            thread = process.thread(threadIndex)
#            if thread.systemID == tid:
#                thread.setCurrent()
#                break
#        return

