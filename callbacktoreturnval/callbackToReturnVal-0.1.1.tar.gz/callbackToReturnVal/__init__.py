import signal
import os

def recvALRM(*args):
    pass

#Receive ALARM signal and continue
signal.signal(signal.SIGALRM, recvALRM)

global callbackReturnValue
callbackReturnValue = ""

def returnCallback(*args):
    global callbackReturnValue
    callbackReturnValue = args
    os.kill(os.getpid(), signal.SIGALRM)

def runSync(function):
    global callbackReturnValue
    signal.pause()
    return callbackReturnValue
