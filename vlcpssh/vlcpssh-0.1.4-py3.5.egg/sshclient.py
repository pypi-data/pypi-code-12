'''
Created on 2015/12/28

:author: hubo
'''
from paramiko.client import SSHClient, AutoAddPolicy
from vlcpssh.channel import Channel
from vlcp.event.event import Event, withIndices

@withIndices('factory', 'sftp', 'identifier')
class SFTPProgressEvent(Event):
    pass

class SSHFactory(object):
    '''
    Create SSH connections in thread pools
    '''
    def __init__(self, taskpool, container):
        '''
        :param taskpool: vlcp.utils.connector.TaskPool object, task pool to be used by factory
        '''
        self.taskpool = taskpool
        self.container = container
    def runTask(self, task, newthread = False):
        for m in self.taskpool.runTask(self.container, task, newthread):
            yield m
    def runGenTask(self, gentask, newthread = True):
        for m in self.taskpool.runGenTask(self.container, task, newthread):
            yield m
    def runAsyncTask(self, asynctask, newthread = True):
        for m in self.taskpool.runAsyncTask(self.container, asynctask, newthread):
            yield m
    def connect(self, hostname, autoadd = True, *args, **kwargs):
        "Create a SSHClient object and call connect. See paramiko.SSHClient.connect for other parameters"
        def task():
            s = SSHClient()
            if autoadd:
                s.set_missing_host_key_policy(AutoAddPolicy())
            s.connect(hostname, *args, **kwargs)
            return s
        for m in self.runTask(task):
            yield m
    def invoke_shell(self, sshclient, *args, **kwargs):
        "Call sshclient.invoke_shell and return a vlcpssh.Channel object"
        def task():
            c = sshclient.invoke_shell(*args, **kwargs)
            return Channel(c, self.container.scheduler)
        for m in self.runTask(task):
            yield m
        chan = self.container.retvalue
        chan.start()
        self.container.retvalue = chan
    def execute_command(self, sshclient, command):
        def task():
            c = sshclient.get_transport().open_session()
            c.exec_command(command)
            return Channel(c, self.container.scheduler)
        for m in self.runTask(task):
            yield m
        chan = self.container.retvalue
        chan.start()
        self.container.retvalue = chan
    def open_sftp(self, sshclient):
        for m in self.runTask(lambda: sshclient.open_sftp()):
            yield m
    def get(self, sftp, remotepath, localpath, progressobject = None, progresslimit = 0):
        def task(sender):
            lastprogress = [0]
            po = progressobject
            if po is None:
                po = object()
            def cb(p, t):
                if progresslimit is not None:
                    if p < lastprogress[0] * t / progresslimit:
                        return
                    lastprogress[0] += 1
                sender((SFTPProgressEvent(self, sftp, po),))
            sftp.get(remotepath, localpath, None if progresslimit is not None and progresslimit <= 0 else cb)
        for m in self.runAsyncTask(task):
            yield m
    def put(self, sftp, localpath, remotepath, progressobject = None, progresslimit = 0):
        def task(sender):
            lastprogress = [0]
            po = progressobject
            if po is None:
                po = object()
            def cb(p, t):
                if progresslimit is not None:
                    if p < lastprogress[0] * t / progresslimit:
                        return
                    lastprogress[0] += 1
                sender((SFTPProgressEvent(self, sftp, po),))
            sftp.put(localpath, remotepath, None if progresslimit is not None and progresslimit <= 0 else cb)
        for m in self.runAsyncTask(task):
            yield m
    def getfo(self, sftp, remotepath, fl, progressobject = None, progresslimit = 0):
        def task(sender):
            lastprogress = [0]
            po = progressobject
            if po is None:
                po = object()
            def cb(p, t):
                if progresslimit is not None:
                    if p < lastprogress[0] * t / progresslimit:
                        return
                    lastprogress[0] += 1
                sender((SFTPProgressEvent(self, sftp, po),))
            sftp.getfo(remotepath, fl, None if progresslimit is not None and progresslimit <= 0 else cb)
        for m in self.runAsyncTask(task):
            yield m
    def putfo(self, sftp, fl, remotepath, progressobject = None, progresslimit = 0):
        def task(sender):
            lastprogress = [0]
            po = progressobject
            if po is None:
                po = object()
            def cb(p, t):
                if progresslimit is not None:
                    if p < lastprogress[0] * t / progresslimit:
                        return
                    lastprogress[0] += 1
                sender((SFTPProgressEvent(self, sftp, po),))
            sftp.putfo(fl, remotepath, None if progresslimit is not None and progresslimit <= 0 else cb)
        for m in self.runAsyncTask(task):
            yield m
