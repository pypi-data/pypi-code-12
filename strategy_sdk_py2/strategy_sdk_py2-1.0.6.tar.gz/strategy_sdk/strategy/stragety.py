# encoding: utf-8
from __future__ import with_statement
from __future__ import absolute_import
import logging
import os
import threading
import time
import sys
import unittest

from agent.agent_type import AgentType
from communication.server.protocol import function_code
from data.common.enum import HedgeFlagType
from exception import StrategyErrorCode
from exception.exception import ConnectionBrokenException
from strategy.bean import protoquote
from strategy.bean.bean import StrategyOrderDetail, StrategyOrderError, StrategyError, StrategyAccountDetail, \
    StrategyPositionStatics, \
    StrategyRequestOrder, \
    StrategyConnectionInfo, StrategyConfiguration, StrategyQuoteDataRequest
from strategy.bean.databean import KlineBean, TickBean
from strategy.bean.enum import PriceType, InterfaceType, OperationType
from strategy.bean.datatype import *
from strategy.client.client import StrategyClient
from strategy.interface import AbstractStrategy, AbstractNotifyMessageHandler
from strategy.client.interface import AbstractAsyncMessageHandler
from strategy.request import RequestInfo, ResponseInfo
from utils import bean as utils_bean

__author__ = u'yonka'


