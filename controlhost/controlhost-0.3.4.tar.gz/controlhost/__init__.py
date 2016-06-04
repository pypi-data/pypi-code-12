# coding=utf-8
# Filename: __init__.py
"""
A set of classes and tools wich uses the ControlHost protocol.

"""
from __future__ import absolute_import

from controlhost.__version__ import version

import socket
import struct
import re

try:
    from km3pipe.logger import logging
except ImportError:
    pass
else:
    log = logging.getLogger(__name__)

__author__ = "Tamas Gal"
__copyright__ = ("Copyright 2014, Tamas Gal and the KM3NeT collaboration "
                 "(http://km3net.org)")
__credits__ = []
__license__ = "MIT"
__version__ = version
__maintainer__ = "Tamas Gal"
__email__ = "tgal@km3net.de"
__status__ = "Development"


BUFFER_SIZE = 1024
valid_tag = re.compile(r"^(IO|RC|TRG)_.*$")


class Client(object):
    """The ControlHost client"""
    def __init__(self, host, port=5553):
        self.host = host
        self.port = port
        self.socket = None
        self.tags = []

    def subscribe(self, tag, mode='wait'):
        full_tag = self._full_tag(tag, mode)
        if full_tag not in self.tags:
            self.tags.append(full_tag)
        self._update_subscriptions()

    def unsubscribe(self, tag, mode='wait'):
        try:
            self.tags.remove(self._full_tag(tag, mode))
        except ValueError:
            pass
        else:
            self._update_subscriptions()

    def _full_tag(self, tag, mode):
        mode_flag = ' w ' if mode == 'wait' else ' a '
        full_tag = mode_flag + tag
        return full_tag

    def _update_subscriptions(self):
        log.debug("Subscribing to tags: {0}".format(self.tags))
        tags = ''.join(self.tags)
        message = Message('_Subscri', tags)
        self.socket.send(message.data)
        message = Message('_Always')
        self.socket.send(message.data)

    def get_message(self):
        while True:
            log.info("     Waiting for control host Prefix")
            prefix = Prefix(data=self.socket.recv(Prefix.SIZE))
            if valid_tag.match(prefix.tag) is None:
                log.error("Invalid tag or corrupt message recieved: '{0}'"
                          .format(prefix.tag))
                self._reconnect()
                continue
            else:
                break

        message = ''
        log.info("       got a Prefix with {0} bytes.".format(prefix.length))
        while len(message) < prefix.length:
            log.info("          message length: {0}".format(len(message)))
            log.info("            (getting next part)")
            buffer_size = min((BUFFER_SIZE, (prefix.length - len(message))))
            message += self.socket.recv(buffer_size)
        log.info("     ------ returning message with {0} bytes"
                 .format(len(message)))
        return prefix, message(self)

    def _connect(self):
        """Connect to JLigier"""
        log.debug("Connecting to JLigier")
        self.socket = socket.socket()
        self.socket.connect((self.host, self.port))

    def _disconnect(self):
        """Close the socket"""
        log.debug("Disconnecting from JLigier")
        if self.socket:
            self.socket.close()

    def _reconnect(self):
        """Reconnect to JLigier and subscribe to the tags."""
        log.debug("Reconnecting to JLigier...")
        self._disconnect()
        self._connect()
        self._update_subscriptions()

    def __enter__(self):
        self._connect()
        return self

    def __exit__(self, type, value, traceback):
        self._disconnect()


class Message(object):
    """The representation of a ControlHost message."""
    def __init__(self, tag, message=''):
        self.prefix = Prefix(tag, len(message))
        self.message = message

    @property
    def data(self):
        return self.prefix.data + self.message


class Tag(object):
    """Represents the tag in a ControlHost Prefix."""
    SIZE = 8

    def __init__(self, data=None):
        self._data = b''
        self.data = data

    @property
    def data(self):
        """The byte data"""
        return self._data

    @data.setter
    def data(self, value):
        """Set the byte data and fill up the bytes to fit the size."""
        if not value:
            value = b''
        if len(value) > self.SIZE:
            raise ValueError("The maximum tag size is {0}".format(self.SIZE))
        self._data = value
        while len(self._data) < self.SIZE:
            self._data += b'\x00'

    def __str__(self):
        return str(self.data).strip('\x00')

    def __len__(self):
        return len(self._data)


class Prefix(object):
    """The prefix of a ControlHost message."""
    SIZE = 16

    def __init__(self, tag=None, length=None, data=None):
        if data:
            self.data = data
        else:
            self.tag = Tag(tag)
            self.length = length

    @property
    def data(self):
        return self.tag.data + struct.pack('>i', self.length) + b'\x00'*4

    @data.setter
    def data(self, value):
        self.tag = Tag(data=value[:Tag.SIZE])
        self.length = struct.unpack('>i', value[Tag.SIZE:Tag.SIZE+4])[0]

    def __str__(self):
        return ("ControlHost Prefix with tag '{0}' ({1} bytes of data)"
                .format(self.tag, self.length))

