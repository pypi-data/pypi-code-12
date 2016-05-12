# encoding: utf-8

from abc import ABCMeta, abstractmethod

from communication.server.protocol.protocol import ProtocolMessage

__author__ = 'Yonka'


class AbstractFramer(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def frame_msg(self, message: ProtocolMessage):
        pass

    @abstractmethod
    def next_msg(self) -> ProtocolMessage:
        pass
