# encoding: utf-8
from __future__ import with_statement
from __future__ import absolute_import
import logging
import threading
from sd.communication.client.connection.interface import AbstractBaseConn

from sd.communication.client.protocol.protocol import LengthFramer
from sd.utils.io.io import SocketIO

__author__ = u'Yonka'


class BaseConn(AbstractBaseConn):
    def __init__(
            self,
            s
    ):
        self.s = s
        # isOpen rather than open to avoid conflicting with key word open
        self.isOpen = True
        input_stream = SocketIO(s, u"rw")  # python does not separate input and output interface
        self.framer = LengthFramer(input_stream)
        self._lock = threading.Lock()

    def close(self):
        with self._lock:
            if self.s is not None:
                try:
                    self.s.close()
                except Exception, e:
                    logging.error(u"close, exception: %s", e)
                self.s = None
            self.isOpen = False

    def write(self, protocol_message):
        result = False
        if not self.isOpen:
            return result
        try:
            self.framer.frame_msg(protocol_message)
            result = True
        except Exception, e:
            logging.error(u"Write message error: %s", e, exc_info=True)
            self.close()
        return result

    def read(self):
        result = None
        if not self.isOpen:
            return result
        try:
            result = self.framer.next_msg()
        except Exception, e:
            logging.error(u"Read message error: %s", e, exc_info=True)
            self.close()
        return result

    def is_open(self):
        return self.isOpen
