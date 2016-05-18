# ============================================================
#
# Copyright (C) 2013, 2015 Jan Moringen <jmoringe@techfak.uni-bielefeld.de>
#
# This file may be licensed under the terms of the
# GNU Lesser General Public License Version 3 (the ``LGPL''),
# or (at your option) any later version.
#
# Software distributed under the License is distributed
# on an ``AS IS'' basis, WITHOUT WARRANTY OF ANY KIND, either
# express or implied. See the LGPL for the specific language
# governing rights and limitations.
#
# You should have received a copy of the LGPL along with this
# program. If not, go to http://www.gnu.org/licenses/lgpl.html
# or write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# The development of this software was supported by:
#   CoR-Lab, Research Institute for Cognition and Robotics
#     Bielefeld University
#
# ============================================================

"""
This module provides functionality to retrieve, select and process
events stored in log files by rsbag record.

In order to create basic objects, have a look at the function
L{openBag}.

@author: jmoringe

"""

import os
import signal
import subprocess
import threading
import time
import Queue

import logging

import rsb

from loggerbyclass import get_logger_by_class

prefix = '/vol/toolkit/nightly/trusty/x86_64/last'

PRIVATE_SCOPE_PREFIX = rsb.Scope('/__rsbag/python')
# number of scope components to skip in received events = private prefix + /listen
PRIVATE_SCOPE_SKIP = len(PRIVATE_SCOPE_PREFIX.components) + 1

class ItemSequence (object):
    def __init__(self, server):
        self.__server  = server
        self.__timeout = 5
        self.__length  = self.__server.length.async().get(timeout = self.__timeout)

    def getServer(self):
        return self.__server

    server = property(getServer)

    def getTimeout(self):
        return self.__timeout

    timeout = property(getTimeout)

    def __len__(self):
        return self.__length

    def __getitem__(self, index):
        if isinstance(index, slice):
            return map(self.__getitem__,
                       xrange(index.start or 0,
                              index.stop or len(self),
                              index.step or 1))
        else:
            return self._get(index)

    def __iter__(self):
        for i in xrange(len(self)):
            yield self._get(i)

    def __repr__(self):
        return '<%s of %d item(s) at %s>' \
            % (type(self).__name__, len(self), id(self))

class EventSequence (ItemSequence):
    def __init__(self, server, queue):
        super(EventSequence, self).__init__(server)

        self.__queue = queue

    def _get(self, index):
        self.server.seek.async(index).get(timeout = self.timeout)
        self.server.emit.async()
        event = self.__queue.get(block = True)
        event.scope = rsb.Scope('/' + '/'.join(event.scope.components[PRIVATE_SCOPE_SKIP:])) # TODO(jmoringe, 2013-04-17): slow
        return event

class DataSequence (ItemSequence):
    def _get(self, index):
        self.server.seek.async(index).get(timeout = self.timeout)
        return self.server.get.async().get(timeout = self.timeout)

class Connection (object):
    def __init__(self, port, controlScope, listenScope, converters = None):
        self.__logger = get_logger_by_class(self.__class__)

        # create a config for the meta-communication
        self.__server   = rsb.createRemoteServer(scope = controlScope,
                                                 config = self._privateParticipantConfig(port))

        # use a second config with the user-defined converters for the real
        # event receiving
        config = self._privateParticipantConfig(port)
        if converters:
            config.getTransport('socket').setConverters(converters)
        self.__listener = rsb.createListener(scope = listenScope, config = config)
        self.__queue    = Queue.Queue()
        self.__listener.addHandler(lambda event: self.__queue.put(event))

        self.__events   = None
        self.__items    = None

    @staticmethod
    def _privateParticipantConfig(port):
        return rsb.ParticipantConfig.fromDict({ 'transport.socket.enabled': '1',
                                                'transport.socket.host':    'localhost',
                                                'transport.socket.port':    '%s' % port,
                                                'transport.socket.server':  '0',
                                                'introspection.enabled':    '0' })

    def _cleanup(self):
        try:
            self.__server.quit.async()
            time.sleep(1)
        except Exception, e:
            self.__logger.warn('Failed to send termination request to rsbag play: %s', e)
        try:
            self.__server.deactivate()
        except Exception, e:
            self.__logger.warn('Failed to deactivate server: %s', e)
        try:
            self.__listener.deactivate()
        except Exception, e:
            self.__logger.warn('Failed to deactivate listener: %s', e)

    def __del__(self):
        self._cleanup

    def getServer(self):
        return self.__server

    server = property(getServer)

    def getListener(self):
        return self.__listener

    listener = property(getListener)

    def getQueue(self):
        return self.__queue

    queue = property(getQueue)

    def getEvents(self):
        if self.__events is None:
            self.__events = EventSequence(self.server, queue = self.queue)
        return self.__events

    events = property(getEvents)

    def getItems(self):
        if self.__items is None:
            self.__items = DataSequence(self.server)
        return self.__items

    items = property(getItems)

