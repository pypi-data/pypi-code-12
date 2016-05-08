# encoding: utf-8

from abc import ABCMeta, abstractmethod

__author__ = 'Yonka'


class AbstractProtocolMessage(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def to_stream_bytes(self):
        pass
