# encoding: utf-8
from __future__ import absolute_import
import unittest

from sd.utils.enum import EnumMetaCls, CommonNameValueEnum, can_not_init

__author__ = u'yonka'


class InterfaceType(CommonNameValueEnum):
    __metaclass__ = EnumMetaCls

    def __str__(self):
        return u"InterfaceType(%d)" % self.v


InterfaceType.INTERFACE_FUTURE = InterfaceType("1")
InterfaceType.INTERFACE_OPTION = InterfaceType("2")
InterfaceType.INTERFACE_STOCK = InterfaceType("3")

InterfaceType.__init__ = can_not_init


class OperationType(CommonNameValueEnum):
    __metaclass__ = EnumMetaCls

    def __str__(self):
        return u"OperationType(%d)" % self.v


OperationType.OPT_INVALID = OperationType(-1)
OperationType.OPT_OPEN_LONG = OperationType(0)#---support
OperationType.OPT_CLOSE_LONG_HISTORY = OperationType(1)#---support
OperationType.OPT_CLOSE_LONG_TODAY = OperationType(2)#---support
OperationType.OPT_OPEN_SHORT = OperationType(3)#---support
OperationType.OPT_CLOSE_SHORT_HISTORY = OperationType(4)#---support
OperationType.OPT_CLOSE_SHORT_TODAY = OperationType(5)#---support
OperationType.OPT_CLOSE_LONG_TODAY_FIRST = OperationType(6)
OperationType.OPT_CLOSE_LONG_HISTORY_FIRST = OperationType(7)
OperationType.OPT_CLOSE_SHORT_TODAY_FIRST = OperationType(8)
OperationType.OPT_CLOSE_SHORT_HISTORY_FIRST = OperationType(9)
OperationType.OPT_CLOSE_LONG_TODAY_HISTORY_THEN_OPEN_SHORT = OperationType(10)
OperationType.OPT_CLOSE_LONG_HISTORY_TODAY_THEN_OPEN_SHORT = OperationType(11)
OperationType.OPT_CLOSE_SHORT_TODAY_HISTORY_THEN_OPEN_LONG = OperationType(12)
OperationType.OPT_CLOSE_SHORT_HISTORY_TODAY_THEN_OPEN_LONG = OperationType(13)
OperationType.OPT_CLOSE_LONG = OperationType(14)#---support
OperationType.OPT_CLOSE_SHORT = OperationType(15)#---support
OperationType.OPT_OPEN = OperationType(16)
OperationType.OPT_CLOSE = OperationType(17)
# ############# 以上是期货的操作
# ############# 以下是股票的操作
OperationType.OPT_BUY = OperationType(18)#---support
OperationType.OPT_SELL = OperationType(19)#---support
OperationType.OPT_FIN_BUY = OperationType(20)
OperationType.OPT_SLO_SELL = OperationType(21)
OperationType.OPT_BUY_SECU_REPAY = OperationType(22)
OperationType.OPT_DIRECT_SECU_REPAY = OperationType(23)
OperationType.OPT_SELL_CASH_REPAY = OperationType(24)
OperationType.OPT_DIRECT_CASH_REPAY = OperationType(25)
OperationType._C_OPT_COUNT = OperationType(26)

OperationType.__init__ = can_not_init


class PriceType(CommonNameValueEnum):
    __metaclass__ = EnumMetaCls

    def __str__(self):
        return u"PriceType(%d)" % self.v


PriceType.PRTP_INVALID = PriceType(-1)
PriceType.PRTP_SALE5 = PriceType(0)
PriceType.PRTP_SALE4 = PriceType(1)
PriceType.PRTP_SALE3 = PriceType(2)
PriceType.PRTP_SALE2 = PriceType(3)
PriceType.PRTP_SALE1 = PriceType(4)
PriceType.PRTP_LATEST = PriceType(5)
PriceType.PRTP_BUY1 = PriceType(6)
PriceType.PRTP_BUY2 = PriceType(7)
PriceType.PRTP_BUY3 = PriceType(8)
PriceType.PRTP_BUY4 = PriceType(9)
PriceType.PRTP_BUY5 = PriceType(10)
PriceType.PRTP_FIX = PriceType(11)
PriceType.PRTP_MARKET = PriceType(12)
PriceType.PRTP_HANG = PriceType(13)
PriceType.PRTP_COMPETE = PriceType(14)
PriceType._C_PRTP_COUNT = PriceType(15)

PriceType.__init__ = can_not_init


