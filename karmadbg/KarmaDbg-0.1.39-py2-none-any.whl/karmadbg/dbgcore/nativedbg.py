from codeop import compile_command

import pykd
from pykd import *

from karmadbg.dbgcore.dbgdecl import *
from karmadbg.dbgcore.util import *

class EventMonitor(pykd.eventHandler):

    def __init__(self, debugServer):
        super(EventMonitor,self).__init__()
        self.eventHandler = debugServer.eventHandler
        self.debugServer = debugServer

    def onExecutionStatusChange(self, status):
        event = { 
            pykd.executionStatus.Go : TargetState(TargetState.TARGET_RUNNING),
            pykd.executionStatus.Break : TargetState(TargetState.TARGET_STOPPED),
            pykd.executionStatus.NoDebuggee : TargetState(TargetState.TARGET_DETACHED)
        }[status]

        if event.IsStopped:
            self.debugServer.frame = pykd.getFrame()

        self.eventHandler.onTargetStateChanged(event)

    def onCurrentThreadChange(self, threadId):
        if pykd.getExecutionStatus() == pykd.executionStatus.Break:
            self.debugServer.frame = pykd.getFrame()
            self.eventHandler.onTargetChangeCurrentThread()

    def onChangeLocalScope(self):
        if pykd.getExecutionStatus() == pykd.executionStatus.Break:
            frame = pykd.getFrame()
            self.debugServer.frame = frame
            self.eventHandler.onTargetChangeCurrentFrame( (frame.ip, frame.ret, frame.fp, frame.sp) )

    def onChangeSymbolPaths(self):
        self.eventHandler.onChangeSymbolPaths()

    def onChangeBreakpoints(self):
        self.eventHandler.onTargetChangeBreakpoints()

    def onDebugOutput(self, text):
        sys.stdout.write(text)

    def onStartInput(self):
        print 
        str = raw_input("input>")
        pykd.dinput(str)
    
