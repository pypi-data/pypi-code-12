


class RpcServer(


LocalDebugServer(DebugServer,Process):

#    def __init__(self):
#        self.outputPipe, outputServerPipe = Pipe()
#        self.commandPipe, commandServerPipe = Pipe()
#        self.interruptPipe, interruptServerPipe = Pipe()
#        self.eventPipe, eventServerPipe = Pipe()
#        self.outputStub = None
#        self.eventStub = None
#        self.interruptStub = None
#        self.commadStub = None
#        self.stopped = False

#        DebugServer.__init__(self)
#        Process.__init__(self, target = self.processRoutine, args = (outputServerPipe, commandServerPipe, interruptServerPipe, eventServerPipe))
