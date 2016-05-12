# encoding: utf-8

from __future__ import absolute_import
from abc import ABCMeta, abstractmethod

__author__ = u'Yonka'


class AbstractFramer(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def frame_msg(self, message):
        pass

    @abstractmethod
    def next_msg(self):
        pass