class NativeDebugger(object):

    WINDBGPREFIX =  ['.', '!', '~', '?', '#', '|', ';', '$', '@']
    WINDBGCMD = [
        'a', 'ad', 'ah', 'al', 'as', 'aS',
        'ba', 'ba', 'bc', 'bd', 'be', 'bl', 'bp', 'bu', 'bm', 'br', 'bs', 'bsc', 
        'c',
        'd', 'da', 'db', 'dc', 'dd', 'dD', 'df', 'dp', 'dq', 'du', 'dw', 'dW', 'dyb', 'dyd', 
        'dda', 'ddp', 'ddu', 'dpp', 'dpu', 'dqa', 'dqp', 'dqu',  'dds', 'dps', 'dqs', 'dg', 'dl', 
        'ds', 'dS', 'dt', 'dv',
        'e', 'ea', 'eb', 'ed', 'eD', 'ef', 'ep', 'eq', 'eu', 'ew', 'eza', 'ezu',
        'f', 'fp',
        'g', 'gc', 'gh', 'gn', 'gN', 'gu',
        'ib', 'iw','id',
        'j',
        'k', 'kb', 'kc', 'kd', 'kp', 'kP', 'kv',
        'l+l', 'l+o', 'l+s', 'l+t','l+*','l-l', 'l-o', 'l-s', 'l-t','l-*','ld', 'lm', 'ln', 'ls', 'lsa', 'lsc', 'lsf', 'lsf-', 'lsp', 
        'm',
        'n',
        'ob', 'ow', 'od',
        'p', 'pa', 'pc', 'pct', 'ph', 'pt', 
        'q', 'qq', 'qd',
        'r', 'rdmsr', 'rm', 
        's', 'so', 'sq', 'sqe', 'sqd', 'sx', 'sxd', 'sxe', 'sxi', 'sxn', 'sxr', 'sx-',
        't', 'ta', 'tb', 'tc', 'tct', 'th', 'tt', 
        'u', 'uf', 'up', 'ur', 'ux',
        'vercommand', 'version', 'vertarget',
        'wrmsr', 'wt',
        'x',
        'z'
        ]

    def __init__(self, debugServer):
        self.eventHandler = debugServer.getClientEventHandler()
        self.clientOutput = debugServer.getClientOutput()
        self.debugServer = debugServer
        self.stepSourceMode = False

        pykd.initialize()

        self.eventMonitor = EventMonitor(self)

    def isWindbgCommand(self, commandStr):
        if commandStr[0] in self.WINDBGPREFIX:
            return True

        token = commandStr.split()[0]

        if token in self.WINDBGCMD:
            return True

        if len(token)>=2 and token[0:2] == 'lm':
            return True

        return False

    def debugCommand(self, commandStr):

        if not self.isWindbgCommand(commandStr):
            return False

        try:
            pykd.dbgCommand(commandStr, suppressOutput=False)
        except pykd.DbgException:
            print "failed to run WinDBG command"

        return True

    def getSourceLine(self, addr):
        try:
            addr = self.frame.ip if addr == 0 else addr
            fileName, fileLine, displacement = pykd.getSourceLine(addr)
            return (fileName, fileLine)
        except pykd.DbgException:
            return ("", 0)

    def getSourceFromServer(self, addr):
        try:
            addr = self.frame.ip if addr == 0 else addr
            return  pykd.getSourceFileFromSrcSrv(addr)
        except pykd.DbgException:
            return ""

    def getDisasm(self,relpos,linecount):
        ip = self.frame.ip
        try:
            for i in xrange(linecount):
                dasm = pykd.disasm(ip)
                dasm.jumprel(relpos + i)
                dasmLines.append(dasm.instruction())
            return dasmLines
        except pykd.DbgException:
            return []

    def getRegsiters(self):
        regs = cpu()
        retlst = []

        #sometimes impossible get register value by index, so we need loop with exception handling
        for i in xrange(len(regs)):
            try:
                retlst.append(regs[i])
            except pykd.DbgException:
                pass
        return retlst

    def getMemory(self,expression, offset, length):

        ret = []
        if offset == 0:
            offset = pykd.expr(expression)

        currentOffset = offset
        while currentOffset < offset + length:
            nextpage = (currentOffset + 0x1000) // 0x1000 * 0x1000
            currentLength = min(nextpage, offset+length) - currentOffset 
            try:
                bytesLst = pykd.loadBytes(currentOffset, currentLength)
            except pykd.MemoryException:
                bytesLst = [None]*currentLength
            ret.extend(bytesLst)
            currentOffset += currentLength

        return ret

        #try:

        #    if offset == 0:
        #        offset = pykd.expr(expression)

        #    return pykd.loadBytes(offset, length)

        #except pykd.DbgException:
        #     return []

    def getStackTrace(self):
        try:
            stack = pykd.getStack()
            return [ (frame.frameOffset, frame.returnOffset, pykd.findSymbol(frame.instructionOffset, True) ) for frame in stack ]
        except pykd.DbgException:
            return []

    def setCurrentFrame(self, frameNo):
        try:
            pykd.setFrame(frameNo)
        except pykd.DbgException:
            pass

    def getCurrentFrame(self):
        return ( self.frame.ip, self.frame.ret, self.frame.fp, self.frame.sp )

    def getExpr(self,expr):
        try:
            return pykd.expr(expr)
        except pykd.DbgException:
            pass

    def pythonEval(self, expr):
        try:
            return str( eval(expr) )
        except Exception, e:
            return str(e)

    def breakin(self):
        try:
            pykd.breakin()
        except pykd.DbgException:
            pass

    def setStepSourceMode(self, mode):
        self.stepSourceMode = mode

    def pythonEval(self, expr):
        try:
            return str(eval(expr, globals(), globals()))
        except Exception, e:
            return str(e)

    def getLiveProcessList(self):
        return pykd.getLocalProcesses()


