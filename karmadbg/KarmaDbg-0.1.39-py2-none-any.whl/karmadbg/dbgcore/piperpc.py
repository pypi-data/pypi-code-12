
import string
import random

from multiprocessing.connection import Listener, Client
from threading import Thread
from multiprocessing import Manager

def createRpcLocator():
    return RpcLocatorProxy(RpcLocator())

class RpcLocator(object):

    def __init__(self):
        self.manager = Manager()
        self.rpcServerList = self.manager.dict()

class RpcLocatorProxy(object):

    def __init__(self, rpcLocator):
        self.rpcServerList = rpcLocator.rpcServerList

    def get(self,name):
        uniqueName = self.rpcServerList[name]
        return RpcProxy(name, uniqueName)

class RpcServer(object):

    def __init__(self, rpcLocator, serverObj, className):
        self.rpcLocator = rpcLocator
        self.serverObject = serverObj
        self.className = className
        self.uniqueName = ''.join(random.choice(string.ascii_letters) for _ in range(32))
        self.listener = Listener(family = "AF_PIPE", address = "\\\\.\\pipe\\" + self.uniqueName)
        rpcLocator.rpcServerList[self.className] = self.uniqueName
        self.thread = Thread(target = self.workerRoutine)
        self.thread.start()

    def workerRoutine(self):
        client = self.listener.accept()
        self.listener.close()
        while True:
            method, args, kwargs = client.recv()
            try:
                res = getattr(self.serverObject, method)(*args, **kwargs)
            except Exception, ex:
                res = ex
            client.send(res)

    def join(self):
        self.thread.join()

    def getUniqueName(self):
        return self.uniqueName

class RpcProxy(object):

    def __init__(self, serverName, serverKey):
        self.clientConnection = Client(family = "AF_PIPE", address = "\\\\.\\pipe\\" + serverKey)

    def __getattr__(self, name):

        clientConnection = self.clientConnection

        class remoteCall(object):
            def __call__(self, *args, **kwargs):
                clientConnection.send( (name, args, kwargs) )
                result = clientConnection.recv()
                if isinstance(result, Exception):
                    raise result
                return result

        return remoteCall()
