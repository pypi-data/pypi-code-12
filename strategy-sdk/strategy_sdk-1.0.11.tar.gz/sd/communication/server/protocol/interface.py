# encoding: utf-8

from __future__ import absolute_import
from abc import ABCMeta, abstractmethod

__author__ = u'Yonka'


class AbstractProtocolMessage(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def to_stream_bytes(self):
        pass
