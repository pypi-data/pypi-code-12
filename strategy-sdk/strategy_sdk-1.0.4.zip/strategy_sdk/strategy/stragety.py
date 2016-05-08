# encoding: utf-8
import logging
import os
import threading
import time
import sys
from typing import List
import unittest

from agent.agent_type import AgentType
from communication.server.protocol import function_code
from communication.server.protocol.protocol import ProtocolMessage
from data.common.enum import HedgeFlagType
from exception import StrategyErrorCode
from exception.exception import ConnectionBrokenException
from strategy.bean.bean import StrategyTradeDetail, StrategyOrderDetail, StrategyOrderError, StrategyQuoteDataResult, \
    StrategyOrderCancelError, StrategyError, \
    StrategyOrderCancel, StrategyQuoteDataRequest, StrategyRequestOrder, \
    StrategyConnectionInfo, StrategyConfiguration, \
    StrategyPositionStatics, StrategyAccountDetail
from strategy.bean.databean import StockMarketBean, KlineBean
from strategy.bean.databean import FutureMarketBean
from strategy.bean.enum import PriceType, InterfaceType, OperationType
from strategy.bean import datatype
from strategy.client.client import StrategyClient
from strategy.interface import AbstractStrategy, AbstractNotifyMessageHandler
from strategy.client.interface import AbstractAsyncMessageHandler
from strategy.request import RequestInfo, ResponseInfo
from utils import bean as utils_bean


__author__ = 'yonka'