# class QuoteDataType(CommonNameValueEnum):
# __metaclass__ = EnumMetaCls
#
# def __str__(self):
#         return u"QuoteDataType(%d)" % self.v

# #LEVEL 1 tick级别行情
# QuoteDataType.TICK_LEVEL_ONE_STOCK=0    #股票tick行情
# QuoteDataType.TICK_LEVEL_ONE_FUTURE=QuoteDataType(1)    #期货tick行情
# QuoteDataType.TICK_LEVEL_ONE_OPTION=QuoteDataType(2)    #期权tick行情
# #LEVEL 2 tick级别行情
# QuoteDataType.TICK_LEVEL_TWO_STOCK=QuoteDataType(10) #    //股票tick行情
# QuoteDataType.TICK_LEVEL_TWO_FUTURE=QuoteDataType(12)#,   //期货tick行情
# QuoteDataType.TICK_LEVEL_TWO_OPTION=QuoteDataType(13)#,   //期权tick
#
# QuoteDataType.KLINE=QuoteDataType(20)
#
# QuoteDataType.TRANSACTION=QuoteDataType(30)
# QuoteDataType.ORDER=QuoteDataType(40)#,//订单成交
# QuoteDataType.ORDER_QUEUE=QuoteDataType(50)#,//订单队列
#
#
# QuoteDataType.SAMPLE_DATA_BEGIN=QuoteDataType(100)#,
# QuoteDataType.SAMPLE_DATA_SECOND=QuoteDataType(101)#,//采样数据（采样的类型通过请求参数确定,通过采样种类，采样间隔，是否填充来决定）
# QuoteDataType.SAMPLE_DATA_MINUTE=QuoteDataType(102)#,//采样数据（采样的类型通过请求参数确定,通过采样种类，采样间隔，是否填充来决定）
# QuoteDataType.SAMPLE_DATA_DAY=QuoteDataType(103)#,//采样数据（采样的类型通过请求参数确定,通过采样种类，采样间隔，是否填充来决定）
# QuoteDataType.SAMPLE_DATA_WEEK=QuoteDataType(104)#,//采样数据（采样的类型通过请求参数确定,通过采样种类，采样间隔，是否填充来决定）
# QuoteDataType.SAMPLE_DATA_MONTH=QuoteDataType(105)#,//采样数据（采样的类型通过请求参数确定,通过采样种类，采样间隔，是否填充来决定）
# QuoteDataType.SAMPLE_DATA_SEASON=QuoteDataType(106)#,//采样数据（采样的类型通过请求参数确定,通过采样种类，采样间隔，是否填充来决定）
# QuoteDataType.SAMPLE_DATA_YEAR=QuoteDataType(107)#,//采样数据（采样的类型通过请求参数确定,通过采样种类，采样间隔，是否填充来决定）
# QuoteDataType.SAMPLE_DATA_END=QuoteDataType(200)

# QuoteDataType.__init__ = can_not_init


class QuoteMarket(CommonNameValueEnum):
    __metaclass__ = EnumMetaCls

    def __str__(self):
        return u"QuoteMarket(%d)" % self.v


QuoteMarket.SHFE = QuoteMarket(0)
QuoteMarket.DCE = QuoteMarket(4)
QuoteMarket.CZCE = QuoteMarket(6)
QuoteMarket.CFFEX = QuoteMarket(8)
QuoteMarket.SHSE = QuoteMarket(101)
QuoteMarket.SZSE = QuoteMarket(102)

QuoteMarket.__init__ = can_not_init


class TestEnum(unittest.TestCase):
    def test_init_interface_type(self):
        print InterfaceType.INTERFACE_FUTURE
        res = False
        try:
            InterfaceType(1)
        except AssertionError:
            res = True
        assert res

    def test_init_operation_type(self):
        print OperationType.OPT_INVALID
        res = False
        try:
            OperationType(1)
        except AssertionError:
            res = True
        assert res

    def test_init_price_type(self):
        print PriceType.PRTP_INVALID
        res = False
        try:
            PriceType(1)
        except AssertionError:
            res = True
        assert res

    def test_init_quote_data_type(self):
        print QuoteDataType.TICK_FIVE_LEVEL
        res = False
        try:
            QuoteDataType(0)
        except AssertionError:
            res = True
        assert res

    def test_init_quote_market(self):
        print QuoteMarket.SHFE
        res = False
        try:
            QuoteMarket(0)
        except AssertionError:
            res = True
        assert res
