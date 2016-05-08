# encoding: utf-8
import logging
import socket
import threading

from communication.client.connection.interface import AbstractBaseConn
from communication.client.protocol.protocol import LengthFramer
from communication.server.protocol.protocol import ProtocolMessage


__author__ = 'Yonka'


class BaseConn(AbstractBaseConn):
    def __init__(
            self,
            s: socket.socket
    ):
        self.s = s
        # isOpen rather than open to avoid conflicting with key word open
        self.isOpen = True
        input_stream = socket.SocketIO(s, "rw")  # python does not separate input and output interface
        self.framer = LengthFramer(input_stream)
        self._lock = threading.Lock()

    def close(self):
        with self._lock:
            if self.s is not None:
                try:
                    self.s.close()
                except Exception as e:
                    logging.error("close, exception: %s", e)
                self.s = None
            self.isOpen = False

    def write(self, protocol_message: ProtocolMessage) -> bool:
        result = False
        if not self.isOpen:
            return result
        try:
            self.framer.frame_msg(protocol_message)
            result = True
        except Exception as e:
            logging.error("Write message error: %s", e, exc_info=True)
            self.close()
        return result

    def read(self) -> ProtocolMessage:
        result = None
        if not self.isOpen:
            return result
        try:
            result = self.framer.next_msg()
        except Exception as e:
            logging.error("Read message error: %s", e, exc_info=True)
            self.close()
        return result

    def is_open(self) -> bool:
        return self.isOpen
