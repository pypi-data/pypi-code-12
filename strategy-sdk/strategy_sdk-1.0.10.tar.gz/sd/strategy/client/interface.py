# encoding: utf-8

from __future__ import absolute_import
from abc import ABCMeta, abstractmethod

__author__ = u'Yonka'


class AbstractAsyncMessageHandler(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def handle_async_message(self, async_message):
        pass


class AbstractStrategyClient(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def sync_rpc(self, request_info):
        pass

    @abstractmethod
    def async_rpc(self, request_info):
        pass

    @abstractmethod
    def is_open(self):
        pass

    @abstractmethod
    def close(self):
        return

    @abstractmethod
    def connect(self):
        pass
