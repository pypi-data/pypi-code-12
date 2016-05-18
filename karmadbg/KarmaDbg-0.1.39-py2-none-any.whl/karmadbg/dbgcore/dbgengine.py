import sys

from multiprocessing import Pipe, Process
from threading import Thread

from karmadbg.dbgcore.dbgdecl import *
from karmadbg.dbgcore.dbgserver import DebugServer

class ConsoleDebugClient(AbstractDebugClient):

    def quit(self):
       pass

    def output(self,str, dml=False):
        sys.stdout.write(str)

    def input(self):
        return sys.stdin.readline()

    def onTargetStateChanged(self,state):
        pass

    def onTargetChangeCurrentThread(self):
        pass

    def onTargetChangeCurrentFrame(self, frame):
        pass

    def onTargetChangeBreakpoints(self):
        pass

    def onPythonStart(self, scriptName):
        return True

    def onPythonQuit(self):
        pass

    def onPythonStateChanged(self,state):
        pass

    def onPythonBreakpointAdd(self, file, line):
        pass

    def onPythonBreakpointRemove(self, file, line):
        pass

    def onPythonStackFrameChanged(self, frameno):
        pass

class LocalProxy(object):

    def __init__(self, pipe):
        self.pipe = pipe

    def __getattr__(self, methodname):

        class callToPipe(object):

            def __init__(self,pipe):
                self.pipe=pipe

            def __call__(self, *args, **kwargs):
                self.pipe.send( (methodname, args, kwargs) )
                result = self.pipe.recv()
                if isinstance(result, Exception):
                    raise result
                return result

        return callToPipe(self.pipe)


class LocalStub(object):

    def __init__(self, pipe, requestHandler):
        self.pipe = pipe
        self.requestHandler = requestHandler
        self.stopped = False

    def getRequest(self):
        return self.pipe.recv()

    def sendAnswer(self, answer):
        return self.pipe.send(answer)

    def stop(self):
        self.stopped = True

class LocalThreadApartmentStub(LocalStub):

    def __init__(self, pipe, requestHandler):
        super(LocalThreadApartmentStub,self).__init__(pipe,requestHandler)
        self.workThread = Thread(target=self.threadRoutine)
        self.workThread.start()

    def threadRoutine(self):

        while not self.stopped:
            if self.pipe.poll(1):
                methodName, args, kwargs = self.getRequest()
                try:
                    result = getattr(self.requestHandler, methodName)(*args, **kwargs)
                except Exception, ex:
                    result = ex
                self.sendAnswer(result)

    def stop(self):
        self.stopped = True
        self.workThread.join()


class LocalDebugServer(DebugServer, Process):

    def __init__(self):
        self.outputPipe, outputServerPipe = Pipe()
        self.commandPipe, commandServerPipe = Pipe()
        self.interruptPipe, interruptServerPipe = Pipe()
        self.eventPipe, eventServerPipe = Pipe()
        self.outputStub = None
        self.eventStub = None
        self.interruptStub = None
        self.commadStub = None
        self.stopped = False

        DebugServer.__init__(self)
        Process.__init__(self, target = self.processRoutine, args = (outputServerPipe, commandServerPipe, interruptServerPipe, eventServerPipe))

    def processRoutine(self, outputPipe, commandPipe, interruptPipe, eventPipe ):

        self.outputPipe = outputPipe
        self.commandPipe = commandPipe
        self.interruptPipe = interruptPipe
        self.eventPipe = eventPipe

        self.startServer()

    def getClientOutput(self):
        return LocalProxy(self.outputPipe)

    def getClientEventHandler(self):
        return LocalProxy(self.eventPipe) 

    def getServerControl(self):
        return LocalProxy(self.commandPipe)

    def getServerInterrupt(self):
        return LocalProxy(self.interruptPipe)

    def processClientOutput(self, requestHandler):
        if not self.outputStub:
            self.outputStub  = LocalThreadApartmentStub(self.outputPipe, requestHandler)
        return self.outputStub

    def processClientEvents(self, requestHandler):
        if not self.eventStub:
            self.eventStub = LocalThreadApartmentStub(self.eventPipe, requestHandler)
        return self.eventStub

    def processServerInterrupt(self, requestHandler):
        if not self.interruptStub:
            self.interruptStub = LocalThreadApartmentStub( self.interruptPipe, requestHandler)
        return self.interruptStub

    def processServerCommand(self, requestHandler):
        if not self.commadStub:
            self.commandStub = LocalStub(self.commandPipe, requestHandler)
        return self.commandStub


class DbgEngine(object):
    
    def __init__(self, dbgClient, dbgServer, dbgSettings):
        self.dbgServer = dbgServer
        self.dbgClient = dbgClient
        self.dbgSettings = dbgSettings

    def start(self):
        #start server
        self.dbgServer.start()

        #start client callback thread-apartment handlers
        self.outputStub = self.dbgServer.processClientOutput(self.dbgClient)
        self.eventsStub = self.dbgServer.processClientEvents(self.dbgClient)

    def stop(self):

        #stop debug server
        self.dbgServer.getServerInterrupt().breakin()
        self.dbgServer.getServerControl().quit()

        #stop client callback thread-apartment handlers
        self.outputStub.stop()
        self.eventsStub.stop()
        
    def getServer(self):
        return self.dbgServer

    def getClient(self):
        return self.dbgClient
