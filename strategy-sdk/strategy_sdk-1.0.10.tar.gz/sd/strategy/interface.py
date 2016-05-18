from __future__ import absolute_import
from abc import ABCMeta, abstractmethod
import unittest

__author__ = u'Yonka'


class AbstractStrategy(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def req_login(self, conn_info):
        pass

    @abstractmethod
    def req_subscribe(self, symbol):
        pass

    @abstractmethod
    def req_subscribe(self, dateType, symbol):
        pass

    @abstractmethod
    def req_unsubscribe(self, symbol):
        pass

    @abstractmethod
    def req_stock_tick(self, symbol=None, beginDate=-1, beginTime=-1, endDate=-1, endTime=-1):
        pass

    @abstractmethod
    def req_future_tick(self, symbol=None, beginDate=-1, beginTime=-1, endDate=-1, endTime=-1, autoFill=0):
        pass

    @abstractmethod
    def req_kline(self, symbol=None, dateType=None, cycDef=1, beginDate=-1, beginTime=-1, endDate=-1, endTime=-1,
                  autoFill=0, cqFlag=0, cqDate=-1, qjFlag=0):
        pass

    @abstractmethod
    def req_account_detail(self, strategy_id):
        pass

    @abstractmethod
    def req_position_statics(self, strategy_id):
        pass

    @abstractmethod
    def req_order_list(self, strategy_id):
        pass

    @abstractmethod
    def req_order(self, order_info):
        pass

    @abstractmethod
    def req_future_order(self, symbol, operation, price_type, price, volume, strategy_id, hedge_type):
        pass

    @abstractmethod
    def req_stock_order(self, symbol, operation, price_type, price, volume, strategy_id):
        pass

    @abstractmethod
    def req_order(self, symbol, operation, price_type, price, volume, strategy_id, hedge_type, interface_type):
        pass

    @abstractmethod
    def req_cancel_order(self, order_id):
        pass


class AbstractNotifyMessageHandler(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def on_notify_order_detail(self, order_detail):
        pass

    @abstractmethod
    def on_notify_trade_detail(self, trade_detail):
        pass

    @abstractmethod
    def on_notify_order_error(self, order_error):
        pass

    @abstractmethod
    def on_notify_cancel_error(self, order_cancel_error):
        pass

    @abstractmethod
    def on_notify_quote(self, dataType, data):
        pass


class TestAbsCls(unittest.TestCase):
    def test_instantiate(self):
        class TCls(AbstractStrategy):
            pass

        TCls()