class BaseStrategy(AbstractStrategy, AbstractNotifyMessageHandler, AbstractAsyncMessageHandler):
    DEFAULT_REQUEST_TIMEOUT = 20000

    def __init__(self, strategy_configuration: StrategyConfiguration):
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

    def init(self) -> bool:
        if self.connClient.connect():
            if self.default_req_login():
                self.login = True
            else:
                logging.warning("self.default_req_login() failed")
        else:
            logging.warning("self.connClient.connect() failed")
        return self.login

    def finish(self):
        self.finish = True

    def run(self, timeout=None):
        runtime = 0
        while not self.finish:
            time.sleep(1)
            runtime += 1
            if timeout is not None:
                if runtime >= timeout:
                    break

    def reconnect(self):
        with self.reconnectLock:
            if self.connClient.is_open() and self.login:
                return
            self.login = False
            self.connClient.close()
            if not self.init():
                raise RuntimeError("auth failed, pls check connection info")

    def _get_and_inc_req_id(self):
        self.requestId += 1
        return self.requestId

    def _build_request_info(self, timeout: int, fc: int) -> RequestInfo:
        request_info = RequestInfo()
        request_info.fc = fc
        request_info.timeout = timeout
        request_info.dataType = self.agentType
        request_info.reqId = self._get_and_inc_req_id()
        return request_info

    @classmethod
    def _convert_2_strategy_error(cls, message: ProtocolMessage) -> StrategyError:
        return StrategyError().from_json(message.body)

    @classmethod
    def _new_500_error(cls) -> StrategyError:
        return StrategyError(error_id=500, error_msg="system error when call reqQuoteData")

    @classmethod
    def _new_succeed_error(cls) -> StrategyError:
        return StrategyError(error_id=0, error_msg="ok")

    def _handle_request_exception(self, e: Exception, safe: bool=True):
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

    def req_subscribe(self, symbol: str) -> StrategyError:
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

    def req_order_list(self, strategy_id: str) -> (List[StrategyOrderDetail], StrategyError):
        result = None
        err = None
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

    def req_account_detail(self, strategy_id: str) -> (List[StrategyAccountDetail], StrategyError):
        result = None
        err = None
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

    def req_position_statics(self, strategy_id: str) -> (List[StrategyPositionStatics], StrategyError):
        result = None
        err = None
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

    def req_cancel_order(self, cancel_order_info: StrategyOrderCancel) -> StrategyError:
        return None

    def req_stock_tick(self, symbol=None, beginDate: int=-1, beginTime: int=-1, endDate: int=-1, endTime: int=-1):
        reqData = StrategyQuoteDataRequest(market="", symbol=symbol, dateType=datatype.TICK_LEVEL_TWO_STOCK,
                                           beginDate=beginDate,
                                           endDate=endDate, beginTime=beginTime, endTime=endTime)

        return self.req_quota_data(reqData)

    def req_future_tick(self, symbol=None, beginDate: int=-1, beginTime: int=-1, endDate: int=-1, endTime: int=-1,
                        autoFill: int=0):
        reqData = StrategyQuoteDataRequest(market="", symbol=symbol, dateType=datatype.TICK_LEVEL_TWO_FUTURE,
                                           beginDate=beginDate, endDate=endDate, beginTime=beginTime, endTime=endTime,
                                           autoFill=autoFill)
        return self.req_quota_data(reqData)

    def req_kline(self, symbol=None, dataType: int=None, cycDef: int=1, beginDate: int=-1, beginTime: int=-1,
                  endDate: int=-1, endTime: int=-1, autoFill: int=0, cqFlag: int=0, cqDate: int=-1, qjFlag: int=0):
        reqData = StrategyQuoteDataRequest(market="", symbol=symbol, dataType=dataType, cycCount=cycDef,
                                           beginDate=beginDate, endDate=endDate, beginTime=beginTime, endTime=endTime,
                                           autoFill=autoFill, cqFlag=cqFlag, cqDate=cqDate, qjFlag=qjFlag)
        return self.req_quota_data(reqData)

    def req_quota_data(self, quote_data_category: StrategyQuoteDataRequest) -> (StrategyQuoteDataResult, StrategyError):
        result = None
        err = self._new_succeed_error()
        logging.info("Request data:%s", quote_data_category.to_json())
        try:
            request_info = self._build_request_info(self.DEFAULT_REQUEST_TIMEOUT, function_code.REQ_ST_DATA)
            request_info.data = quote_data_category.to_json()
            response_info = self.connClient.sync_rpc(request_info)
            data = response_info.data
            dataType = quote_data_category.dataType
            if response_info.is_success():
                if dataType == datatype.TICK_LEVEL_ONE_STOCK or dataType == datatype.TICK_LEVEL_TWO_STOCK:
                    result = utils_bean.json_load_bean_list(data, StockMarketBean)
                elif dataType == datatype.TICK_LEVEL_ONE_FUTURE or dataType == datatype.TICK_LEVEL_TWO_FUTURE:
                    result = utils_bean.json_load_bean_list(data, FutureMarketBean)
                elif datatype.SAMPLE_DATA_BEGIN < dataType < datatype.SAMPLE_DATA_END:
                    result = utils_bean.json_load_bean_list(data, KlineBean)
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
    # request_info = self._build_request_info(self.DEFAULT_REQUEST_TIMEOUT, function_code.REQ_ST_POTITIONDETAIL)
    # request_info.data = strategy_id
    # response_info = self.connClient.sync_rpc(request_info)
    # data = response_info.data
    # if response_info.is_success():
    # result = utils_bean.json_load_bean_list(data, StrategyPositionDetail)
    # else:
    # err = StrategyError().from_json(data)
    # except StrategyError as se:
    #         logging.exception("%s", se)
    #         err = se
    #     except Exception as e:
    #         logging.exception("%s", e)
    #         self._handle_request_exception(e)
    #         err = self._new_500_error()
    #     return result, err

    def req_order(self, order_info: StrategyRequestOrder) -> (str, StrategyError):
        result = None
        err = None
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

    def req_unsubscribe(self, symbol: str) -> StrategyError:
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

    def req_login(self, conn_info: StrategyConnectionInfo) -> StrategyError:
        try:
            request_info = self._build_request_info(self.DEFAULT_REQUEST_TIMEOUT, function_code.STRATEGYLOGIN)
            conn_info.strategyClientID = os.getpid()  # XXX 确定是不是要这个？
            # XXX 把时间类型转为 "yyyy-MM-dd HH:mm:ss" 格式，但StrategyConnectionInfo没有时间类型啊，囧...
            data = conn_info.to_json()
            request_info.data = data
            response_info = self.connClient.sync_rpc(request_info)
            err = self._convert_2_strategy_error(response_info.protocolMessage)
            if err.errorId == 0:
                logging.info("请求连接成功，err is %s", err.to_json())
            else:
                logging.exception("请求连接失败，err is %s", err.to_json())
                sys.exit(1)
            return err
        except StrategyError as se:
            logging.exception("%s", se)
            return se
        except Exception as e:
            logging.exception("%s", e)
            return self._new_500_error()

    def on_notify_trade_detail(self, trade_detail: StrategyTradeDetail):
        pass

    def on_notify_order_error(self, order_error: StrategyOrderError):
        pass

    def on_notify_order_detail(self, order_detail: StrategyOrderDetail):
        pass

    def on_notify_quote(self, dataType, data: StrategyQuoteDataResult):
        pass

    def on_notify_cancel_error(self, order_cancel_error: StrategyOrderCancelError):
        pass

    def handle_async_message(self, async_message: ProtocolMessage):
        def notify_st_subscribe_handler(self: BaseStrategy, async_message: ProtocolMessage):
            try:
                response_info = ResponseInfo(protocol_message=async_message)
                data = None
                if response_info.dataType == datatype.TICK_LEVEL_TWO_FUTURE or response_info.dataType == datatype.TICK_LEVEL_ONE_FUTURE:
                    data = FutureMarketBean().from_json(response_info.data)
                elif response_info.dataType == datatype.TICK_LEVEL_TWO_STOCK or response_info.dataType == datatype.TICK_LEVEL_ONE_STOCK:
                    data = StockMarketBean().from_json(response_info.data)
                elif datatype.SAMPLE_DATA_BEGIN < response_info.dataType < datatype.SAMPLE_DATA_END:
                    data = KlineBean().from_json(response_info.data)

                self.externalNotifyMessageHandler.on_notify_quote(response_info.dataType, data)
            except Exception as e:
                logging.exception("%s", e)

        def notify_st_orderdetail_handler(self: BaseStrategy, async_message: ProtocolMessage):
            try:
                logging.debug("return orderdetail: %s", async_message.body)
                strategy_order_detail = StrategyOrderDetail().from_json(async_message.body)
                self.externalNotifyMessageHandler.on_notify_order_detail(strategy_order_detail)
            except Exception as e:
                logging.exception("%s", e)

        def notify_st_ordererror_handler(self: BaseStrategy, async_message: ProtocolMessage):
            try:
                strategy_order_error = StrategyOrderError().from_json(async_message.body)
                self.externalNotifyMessageHandler.on_notify_order_error(strategy_order_error)
            except Exception as e:
                logging.exception("%s", e)

        def notify_st_unsubscribe_handler(self: BaseStrategy, async_message: ProtocolMessage):
            try:
                logging.info("成功取消订阅： %s", async_message.body)
            except Exception:
                # XXX java代码里todo，处理exception
                pass

        _base_handlers = {
            function_code.NOTIFY_ST_SUBSCRIBE: notify_st_subscribe_handler,
            function_code.NOTIFY_ST_ORDERDETAIL: notify_st_orderdetail_handler,
            function_code.NOTIFY_ST_ORDERERROR: notify_st_ordererror_handler,
            function_code.NOTIFY_ST_UNSUBSCRIBE: notify_st_unsubscribe_handler
        }

        def _base_handle_async_message(self, async_message: ProtocolMessage):
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
            quote_config: StrategyConfiguration,
            trader_config: StrategyConfiguration,
    ):
        self.quoteStrategy = BaseStrategy(quote_config)
        self.traderStrategy = BaseStrategy(trader_config)

    def init(self) -> bool:
        success = False
        for name, strategy in [("trader", self.traderStrategy), ("quote", self.quoteStrategy)]:
            if strategy is not None:
                try:
                    success = strategy.init()
                    if success:
                        logging.info("%s connection login succeed", name)
                    else:
                        logging.exception("%s connection failed.....", name)
                except Exception as e:
                    logging.exception("login failed, e is %s", e)
                    return False
        return success

    def req_account_detail(self, strategy_id: str) -> (List[StrategyAccountDetail], StrategyError):
        return self.traderStrategy.req_account_detail(strategy_id)

    def req_stock_tick(self, symbol=None, beginDate: int=-1, beginTime: int=-1, endDate: int=-1, endTime: int=-1):
        return self.quoteStrategy.req_stock_tick(symbol, beginDate, beginTime, endDate, endTime)

    def req_future_tick(self, symbol=None, beginDate: int=-1, beginTime: int=-1, endDate: int=-1, endTime: int=-1,
                        autoFill: int=0):
        return self.quoteStrategy.req_future_tick(symbol, beginDate, beginTime, endDate, endTime)

    def req_kline(self, symbol=None, dataType=None, cycDef: int=1, beginDate: int=-1, beginTime: int=-1,
                  endDate: int=-1, endTime: int=-1,
                  autoFill: int=0, cqFlag: int=0, cqDate: int=-1, qjFlag: int=0):
        return self.quoteStrategy.req_kline(symbol, dataType, cycDef, beginDate, beginTime, endDate, endTime, autoFill,
                                            cqFlag, cqDate, qjFlag)

    def req_order(self, order_info: StrategyRequestOrder) -> (str, StrategyError):
        return self.traderStrategy.req_order(order_info)

    def req_order_list(self, strategy_id: str) -> (List[StrategyOrderDetail], StrategyError):
        return self.traderStrategy.req_order_list(strategy_id)

    def req_login(self, conn_info: StrategyConnectionInfo) -> StrategyError:
        self.traderStrategy.req_login(conn_info)
        err = self.quoteStrategy.req_login(conn_info)
        logging.info("req_login, err is ", err.to_json())
        return err

    def req_subscribe(self, symbol: str) -> StrategyError:
        return self.quoteStrategy.req_subscribe(symbol)

    def req_position_statics(self, strategy_id: str) -> (List[StrategyPositionStatics], StrategyError):
        return self.traderStrategy.req_position_statics(strategy_id)

    def req_cancel_order(self, cancel_order_info: StrategyOrderCancel) -> StrategyError:
        return self.traderStrategy.req_cancel_order(cancel_order_info)

    # def req_position_detail(self, strategy_id: str) -> (List[StrategyPositionDetail], StrategyError):
    # return self.traderStrategy.req_position_detail(strategy_id)

    def req_unsubscribe(self, symbol: str) -> StrategyError:
        return self.quoteStrategy.req_unsubscribe(symbol)

    def on_notify_order_error(self, order_error: StrategyOrderError):
        logging.exception("order_error: ", order_error.to_json())

    def on_notify_trade_detail(self, trade_detail: StrategyTradeDetail):
        pass

    def on_notify_order_detail(self, order_detail: StrategyOrderDetail):
        logging.info("order detail: %s", order_detail)

    def on_notify_cancel_error(self, order_cancel_error):
        pass

    def on_notify_quote(self, dataType, data):
        pass


