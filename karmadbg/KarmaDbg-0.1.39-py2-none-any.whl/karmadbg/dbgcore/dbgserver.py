import signal
import sys
import time
import os
import timeit
import shlex
import glob
import re

from copy import copy, deepcopy
from abc import abstractmethod
from bdb import BdbQuit
from codeop import compile_command

from karmadbg.dbgcore.dbgdecl import *
from karmadbg.dbgcore.util import *
from karmadbg.dbgcore.nativedbg import NativeDebugger
from karmadbg.dbgcore.pydebug import PythonDebugger
from karmadbg.dbgcore.macro import *
from karmadbg.dbgcore.autocomplete import autoComplete

import pykd
from pykd import *

dbgserver = None



class DebugServer(object):

    def __init__(self):
        self.pythonRunCode = False

    def startServer(self):

        global dbgserver
        dbgserver = self

        self.commandHandler = None

        signal.signal( signal.SIGINT, signal.SIG_IGN)

        self.clientOutput = self.getClientOutput()

        sys.stdin = self
        sys.stdout = self
        sys.stderr = self

        self.nativeDbg = NativeDebugger(self)
        self.pythonDbg = PythonDebugger(self)

        self.interruptServer = self.processServerInterrupt(self)
        self.commandServer = self.processServerCommand(self)

        registerMacros()

        print
        print "start debug server"
        self.startup()

        self.pythonRunCode = False
        self.pythonEdit = False

        self.nativeCommandLoop()

    def getPrompt(self):
        if self.pythonRunCode:
            return "PY>"
        if self.pythonEdit:
            return "..."
        return ">>>"

    def pythonEditLoop(self, editObj):
        self.commandServer.sendAnswer(None)
        self.commandLoop(editObj)

    def pythonCommandLoop(self):
        self.commandServer.sendAnswer(None)
        self.commandLoop(self.pythonDbg)

    def nativeCommandLoop(self):
        self.commandLoop(self.nativeDbg)

    def commandLoop(self, commandHandler):

        oldHandler = self.commandHandler
        self.commandHandler = commandHandler

        while not self.commandServer.stopped:

            methodName, args, kwargs = self.commandServer.getRequest()

            try:

                if hasattr(self, methodName):

                    try:
                        res = getattr(self,methodName)(*args, **kwargs)
                    except CommandLoopExit:
                        self.commandHandler = oldHandler
                        return
                    except Exception, ex:
                        res = ex

                    self.commandServer.sendAnswer(res)
                    continue

                    # Native DBG command ( windbg )
                if hasattr(self.nativeDbg, methodName):
                    try:
                        res = getattr(self.nativeDbg, methodName)(*args, **kwargs)
                    except CommandLoopExit:
                        self.commandHandler = oldHandler
                        return
                    self.commandServer.sendAnswer(res)
                    continue

                # Python DBG command 
                if hasattr(self.pythonDbg, methodName):
                    try:
                        res = getattr(self.pythonDbg, methodName)(*args, **kwargs)
                    except CommandLoopExit:
                        self.commandHandler = oldHandler
                        return
                    self.commandServer.sendAnswer(res)
                    continue

                self.commandServer.sendAnswer(None)


            except:
                sys.stderr.write(showtraceback( sys.exc_info(), 2 ))
                self.commandServer.sendAnswer(None)

    def debugCommand(self, commandStr):


        if self.commandHandler is self.nativeDbg:

            if not commandStr:
                return

            if self.nativeDbg.debugCommand(commandStr):
                return

            if self.isMacroCmd(commandStr):
                self.macroCmd(commandStr)
                return

            self.pythonCommand(commandStr)

            return

        elif self.commandHandler is self.pythonDbg:

            self.pythonDbg.debugCommand(commandStr)

        else:

            self.commandHandler.debugCommand(commandStr)

    def callFunction(self, func, *args, **kwargs):
        return func(*args,**kwargs)

    def writedml(self, str):
        self.clientOutput.output(str, True)

    def write(self,str):
        self.clientOutput.output(str, False)

    def readline(self):
        return self.clientOutput.input()

    def flush(self):
        pass

    def breakin(self):

        if self.pythonRunCode == True:
            if self.pythonDbg.breakin():
                return
        self.nativeDbg.breakin()

    def quit(self):
        self.interruptServer.stop()
        self.commandServer.stop()

    def isMacroCmd(self,commandStr):
        return commandStr[0] == '%'

    def macroCmd(self,commandStr):

        try:
           macroCommand(commandStr)
        except SystemExit:
            print "macro command raised SystemExit"
        except:
            print showtraceback(sys.exc_info())

    def runCodeCommand(self, scriptname, args, debug = False):

        sysargv = copy(sys.argv)
        syspath = copy(sys.path)
        sysmodules = copy(sys.modules)

        dirname, _ = os.path.split(scriptname)

        if not dirname:
            script, suffix = os.path.splitext(scriptname)
            try:
                _,scriptname,_=imp.find_module(script)
                dirname, _ = os.path.split(scriptname)
            except ImportError:
                sys.stderr.write("module \'%s\' not found\n" % script)
                self.commandServer.sendAnswer(None)
                return

        if not dirname in sys.path:
            sys.path.append(dirname)

        self.pythonRunCode = True

        try:
            
            sys.argv = []
            sys.argv.append(scriptname)
            sys.argv.extend(args)

            import __builtin__

            glob = {}
            glob['__builtins__'] = __builtin__
            glob["__name__"] = "__main__"
            glob["__file__"] = scriptname
            glob["__doc__"] = None
            glob["__package__"] = None

            if debug:
                self.pythonDbg.execfile(scriptname,glob,glob)
            else:
                execfile(scriptname, glob, glob)

        except SystemExit:
            print "script raised SystemExit"

        except:
            sys.stderr.write(showtraceback( sys.exc_info(), 2 ))

        self.pythonRunCode = False

        sys.argv = sysargv
        sys.path = syspath
        sys.modules = sysmodules

        sys.stdin = self
        sys.stdout = self
        sys.stderr = self


    def execCode(self, codestr, debug = False):

        if not codestr:
            return

        self.pythonRunCode = True

        try:

            codeObject = compile(codestr, "<input>", "single")

            if debug:
                self.pythonDbg.execcode(codeObject, globals(), globals())
            else:
                exec codeObject in globals()

        except SystemExit:
            print "expression raised SystemExit"

        except:
            print showtraceback( sys.exc_info(), 2 )

        self.pythonRunCode = False

    def timeCommand(self, command):
        t1 = time.clock()
        ret = self.nativeDbg.debugCommand(" ".join(vars[1:]))
        t2 = time.clock()
        print "time elapsed: %fs" % (t2-t1)
        return ret


    def pythonCommand(self, commandStr):

        class PythonCommand(object):
            def __init__(innerself, commandStr):
                innerself.commandStr = commandStr

            def execute(innerself):
                
                try:

                    self.pythonEdit = True

                    while True:

                        code = compile_command(innerself.commandStr, "<input>", "single")
                        if code:
                            break

                        self.pythonEditLoop(innerself)
 
                except SyntaxError:
                    self.pythonEdit = False
                    print showtraceback(sys.exc_info(), 3)
                    return

                self.pythonEdit = False

                try:
                    exec code in globals()

                except SystemExit:
                    self.getClientEventHandler().quit()

                except:
                    print showtraceback(sys.exc_info())
            
            def debugCommand(innerself, str):
                innerself.commandStr += "\n" + str
                raise CommandLoopExit

        PythonCommand(commandStr).execute()

    def startup(self):
        #from karmadbg.startup.firstrun import firstrun
        from karmadbg.startup.startup import startup
        #firstrun()
        startup()

    def getAutoComplete(self, startAutoComplete):
        return autoComplete(startAutoComplete)