class BaseStrategy(AbstractStrategy, AbstractNotifyMessageHandler, AbstractAsyncMessageHandler):
    DEFAULT_REQUEST_TIMEOUT = 20000

    def __init__(self, strategy_configuration):
        self.connClient = StrategyClient(
            strategy_configuration.host,
            strategy_configuration.port,
            strategy_configuration.readTimeout,
            strategy_configuration.connTimeout,
            self
        )
        self.requestId = int(time.time() * 1000)
        self.externalAsyncMessageHandler = None
        self.externalNotifyMessageHandler = self
        self.strategyConnectionInfo = strategy_configuration.strategyConnectionInfo
        self.autoReconnect = False
        self.login = False
        self.agentType = strategy_configuration.usageType
        self.reconnectLock = threading.Lock()
        self.finish = False

    def init(self):
        if self.connClient.connect():
            if self.default_req_login():
                self.login = True
            else:
                logging.warning(u"self.default_req_login() failed")
        else:
            logging.warning(u"self.connClient.connect() failed")
        return self.login

    def finish(self):
        self.finish = True

    def run(self, timeout=None):
        runtime = 0
        while (not self.finish):
            time.sleep(1)
            runtime += 1
            if (timeout is not None):
                if runtime >= timeout:
                    break

    def reconnect(self):
        with self.reconnectLock:
            if self.connClient.is_open() and self.login:
                return
            self.login = False
            self.connClient.close()
            if not self.init():
                raise RuntimeError(u"auth failed, pls check connection info")

    def _get_and_inc_req_id(self):
        self.requestId += 1
        return self.requestId

    def _build_request_info(self, timeout, fc):
        request_info = RequestInfo()
        request_info.fc = fc
        request_info.dataType = self.agentType
        request_info.timeout = timeout
        request_info.reqId = self._get_and_inc_req_id()
        return request_info

    @classmethod
    def _convert_2_strategy_error(cls, message):
        return StrategyError().from_json(message.body)

    @classmethod
    def _new_500_error(cls):
        return StrategyError(error_id=500, error_msg=u"system error when call reqQuoteData")

    @classmethod
    def _new_succeed_error(cls):
        return StrategyError(error_id=0, error_msg=u"ok")

    def _handle_request_exception(self, e, safe=True):
        try:
            if isinstance(e, ConnectionBrokenException):
                if self.autoReconnect:
                    self.reconnect()
                else:
                    raise e
            else:
                # XXX java code todo
                pass
        except Exception as e1:
            if safe:
                logging.exception("_handle_request_exception met error: %s", e)
            else:
                raise e1

    def default_req_login(self):
        return StrategyErrorCode.is_success(self.req_login(self.strategyConnectionInfo).errorId)

    def req_subscribe(self, symbol):
        try:
            request_info = self._build_request_info(self.DEFAULT_REQUEST_TIMEOUT, function_code.REQ_ST_SUBSCRIBE)
            request_info.data = symbol
            response_info = self.connClient.sync_rpc(request_info)
            return self._convert_2_strategy_error(response_info.protocolMessage)
        except StrategyError as se:
            return se
        except Exception as e:
            logging.exception("%s", e)
            self._handle_request_exception(e)
            return self._new_500_error()

    def req_order_list(self, strategy_id):
        result = None
        err = self._new_succeed_error()
        try:
            request_info = self._build_request_info(self.DEFAULT_REQUEST_TIMEOUT, function_code.REQ_ST_ORDERLIST)
            request_info.data = strategy_id
            response_info = self.connClient.sync_rpc(request_info)
            data = response_info.data
            if response_info.is_success():
                result = utils_bean.json_load_bean_list(data, StrategyOrderDetail)
            else:
                err = StrategyError().from_json(data)
        except StrategyError as se:
            logging.exception("%s", se)
            err = se
        except Exception as e:
            logging.exception("%s", e)
            self._handle_request_exception(e)
            err = self._new_500_error()
        return result, err

    def req_account_detail(self, strategy_id):
        result = None
        err = self._new_succeed_error()
        try:
            request_info = self._build_request_info(self.DEFAULT_REQUEST_TIMEOUT, function_code.REQ_ST_ACCOUNTETAIL)
            request_info.data = strategy_id
            response_info = self.connClient.sync_rpc(request_info)
            data = response_info.data
            if response_info.is_success():
                result = utils_bean.json_load_bean_list(data, StrategyAccountDetail)
            else:
                err = StrategyError().from_json(data)
        except StrategyError as se:
            logging.exception("%s", se)
            err = se
        except Exception as e:
            logging.exception("%s", e)
            self._handle_request_exception(e)
            err = self._new_500_error()
        return result, err

    def req_position_statics(self, strategy_id):
        result = None
        err = self._new_succeed_error()
        try:
            request_info = self._build_request_info(self.DEFAULT_REQUEST_TIMEOUT, function_code.REQ_ST_POTITIONDSTATICS)
            request_info.data = strategy_id
            response_info = self.connClient.sync_rpc(request_info)
            data = response_info.data
            if response_info.is_success():
                result = utils_bean.json_load_bean_list(data, StrategyPositionStatics)
            else:
                err = StrategyError().from_json(data)
        except StrategyError as se:
            logging.exception("%s", se)
            err = se
        except Exception as e:
            logging.exception("%s", e)
            self._handle_request_exception(e)
            err = self._new_500_error()
        return result, err

    def req_cancel_order(self, cancel_order_info):
        return None

    def req_stock_tick(self, symbol=None, begin_date=-1, begin_time=-1, end_date=-1, end_time=-1):
        req_data = StrategyQuoteDataRequest(market="", symbol=symbol, dateType=TICK_STOCK, beginDate=begin_date,
                                            endDate=end_date, beginTime=begin_time, endTime=end_time)
        return self.req_quota_data(req_data)

    def req_future_tick(self, symbol=None, begin_date=-1, begin_time=-1, end_date=-1, end_time=-1, auto_fill=0):
        req_data = StrategyQuoteDataRequest(market="", symbol=symbol, dateType=TICK_FUTURE,
                                            beginDate=begin_date, endDate=end_date, beginTime=begin_time,
                                            endTime=end_time,
                                            autoFill=auto_fill)
        return self.req_quota_data(req_data)

    def req_kline(self, symbol=None, data_type=None, cyc_def=1, begin_date=-1, begin_time=-1, end_date=-1, end_ime=-1,
                  auto_fill=0, cq_flag=0, cq_date=-1, qj_flag=0):
        req_data = StrategyQuoteDataRequest(market="", symbol=symbol, dataType=data_type, cycCount=cyc_def,
                                            beginDate=begin_date, endDate=end_date, beginTime=begin_time,
                                            endTime=end_ime,
                                            autoFill=auto_fill, cqFlag=cq_flag, cqDate=cq_date, qjFlag=qj_flag)
        return self.req_quota_data(req_data)

    def req_quota_data(self, quote_data_category):
        result = None
        err = self._new_succeed_error()
        logging.info("Request data:%s", quote_data_category.to_json())
        try:
            request_info = self._build_request_info(self.DEFAULT_REQUEST_TIMEOUT, function_code.REQ_ST_DATA)
            request_info.data = quote_data_category.to_json()
            response_info = self.connClient.sync_rpc(request_info)
            data = response_info.protocolMessage.byteBody
            data_type = quote_data_category.dataType
            if response_info.is_success():
                if data_type == TICK_STOCK or data_type == TICK_STOCK:
                    result = utils_bean.history_data_proto_2_bean_list(data, protoquote.TickBean, TickBean)
                elif data_type == TICK_FUTURE:
                    result = utils_bean.history_data_proto_2_bean_list(data, protoquote.TickBean, TickBean)
                elif SAMPLE_DATA_END > data_type > SAMPLE_DATA_BEGIN:
                    result = utils_bean.history_data_proto_2_bean_list(data, protoquote.KLineBean, KlineBean)
            else:
                err = StrategyError().from_json(data)
        except StrategyError as se:
            logging.exception("%s", se)
            err = se
        except Exception as e:
            logging.exception("%s", e)
            self._handle_request_exception(e)
            err = self._new_500_error()
        return result, err

    # def req_position_detail(self, strategy_id: str) -> (List[StrategyPositionDetail], StrategyError):
    # result = None
    # err = None
    # try:
    #         request_info = self._build_request_info(self.DEFAULT_REQUEST_TIMEOUT, function_code.REQ_ST_POTITIONDETAIL)
    #         request_info.data = strategy_id
    #         response_info = self.connClient.sync_rpc(request_info)
    #         data = response_info.data
    #         if response_info.is_success():
    #             result = utils_bean.json_load_bean_list(data, StrategyPositionDetail)
    #         else:
    #             err = StrategyError().from_json(data)
    #     except StrategyError as se:
    #         logging.exception("%s", se)
    #         err = se
    #     except Exception as e:
    #         logging.exception("%s", e)
    #         self._handle_request_exception(e)
    #         err = self._new_500_error()
    #     return result, err
    def req_future_order(self, symbol=None, operation=None, price_type=None, price=None, volume=None, strategy_id=None,
                         hedge_type=HedgeFlagType.HEDGE_FLAG_HEDGE):
        if strategy_id is None:
            strategy_id = self.strategyConnectionInfo.strategyId
        return self.req_order(symbol, operation, price_type, price, volume, strategy_id, hedge_type,
                              InterfaceType.INTERFACE_FUTURE)

    def req_stock_order(self, symbol, operation, price_type, price, volume, strategy_id):
        if strategy_id is None:
            strategy_id = self.strategyConnectionInfo.strategyId
        return self.req_order(symbol, operation, price_type, price, volume, strategy_id, InterfaceType.INTERFACE_STOCK)

    def req_order(self, symbol, operation, price_type, price, volume, strategy_id, interface_type):
        order = StrategyRequestOrder(price=price, price_type=price_type, instrument=symbol,
                                     order_operation_type=operation, interface_type=interface_type,
                                     strategy_id=strategy_id, volume=volume)
        return self.req_order(order)

    def req_order(self, order_info):
        result = None
        err = self._new_succeed_error()
        logging.debug("Requested order info:%s", order_info.to_json())
        try:
            request_info = self._build_request_info(self.DEFAULT_REQUEST_TIMEOUT, function_code.REQ_ST_ORDER)
            order_info.strategyClientID = os.getpid()  # XXX 是不是这个？
            request_info.data = order_info.to_json()
            response_info = self.connClient.sync_rpc(request_info)
            data = response_info.data
            if response_info.is_success():
                result = data
                logging.info("response order: ", data)
            else:
                err = StrategyError().from_json(data)
        except StrategyError as se:
            logging.exception("%s", se)
            err = se
        except Exception as e:
            logging.exception("%s", e)
            self._handle_request_exception(e)
        return result, err

    def req_unsubscribe(self, symbol):
        try:
            request_info = self._build_request_info(self.DEFAULT_REQUEST_TIMEOUT, function_code.REQ_ST_UNSUBSCRIBE)
            request_info.data = symbol
            response_info = self.connClient.sync_rpc(request_info)
            return self._convert_2_strategy_error(response_info.protocolMessage)
        except StrategyError as se:
            logging.exception("%s", se)
            return se
        except Exception as e:
            logging.exception("%s", e)
            self._handle_request_exception(e)
            return self._new_500_error()

    def req_login(self, conn_info):
        try:
            request_info = self._build_request_info(self.DEFAULT_REQUEST_TIMEOUT, function_code.STRATEGYLOGIN)
            conn_info.strategyClientID = os.getpid()  # XXX 确定是不是要这个？
            # XXX 把时间类型转为 "yyyy-MM-dd HH:mm:ss" 格式，但StrategyConnectionInfo没有时间类型啊，囧...
            data = conn_info.to_json()
            request_info.data = data
            response_info = self.connClient.sync_rpc(request_info)
            err = self._convert_2_strategy_error(response_info.protocolMessage)
            if err.errorId == 0:
                logging.info(u"请求连接成功，err is %s", err.to_json())
            else:
                logging.exception(u"请求连接失败，err is %s", err.to_json())
                sys.exit(1)
            return err
        except StrategyError as se:
            logging.exception("%s", se)
            return se
        except Exception as e:
            logging.exception("%s", e)
            return self._new_500_error()

    def on_notify_trade_detail(self, trade_detail):
        pass

    def on_notify_order_error(self, order_error):
        pass

    def on_notify_order_detail(self, order_detail):
        pass

    def on_notify_quote(self, dataType, data):
        pass

    def on_notify_cancel_error(self, order_cancel_error):
        pass

    def handle_async_message(self, async_message):
        def notify_st_subscribe_handler(self, async_message):
            try:
                response_info = ResponseInfo(protocol_message=async_message)
                data = None
                if response_info.dataType == TICK_FUTURE or response_info.dataType == TICK_STOCK:
                    data = utils_bean.proto_to_bean(response_info.data, protoquote.TickBean, TickBean)
                elif SAMPLE_DATA_BEGIN < response_info.dataType < SAMPLE_DATA_END:
                    data = utils_bean.proto_to_bean(response_info.data, protoquote.KLineBean, KlineBean)
                elif KLINE < response_info.dataType < KLINE_END:
                    data = utils_bean.proto_to_bean(response_info.data, protoquote.KLineBean, KlineBean)
                if data:
                    self.externalNotifyMessageHandler.on_notify_quote(response_info.dataType, data)
            except Exception, e:
                logging.exception(u"%s", e)

        def notify_st_orderdetail_handler(self, async_message):
            try:
                logging.debug(u"return orderdetail: %s", async_message.body)
                strategy_order_detail = StrategyOrderDetail().from_json(async_message.body)
                self.externalNotifyMessageHandler.on_notify_order_detail(strategy_order_detail)
            except Exception, e:
                logging.exception(u"%s", e)

        def notify_st_ordererror_handler(self, async_message):
            try:
                strategy_order_error = StrategyOrderError().from_json(async_message.body)
                self.externalNotifyMessageHandler.on_notify_order_error(strategy_order_error)
            except Exception, e:
                logging.exception(u"%s", e)

        def notify_st_unsubscribe_handler(self, async_message):
            try:
                logging.info(u"成功取消订阅： %s", async_message.body)
            except Exception:
                # XXX java代码里todo，处理exception
                pass

        _base_handlers = {
            function_code.NOTIFY_ST_SUBSCRIBE: notify_st_subscribe_handler,
            function_code.NOTIFY_ST_ORDERDETAIL: notify_st_orderdetail_handler,
            function_code.NOTIFY_ST_ORDERERROR: notify_st_ordererror_handler,
            function_code.NOTIFY_ST_UNSUBSCRIBE: notify_st_unsubscribe_handler
        }

        def _base_handle_async_message(self, async_message):
            handler = _base_handlers.get(async_message.fc)
            if handler is not None:
                handler(self, async_message)

        if self.externalAsyncMessageHandler is not None:
            self.externalAsyncMessageHandler.handle_async_message(self, async_message)
        else:
            _base_handle_async_message(self, async_message)