class TestStrategy(unittest.TestCase):
    # trader_port = 8280
    trader_port = 8080
    # quote_port = 8380
    quote_port = 8180
    trader_addr = "101.200.228.73"
    quote_addr = "101.200.228.73"

    @unittest.skip("")
    def test_quote_strategy(self):
        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
        quote_conn_info = StrategyConnectionInfo(
            account_id="016860",
            strategy_id="1",
            tcfs=AgentType.QUOTE
        )
        quote_config = StrategyConfiguration(
            self.quote_addr, self.quote_port, strategy_connection_info=quote_conn_info)

        quote_strategy = BaseStrategy(quote_config)
        quote_strategy.init()

        time.sleep(1000)

    def test_simple_strategy(self):
        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
        trader_conn_info = StrategyConnectionInfo(
            ip="101.200.228.73",
            port=str(self.trader_port),
            account_id="016860",
            password="96e79218965eb72c92a549dd5a330112",
            strategy_id="1",
            tcfs=AgentType.TRADE
        )
        trader_config = StrategyConfiguration(
            self.trader_addr, self.trader_port, strategy_connection_info=trader_conn_info)
        quote_conn_info = StrategyConnectionInfo(
            account_id="016860",
            strategy_id="1",
            tcfs=AgentType.QUOTE
        )
        quote_config = StrategyConfiguration(
            self.quote_addr, self.quote_port, strategy_connection_info=quote_conn_info)

        simple_strategy = SimpleStrategy(quote_config, trader_config)
        simple_strategy.init()

        order_info = StrategyRequestOrder(
            account_id="016860",
            hedge_flag=HedgeFlagType.HEDGE_FLAG_HEDGE,
            market="SHFE",
            product="rb",
            price=2100,
            volume=1,
            instrument="rb1605",
            strategy_id="1",
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
            account_detail, err = simple_strategy.req_account_detail("1")
            logging.info("account_detail: %s", account_detail.to_json() if account_detail else account_detail)
        except Exception as e:
            logging.exception("e: %s", e)
            raise e

        # try:
        # position_detail, err = simple_strategy.req_position_detail("1")
        # logging.info("position_detail: %s", position_detail.to_json() if position_detail else position_detail)
        # except Exception as e:
        # logging.exception("e: %s", e)
        # raise e

        try:
            position_statics, err = simple_strategy.req_position_statics("1")
            logging.info("position_detail: %s", position_statics.to_json() if position_statics else position_statics)
        except Exception as e:
            logging.exception("e: %s", e)
            raise e

        time.sleep(1000)
