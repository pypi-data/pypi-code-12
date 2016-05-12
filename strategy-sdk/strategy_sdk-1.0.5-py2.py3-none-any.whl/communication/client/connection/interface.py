# encoding: utf-8

from abc import ABCMeta, abstractmethod

from communication.server.protocol.protocol import ProtocolMessage

__author__ = 'Yonka'


class AbstractBaseConn(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def read(self) -> ProtocolMessage:
        pass

    @abstractmethod
    def write(self, protocol_message: ProtocolMessage) -> bool:
        pass

    @abstractmethod
    def is_open(self) -> bool:
        pass

    @abstractmethod
    def close(self):
        pass
