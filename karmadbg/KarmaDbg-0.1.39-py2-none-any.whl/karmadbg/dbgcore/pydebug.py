
import sys
import thread
import inspect

from pprint import pprint
from bdb import Bdb, BdbQuit

from karmadbg.dbgcore.dbgdecl import *
from karmadbg.dbgcore.util import *
from karmadbg.dbgcore.varprint import *

class PythonDebugger(Bdb):

    def __init__(self, debugServer):
        Bdb.__init__(self, skip=["karmadbg.dbgcore.*"])
        self.eventHandler = debugServer.getClientEventHandler()
        self.debugServer = debugServer
        self.origtrace = None
        self.debugStarted = False
        self.currentFrameNo = 0

    def __enter__(self):
        self.origtrace = sys.gettrace()
        self.topframe = sys._getframe().f_back
        self.debugStarted = True
        self.clear_all_breaks()
        self.set_trace()

    def __exit__(self, type, value, traceback):
        self.debugStarted = False
        sys.settrace(self.origtrace)
        self.origtrace = None
        self.eventHandler.onPythonQuit()

    def outputPrompt(self):
        self.debugServer.write("PY>")

    def execfile(self, fileName, globals, locals):
        self.needQuit = False
        if self.eventHandler.onPythonStart(self.canonic(fileName)):
            with self:
                try:
                    execfile(fileName, globals, locals)
                except BdbQuit:
                    pass

    def execcode(self, code, globals, locals):
        self.needQuit = False
        if self.eventHandler.onPythonStart("<string>"):
            with self:
                try:
                    exec code in globals, locals
                except BdbQuit:
                    pass

    def getCurrentFrame(self):
        frame = self.currentFrame
        i = self.currentFrameNo
        while frame is not None and frame is not self.topframe and i > 0:
            i -= 1
            frame = frame.f_back
        return frame

    def user_line(self, frame):
        self.currentFrameNo = 0
        self.currentFrame = frame
        self.eventHandler.onPythonStateChanged(TargetState(TargetState.TARGET_STOPPED))
        self.interract(frame)
        self.eventHandler.onPythonStateChanged(TargetState(TargetState.TARGET_RUNNING))

    def user_return(self, frame, retval):
        self.currentFrameNo = 0
        self.currentFrame = frame
        self.eventHandler.onPythonStateChanged(TargetState(TargetState.TARGET_STOPPED))
        self.interract(frame)
        self.eventHandler.onPythonStateChanged(TargetState(TargetState.TARGET_RUNNING))


    def user_exception(self, frame, exc_info):

        self.currentFrameNo = 0
        self.currentFrame = frame

        print "!!! Exception"
        print showexception(exc_info)

        self.eventHandler.onPythonStateChanged(TargetState(TargetState.TARGET_STOPPED))
        self.interract(frame)
        self.eventHandler.onPythonStateChanged(TargetState(TargetState.TARGET_RUNNING))


    def interract(self, frame):
        
        filename, line = self.getPythonSourceLine()
        print filename
        with file(filename, 'r') as f:
            print " %04d" % line, "|", f.readlines()[line-1]

        self.debugServer.pythonCommandLoop()
        
        if self.needQuit == True:
            raise BdbQuit


    def debugCommand(self, commandStr):

        tokens = commandStr.split()

        if len(tokens) == 0:
            return

        if tokens[0] == 'q':
            print "stop python debugger"
            self.needQuit = True
            raise CommandLoopExit

        if tokens[0] == 'g':
            self._set_stopinfo(self.botframe, None, -1)
            raise CommandLoopExit

        if tokens[0] == 't':
            self.set_step()
            raise CommandLoopExit

        if tokens[0] == 'p':
            self.set_next(self.currentFrame)
            raise CommandLoopExit

        if tokens[0] == 'gu':
            self._set_stopinfo(self.currentFrame.f_back, None, 0)
            self.currentFrame.f_back.f_trace = self.trace_dispatch
            raise CommandLoopExit

        if tokens[0] == 'bp':
            try:
                if len(tokens) < 2:
                    self.setPythonBreakpoint( self.canonic( self.getCurrentFrame().f_code.co_filename), self.getCurrentFrame().f_lineno)
                if len(tokens) < 3:
                    self.setPythonBreakpoint( self.canonic( self.getCurrentFrame().f_code.co_filename), int(tokens[1]))
                else:
                    self.setPythonBreakpoint(tokens[1], int(tokens[2]))
            except:
                print "failed to set breakpoint"

            return

        if tokens[0] == 'bc':
            try:
                if len(tokens) < 2:
                    self.removePythonBreakpoint( self.canonic( self.getCurrentFrame().f_code.co_filename), self.getCurrentFrame().f_lineno)
                if len(tokens) < 3:
                    self.removePythonBreakpoint( self.canonic( self.getCurrentFrame().f_code.co_filename), int(tokens[1]))
                else:
                    self.removePythonBreakpoint(tokens[1], int(tokens[2]))
            except:
                print "failed to remove breakpoint"

            return

        if tokens[0] == 'pp':
            try:
                print eval(tokens[1], self.getCurrentFrame().f_globals, self.getCurrentFrame().f_locals)
            except:
                print showexception(sys.exc_info()) 
           
            return

        if tokens[0] == 'w':
            for l in self.getPythonStackTrace():
                print "%s\t%s : %d" % l
          
            return

        if tokens[0] == 'f':
            if len(tokens) >= 2:
                try:
                    frameno = int(tokens[1])
                    if 0 > frameno or frameno >= len(self.getPythonStackTrace()):
                        print "invalid frame number"
                        return
                    self.setPythonCurrentFrame(frameno)
                except:
                    print "invalid command"
                    return

            print self.canonic( self.getCurrentFrame().f_code.co_filename), "line:", self.getCurrentFrame().f_lineno
            return

        if tokens[0] == 'l':
            for name, val in self.getCurrentFrame().f_locals.iteritems():
                print "%20s : %s" % ( name, val )
            return

        if tokens[0] == 'h':
            print "Commands:"
            print  "q - quit from debugger"
            print  "g - go "
            print  "gu -  go up"
            print  "t - trace in"
            print  "p - step over"
            print  "bp [file] lineno - set breakpoint"
            print  "bc [file] lineno - remove breakpoint"
            print  "w - print stack"
            print  "pp var - print variable"
            print  "h - read this"
            print  "f [frameno] - change frame set"
            print  "l - print local scope"

            return

        print "invalid command"
        return
    
    def getPythonSourceLine(self):

        fileName = self.canonic( self.getCurrentFrame().f_code.co_filename)
        fileLine = self.getCurrentFrame().f_lineno
        return (fileName, fileLine)

    def getPythonStackTrace(self):
        stack = []
        frame = self.currentFrame
        while frame is not None and frame is not self.topframe:
            stack.append((frame.f_code.co_name, frame.f_globals["__name__"], frame.f_lineno))
            frame = frame.f_back
        return stack

    def setPythonBreakpoint(self, fileName, lineno):
        self.set_break(self.canonic(fileName), lineno)
        self.eventHandler.onPythonBreakpointAdd(self.canonic(fileName),lineno)

    def removePythonBreakpoint(self, fileName, lineno):
        self.clear_break(self.canonic(fileName), lineno)
        self.eventHandler.onPythonBreakpointRemove(self.canonic(fileName),lineno)

    def getPythonBreakpointList(self):
        return self.get_all_breaks()


    def getPythonLocals(self, subitems):
        
        vars = []
        if not subitems:
            for name, var in self.getCurrentFrame().f_locals.items():
                varPrinter = getMultilinePrinter(name,var)
                vars.append( (varPrinter.getVarName(), name, varPrinter.getVarShortValue(), varPrinter.getVarType(), varPrinter.getVarSubitems()) )
            return vars

        varName = subitems[0]
        var = self.getCurrentFrame().f_locals[varName]
        varPrinter = getMultilinePrinter(varName, var)
        subitems = subitems[1:]

        for subkey in subitems:
            varPrinter = varPrinter.getSubPrinter(subkey)

        for subname, subkey in varPrinter.getVarSubitems():
            subPrinter = varPrinter.getSubPrinter(subkey)
            vars.append( (subPrinter.getVarName(), subkey, subPrinter.getVarShortValue(), subPrinter.getVarType(), subPrinter.getVarSubitems()) )

        return vars

    def breakin(self):
        if self.debugStarted == False:
             thread.interrupt_main()
             return False
        self.set_step()
        return True

    def setPythonCurrentFrame(self, frameno):
        self.currentFrameNo = frameno
        self.eventHandler.onPythonStackFrameChanged(frameno)

    def getPythonCurrentFrame(self):
        return  self.currentFrameNo