class SimpleStrategy(AbstractStrategy, AbstractNotifyMessageHandler):
    def __init__(
            self,
            quote_config,
            trader_config,
    ):
        self.quoteStrategy = BaseStrategy(quote_config)
        self.traderStrategy = BaseStrategy(trader_config)

    def init(self):
        success = False
        for name, strategy in [(u"trader", self.traderStrategy), (u"quote", self.quoteStrategy)]:
            if strategy is not None:
                try:
                    success = strategy.init()
                    if success:
                        logging.info(u"%s connection login succeed", name)
                    else:
                        logging.exception(u"%s connection failed.....", name)
                except Exception, e:
                    logging.exception(u"login failed, e is %s", e)
                    return False
        return success

    def req_account_detail(self, strategy_id=None):
        return self.traderStrategy.req_account_detail(strategy_id)

    def req_stock_tick(self, symbol=None, beginDate=-1, beginTime=-1, endDate=-1, endTime=-1):
        return self.quoteStrategy.req_stock_tick(symbol, beginDate, beginTime, endDate, endTime)

    def req_future_tick(self, symbol=None, beginDate=-1, beginTime=-1, endDate=-1, endTime=-1, autoFill=0):
        return self.quoteStrategy.req_future_tick(symbol, beginDate, beginTime, endDate, endTime)

    def req_kline(self, symbol=None, dataType=None, cycDef=1, beginDate=-1, beginTime=-1, endDate=-1, endTime=-1,
                  autoFill=0, cqFlag=0, cqDate=-1, qjFlag=0):
        return self.quoteStrategy.req_kline(symbol, dataType, cycDef, beginDate, beginTime, endDate, endTime, autoFill,
                                            cqFlag, cqDate, qjFlag)

    def req_order_list(self, strategy_id=None):
        return self.traderStrategy.req_order_list(strategy_id)

    def req_order(self, order_info):
        return self.traderStrategy.req_order(order_info)

    def req_future_order(self, symbol=None, operation=None, price_type=None, price=None, volume=None, strategy_id=None,
                         hedge_type=HedgeFlagType.HEDGE_FLAG_HEDGE):
        return self.traderStrategy.req_order(symbol, operation, price_type, price, volume, strategy_id, hedge_type)

    def req_stock_order(self, symbol, operation, price_type, price, volume, strategy_id):
        return self.traderStrategy.req_order(symbol, operation, price_type, price, volume, strategy_id,
                                             InterfaceType.INTERFACE_STOCK)

    def req_order(self, symbol, operation, price_type, price, volume, strategy_id, interface_type):
        return self.traderStrategy.req_order(symbol, operation, price_type, price, volume, strategy_id, interface_type)

    def req_login(self, conn_info):
        self.traderStrategy.req_login(conn_info)
        err = self.quoteStrategy.req_login(conn_info)
        logging.info("req_login, err is ", err.to_json())
        return err

    def req_subscribe(self, symbol):
        return self.quoteStrategy.req_subscribe(symbol)

    def req_position_statics(self, strategy_id=None):
        return self.traderStrategy.req_position_statics(strategy_id)

    def req_cancel_order(self, cancel_order_info):
        return self.traderStrategy.req_cancel_order(cancel_order_info)

    def req_position_detail(self, strategy_id=None):
        return self.traderStrategy.req_position_detail(strategy_id)

    def req_unsubscribe(self, symbol):
        return self.quoteStrategy.req_unsubscribe(symbol)

    def on_notify_order_error(self, order_error):
        logging.exception("order_error: ", order_error.to_json())

    def on_notify_trade_detail(self, trade_detail):
        print(trade_detail)

    def on_notify_order_detail(self, order_detail):
        logging.info("order detail: %s", order_detail)

    def on_notify_cancel_error(self, order_cancel_error):
        print(order_cancel_error)

    def on_notify_quote(self, dataType, data):
        pass

    def run(self):
        while (True):
            time.sleep(1000)


