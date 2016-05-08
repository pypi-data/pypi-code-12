# encoding: utf-8

from abc import ABCMeta, abstractmethod

from communication.server.protocol.interface import AbstractProtocolMessage
from strategy.request import RequestInfo, ResponseInfo

__author__ = 'Yonka'


class AbstractAsyncMessageHandler(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def handle_async_message(self, async_message: AbstractProtocolMessage):
        pass


class AbstractStrategyClient(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def sync_rpc(self, request_info: RequestInfo) -> ResponseInfo:
        pass

    @abstractmethod
    def async_rpc(self, request_info: RequestInfo) -> bool:
        pass

    @abstractmethod
    def is_open(self) -> bool:
        pass

    @abstractmethod
    def close(self) -> bool:
        return

    @abstractmethod
    def connect(self) -> bool:
        pass
