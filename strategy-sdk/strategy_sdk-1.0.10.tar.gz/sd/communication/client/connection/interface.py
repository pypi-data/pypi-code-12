# encoding: utf-8

from __future__ import absolute_import
from abc import ABCMeta, abstractmethod

__author__ = u'Yonka'


class AbstractBaseConn(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def write(self, protocol_message):
        pass

    @abstractmethod
    def is_open(self):
        pass

    @abstractmethod
    def close(self):
        pass