class TestStrategy(unittest.TestCase):
    # trader_port = 8280
    trader_port = 8080
    # quote_port = 8380
    quote_port = 8180
    trader_addr = u"101.200.228.73"
    quote_addr = u"101.200.228.73"

    @unittest.skip(u"")
    def test_quote_strategy(self):
        logging.basicConfig(format=u'%(asctime)s %(message)s', datefmt=u'%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
        quote_conn_info = StrategyConnectionInfo(
            account_id=u"016860",
            strategy_id=u"1",
            tcfs=AgentType.QUOTE
        )
        quote_config = StrategyConfiguration(
            self.quote_addr, self.quote_port, strategy_connection_info=quote_conn_info)

        quote_strategy = BaseStrategy(quote_config)
        quote_strategy.init()

        time.sleep(1000)

    def test_simple_strategy(self):
        logging.basicConfig(format=u'%(asctime)s %(message)s', datefmt=u'%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
        trader_conn_info = StrategyConnectionInfo(
            ip=u"101.200.228.73",
            port=unicode(self.trader_port),
            account_id=u"016860",
            password=u"96e79218965eb72c92a549dd5a330112",
            strategy_id=u"1",
            tcfs=AgentType.TRADE
        )
        trader_config = StrategyConfiguration(
            self.trader_addr, self.trader_port, strategy_connection_info=trader_conn_info)
        quote_conn_info = StrategyConnectionInfo(
            account_id=u"016860",
            strategy_id=u"1",
            tcfs=AgentType.QUOTE
        )
        quote_config = StrategyConfiguration(
            self.quote_addr, self.quote_port, strategy_connection_info=quote_conn_info)

        simple_strategy = SimpleStrategy(quote_config, trader_config)
        simple_strategy.init()

        order_info = StrategyRequestOrder(
            account_id=u"016860",
            hedge_flag=HedgeFlagType.HEDGE_FLAG_HEDGE,
            market=u"SHFE",
            product=u"rb",
            price=2100,
            volume=1,
            instrument=u"rb1605",
            strategy_id=u"1",
            price_type=PriceType.PRTP_FIX,
            interface_type=InterfaceType.INTERFACE_FUTURE,
            order_operation_type=OperationType.OPT_CLOSE_SHORT_TODAY
        )

        # try:
        # data = simple_strategy.req_order(order_info)
        # logging.info("data is: %s", data)
        # except Exception as e:
        # logging.exception("e: %s", e)
        # raise e

        try:
            account_detail, err = simple_strategy.req_account_detail(u"1")
            logging.info(u"account_detail: %s", account_detail.to_json() if account_detail else account_detail)
        except Exception, e:
            logging.exception(u"e: %s", e)
            raise e

        # try:
        # position_detail, err = simple_strategy.req_position_detail(u"1")
        #     logging.info(u"position_detail: %s", position_detail.to_json() if position_detail else position_detail)
        # except Exception, e:
        #     logging.exception(u"e: %s", e)
        #     raise e

        try:
            position_statics, err = simple_strategy.req_position_statics(u"1")
            logging.info(u"position_detail: %s", position_statics.to_json() if position_statics else position_statics)
        except Exception, e:
            logging.exception(u"e: %s", e)
            raise e

        time.sleep(1000)