class _NonBlockingStreamReader(object):
    """
    Adapted from: http://eyalarubas.com/python-subproc-nonblock.html
    """

    def __init__(self, stream):
        self._stream = stream
        self._queue = Queue.Queue()

        def populateQueue(stream, queue):
            while True:
                line = stream.readline()
                if line:
                    queue.put(line)
                else:
                    # else we have reached the end of the stream
                    break

        self._thread = threading.Thread(target = populateQueue,
                                        args = (self._stream, self._queue))
        self._thread.daemon = True
        self._thread.start()

    def readline(self, timeout = None):
        try:
            return self._queue.get(block = timeout is not None,
                                   timeout = timeout)
        except Queue.Empty:
            return None

class Bag (Connection):
    def __init__(self, file, channels = None,
                 rsbag = os.path.join(prefix, 'bin/rsbagcl0.13'),
                 converters = None):
        self.__logger = get_logger_by_class(self.__class__)

        self.__file         = file

        self.__controlScope = PRIVATE_SCOPE_PREFIX.concat(rsb.Scope('/control/'))
        self.__controlURI   = 'socket://localhost:0%s?server=1&portfile=-' % self.__controlScope.toString()

        self.__listenScope  = PRIVATE_SCOPE_PREFIX.concat(rsb.Scope('/listen/'))
        self.__listenURI    = 'socket://localhost:0%s?server=1&portfile=-' % self.__listenScope.toString()

        env = dict(os.environ)
        env['RSB_INTROSPECTION_ENABLED'] = '0'

        channelOptions = []
        if not channels is None:
            for channel in channels:
                channelOptions += [ '-c', channel ]

        adjustments = [ '(:original_send (:copy :send))',
                        '(:|rsbag:original_send| (:copy :send))',
                        '(:|rsbag:original_receive| (:copy :receive))' ]
        command = [ rsbag, 'play',
                    '--show-progress', 'ready',
                    '--on-error=continue',
                    '--replay-strategy',
                    'remote-controlled :uri "%s" :adjustments (%s)'
                    % (self.__controlURI,
                       ' '.join(adjustments)) ] \
                  + channelOptions                                      \
                  + [ file, self.__listenURI ]
        self.__logger.debug('Executing command %s', command)
        self.__process = subprocess.Popen(command, close_fds = True,
                                          env = env,
                                          stdout = subprocess.PIPE,
                                          stderr = subprocess.PIPE)

        # wait for the bag binary to return the port
        try:
            reader = _NonBlockingStreamReader(self.__process.stdout)
            out = reader.readline(20.0)
            if out is None:
                raise RuntimeError('Bag did not print the socket port until timeout')
            self.__logger.debug('Output returned by bag: "%s"', out)
            port = int(out.strip())

            # wait for ready output from bag
            reader = _NonBlockingStreamReader(self.__process.stderr)
            out = reader.readline(20.0)
            if out is None:
                raise RuntimeError('Bag did not print ready until timeout')
            assert out.strip() == 'ready'

            super(Bag, self).__init__(port, self.__controlScope, self.__listenScope, converters=converters)
        except Exception as error:
            self._cleanProcess()
            raise error

    def _cleanup(self):
        super(self.__class__, self)._cleanup()
        self._cleanProcess()

    def _cleanProcess(self):
        def waitForChild():
            try:
                for i in xrange(50):
                    if not (self.__process.poll() is None):
                        self.__logger.debug('Child process terminated')
                        return True
                    time.sleep(.1)
            except Exception, e:
                self.__logger.warn('Failed to wait for child process: %s', e)
        self.__logger.debug('Waiting for child process')
        if not waitForChild():
            self.__logger.warn('Child process did not terminate')
            try:
                self.__process.terminate()
                waitForChild()
            except Exception, e:
                self.__logger.warn('Failed to terminate child process: %s', e)

    def __del__(self):
        self._cleanup()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup()

    def __repr__(self):
        string = self.__file
        if len(string) > 35:
            string = string[:16] + "..." + string[-16:]
        return '<%s for "%s" at %s>' \
            % (type(self).__name__, string, id(self))

def openBag(file, channels = None,
            rsbag = os.path.join(prefix, 'bin/rsbagcl0.13'),
            converters = None):
    """
    Open B{file}, potentially selecting B{channels}, for processing and
    return a L{Bag} object representing the log file.

    @param file: The name of the log file which should be opened.
    @type file: str
    @param channels: If supplied, a list of regular expression strings
                     which select channels to be included in the event
                     sequence.
    @type channels: list or None
    @param rsbag: If supplied, filename of the rsbag binary that
                  should be used.
    @type rsbag: str
    @param converters: converters to use for receiving events. Defaults to the
                       converters registered in the RSB repository
    @type converters: ConverterSelectionStrategy or None
    @rtype: Bag

    @author: jmoringe

    """
    return Bag(file, channels = channels, rsbag = rsbag, converters = converters)
