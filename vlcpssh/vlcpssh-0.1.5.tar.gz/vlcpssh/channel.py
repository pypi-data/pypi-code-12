'''
Created on 2015/12/25

:author: hubo
'''
from vlcp.event.runnable import RoutineContainer
from vlcp.event.stream import Stream
from vlcp.event.event import withIndices, Event
from vlcp.event.core import PollEvent
import socket

@withIndices('channel', 'channelobj', 'ioerror', 'exitstatus')
class ChannelExitEvent(Event):
    pass

class Channel(RoutineContainer):
    def __init__(self, channel = None, scheduler = None, writebufferlimit=0, autoclose = True):
        '''
        Constructor
        '''
        RoutineContainer.__init__(self, scheduler)
        self.channel = channel
        if self.channel is not None:
            self.channel.setblocking(False)
        # Counters
        self.totalrecv = 0
        self.totalsend = 0
        self.connrecv = 0
        self.connsend = 0
        self.daemon = False
        self.stdin = Stream(writebufferlimit=writebufferlimit)
        self.stdout = Stream(writebufferlimit=writebufferlimit)
        self.stderr = Stream(writebufferlimit=writebufferlimit)
        self.exit_status = -1
        self.autoclose = autoclose
    def attach(self, channel):
        self.channel = channel
        if self.channel is not None:
            self.channel.setblocking(False)
    def setdaemon(self, daemon):
        if self.daemon != daemon:
            if self.channel:
                self.scheduler.setPollingDaemon(self.channel, daemon)
            if hasattr(self, 'mainroutine'):
                self.scheduler.setDaemon(self.mainroutine, daemon, True)
            self.daemon = daemon
    def _read_main(self):
        try:
            canread_matcher = PollEvent.createMatcher(self.channel.fileno(), PollEvent.READ_READY)
            self.readstop = False
            exitLoop = False
            firstTime = True
            eofExit = False
            maxsize = 4096
            while self.exit_status == -1:
                if not firstTime:
                    if exitLoop:
                        for m in self.waitWithTimeout(1, canread_matcher):
                            yield m
                        if self.channel.exit_status_ready():
                            self.exit_status = self.channel.recv_exit_status()
                        if self.timeout:
                            break
                    else:
                        yield (canread_matcher,)
                else:
                    firstTime = False
                while True:
                    try:
                        data = self.channel.recv(maxsize)
                        if not data:
                            eofExit = True
                            exitLoop = True
                            break
                        self.totalrecv += len(data)
                        self.connrecv += len(data)
                        for m in self.stdout.write(data, self, False, True, buffering=False, split=False):
                            yield m
                    except socket.timeout:
                        break
                    except:
                        exitLoop = True
                        break
                while True:
                    try:
                        data = self.channel.recv_stderr(maxsize)
                        if not data:
                            break
                        self.totalrecv += len(data)
                        self.connrecv += len(data)
                        for m in self.stderr.write(data, self, False, True, buffering=False, split=False):
                            yield m
                    except socket.timeout:
                        break
                    except:
                        exitLoop = True
                        break
                if self.channel.exit_status_ready():
                    self.exit_status = self.channel.recv_exit_status()
        except:
            for m in self.stdout.error(self, True):
                yield m
            for m in self.stderr.error(self, True):
                yield m
            for m in self.waitForSend(ChannelExitEvent(self, self.channel, True, self.exit_status)):
                yield m
            raise
        else:
            if eofExit:
                for m in self.stdout.write(b'', self, True, True, buffering=False, split=False):
                    yield m
                for m in self.stderr.write(b'', self, True, True, buffering=False, split=False):
                    yield m
                for m in self.waitForSend(ChannelExitEvent(self, self.channel, False, self.exit_status)):
                    yield m
            else:
                for m in self.stdout.error(self, True):
                    yield m
                for m in self.stderr.error(self, True):
                    yield m
                for m in self.waitForSend(ChannelExitEvent(self, self.channel, True, self.exit_status)):
                    yield m
        finally:
            self.readstop = True
            if self.autoclose and not self.writestop:
                if hasattr(self, 'writeroutine') and self.writeroutine:
                    self.writeroutine.close()
            if self.writestop and self.connected:
                self.connected = False
                self._close(False)
    def _write_main(self):
        try:
            self.writestop = False
            canwrite_matcher = PollEvent.createMatcher(self.channel.fileno(), PollEvent.WRITE_READY)
            exitLoop = False
            while not exitLoop:
                for m in self.stdin.prepareRead(self):
                    yield m
                try:
                    msg = self.stdin.readonce()
                    isEOF = False
                except:
                    msg = b''
                    isEOF = True
                totalLen = len(msg)
                currPos = 0
                while currPos < totalLen:
                    wouldblock = False
                    try:
                        currLen = self.channel.send(msg[currPos:])
                        currPos += currLen
                        self.totalsend += currLen
                        self.connsend += currLen
                    except socket.timeout:
                        wouldblock = True
                    except:
                        exitLoop = True
                        break
                    if wouldblock:
                        yield (canwrite_matcher,)
                if isEOF:
                    try:
                        self.channel.shutdown(socket.SHUT_WR)
                    except:
                        pass
                    exitLoop = True
        finally:
            self.stdin.close(self.scheduler)
            self.writestop = True
            if self.readstop and self.connected:
                self.connected = False
                self._close(False)
    def _close(self, closeroutine = True):
        if closeroutine:
            if hasattr(self, 'readroutine'):
                self.writeroutine.close()
            if hasattr(self, 'writeroutine'):
                self.writeroutine.close()
        if self.channel is not None:
            self.scheduler.unregisterPolling(self.channel, self.daemon)
            self.channel.close()
            self.channel = None
    def close(self):
        self._close()
    def main(self):
        try:
            self.localaddr = self.channel.get_transport().sock.getsockname()
        except:
            pass
        try:
            self.remoteaddr = self.channel.get_transport().sock.getpeername()
        except:
            pass
        self.scheduler.registerPolling(self.channel.fileno())
        self.connmark = 0
        self.connected = True
        self.connrecv = 0
        self.connsend = 0
        self.writestop = False
        self.readstop = False
        self.subroutine(self._read_main(), True, 'readroutine', self.daemon)
        self.subroutine(self._write_main(), True, 'writeroutine', self.daemon)
        if False:
            yield
    def shutdown(self, force = False, connmark = -1):
        '''
        Can call without delegate
        '''
        self._close()
        if False:
            yield
    def reconnect(self, force = True, connmark = None):
        '''
        Can call without delegate
        '''
        self._close()
        if False:
            yield
    def reset(self, force = True, connmark = None):
        '''
        Can call without delegate
        '''
        self._close()
        if False:
            yield
    def wait(self, container, raiseException = True):
        if self.readstop:
            if raiseException and self.exit_status == -1:
                raise IOError('Channel read exception occurs')
            else:
                container.retvalue = self.exit_status
        else:
            yield (ChannelExitEvent.createMatcher(self),)
            if raiseException and container.event.ioerror:
                raise IOError('Channel read exception occurs')
            else:
                container.retvalue = container.event.exitstatus
    def __repr__(self, *args, **kwargs):
        baserepr = RoutineContainer.__repr__(self, *args, **kwargs)
        return baserepr + '(#%d %r -> %r)' % (self.channel.get_id() if self.channel else 0, getattr(self, 'localaddr', None), getattr(self, 'remoteaddr', None))
