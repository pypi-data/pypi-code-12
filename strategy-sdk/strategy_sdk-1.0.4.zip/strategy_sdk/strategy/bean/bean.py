# encoding: utf-8
from typing import List
import unittest

from data.common.enum import OffsetFlagType, EntrustSubmitStatus, \
    EntrustStatus, HedgeFlagType, EntrustBS
from agent import agent_type
from strategy.bean.enum import OperationType, PriceType, InterfaceType
from utils.bean import BaseBean


__author__ = 'yonka'


class StrategyFinanceAccountDetail(BaseBean):
    def __init__(
            self,
            account_id: str=None,
            status: str=None,
            open_date: str=None,
            trading_date: str=None,
            available_money: float=0,
            instrument_value: float=0,
            balance: float=0,
            margin_rate: float=0,
            frozen_margin: float=0,
            frozen_cash: float=0,
            frozen_commission: float=0,
            risk_rate: float=0,
            net_value: float=0,
            pre_balance: float=0,
            commission: float=0,
            position_profit: float=0,
            close_profit: float=0,
            curr_margin: float=0,
            init_close_money: float=0,
            deposit: float=0,
            withdraw: float=0,
            pre_credit: float=0,
            pre_mortgage: float=0,
            credit: float=0,
            mortgage: float=0,
            assure_asset: float=0,
            entrust_asset: float=0,
            total_debit: float=0,
    ):
        self.accountId = account_id
        self.status = status
        self.openDate = open_date
        self.tradingDate = trading_date
        self.availableMoney = available_money
        self.instrumentValue = instrument_value
        self.balance = balance
        self.marginRate = margin_rate
        self.frozenMargin = frozen_margin
        self.frozenCash = frozen_cash
        self.frozenCommission = frozen_commission
        self.riskRate = risk_rate
        self.netValue = net_value
        self.preBalance = pre_balance
        self.commission = commission
        self.positionProfit = position_profit
        self.closeProfit = close_profit
        self.currMargin = curr_margin
        self.initCloseMoney = init_close_money
        self.deposit = deposit
        self.withdraw = withdraw
        self.preCredit = pre_credit
        self.preMortgage = pre_mortgage
        self.credit = credit
        self.mortgage = mortgage
        self.assureAsset = assure_asset
        self.entrustAsset = entrust_asset
        self.totalDebit = total_debit


class StrategyPositionDetail(BaseBean):
    _types = {
        "hedgeFlag": HedgeFlagType,
        "direction": EntrustBS,
    }

    def __init__(
            self,
            account_id: str=None,
            exchange_id: str=None,
            exchange_name: str=None,
            product_id: str=None,
            product_name: str=None,
            instrument_id: str=None,
            instrument_name: str=None,
            open_date: str=None,
            trade_id: str=None,
            volume: int=0,
            open_price: float=0,
            trading_day: str=None,
            margin: float=0,
            open_cost: float=0,
            settlement_price: float=0,
            close_volume: int=0,
            close_amount: float=0,
            float_profit: float=0,
            close_profit: float=0,
            market_value: float=0,
            position_cost: float=0,
            position_profit: float=0,
            last_settlement_price: float=0,
            instrument_value: float=0,
            is_today: bool=False,
            order_id: str=None,
            frozen_volume: int=0,
            can_use_volume: int=0,
            on_road_volume: int=0,
            yesterday_volume: int=0,
            last_price: float=0,
            profit_rate: float=0,
            hedge_flag: HedgeFlagType=None,
            direction: EntrustBS=None,
    ):
        self.accountID = account_id,
        self.exchangeID = exchange_id,
        self.exchangeName = exchange_name,
        self.productID = product_id,
        self.productName = product_name,
        self.instrumentID = instrument_id,
        self.instrumentName = instrument_name,
        self.openDate = open_date,
        self.tradeID = trade_id,
        self.volume = volume,
        self.openPrice = open_price,
        self.tradingDay = trading_day,
        self.margin = margin,
        self.openCost = open_cost,
        self.settlementPrice = settlement_price,
        self.closeVolume = close_volume,
        self.closeAmount = close_amount,
        self.floatProfit = float_profit,
        self.closeProfit = close_profit,
        self.marketValue = market_value,
        self.positionCost = position_cost,
        self.positionProfit = position_profit,
        self.lastSettlementPrice = last_settlement_price,
        self.instrumentValue = instrument_value,
        self.isToday = is_today,
        self.orderID = order_id,
        self.frozenVolume = frozen_volume,
        self.canUseVolume = can_use_volume,
        self.onRoadVolume = on_road_volume,
        self.yesterdayVolume = yesterday_volume,
        self.lastPrice = last_price,
        self.profitRate = profit_rate,
        self.hedgeFlag = hedge_flag,
        self.direction = direction,


class StrategyPositionStatics(BaseBean):
    def __init__(
            self,
            account_id: str=None,
            exchange_id: str=None,
            exchange_name: str=None,
            product_id: str=None,
            instrument_id: str=None,
            instrument_name: str=None,
            yesterday_position: int=0,
            today_position: int=0,
            open_cost: float=0,
            position_cost: float=0,
            close_profit: float=0,
            float_profit: float=0,
            open_price: float=0,
            can_close_vol: int=0,
            used_margin: float=0,
            used_commission: float=0,
            frozen_margin: float=0,
            frozen_commission: float=0,
            instrument_value: float=0,
            open_times: int=0,
            open_volume: int=0,
            cancel_times: int=0,
            frozen_volume: int=0,
            can_use_volume: int=0,
            on_road_volume: int=0,
            settlement_price: float=0,
            profit_rate: float=0,
            hedge_flag: HedgeFlagType=None,
            direction: EntrustBS=None,
            create_time: str=None,
    ):
        self.accountID = account_id
        self.exchangeID = exchange_id
        self.exchangeName = exchange_name
        self.productID = product_id
        self.instrumentID = instrument_id
        self.instrumentName = instrument_name
        self.yesterdayPosition = yesterday_position
        self.todayPosition = today_position
        self.openCost = open_cost
        self.positionCost = position_cost
        self.closeProfit = close_profit
        self.floatProfit = float_profit
        self.openPrice = open_price
        self.canCloseVol = can_close_vol
        self.usedMargin = used_margin
        self.usedCommission = used_commission
        self.frozenMargin = frozen_margin
        self.frozenCommission = frozen_commission
        self.instrumentValue = instrument_value
        self.openTimes = open_times
        self.openVolume = open_volume
        self.cancelTimes = cancel_times
        self.frozenVolume = frozen_volume
        self.canUseVolume = can_use_volume
        self.onRoadVolume = on_road_volume
        self.settlementPrice = settlement_price
        self.profitRate = profit_rate
        self.hedgeFlag = hedge_flag
        self.direction = direction
        self.createTime = create_time


class CtpOrderError(BaseBean):
    def __init__(
            self,
            account_id: str=None,
            error_code: int=0,
            error_msg: str=None,
            session_id: str=None,
            front_id: str=None,
            order_ref_id: str=None,
            request_id: int=0,
            order_id: str=None,
            order_sys_id: str=None,
    ):
        self.accountId = account_id
        self.errorCode = error_code
        self.errorMsg = error_msg
        self.sessionId = session_id
        self.front_id = front_id
        self.orderRefId = order_ref_id
        self.requestId = request_id
        self.orderId = order_id
        self.orderSysId = order_sys_id


class StrategyAccountDetail(BaseBean):
    def __init__(
            self,
            account_id: str=None,
            status: str=None,
            open_date: str=None,
            trading_date: str=None,
            available_money: float=0,
            instrument_value: float=0,
            balance: float=0,
            margin_rate: float=0,
            frozen_margin: float=0,
            frozen_cash: float=0,
            frozen_commission: float=0,
            risk_rate: float=0,
            net_value: float=0,
            pre_balance: float=0,
            commission: float=0,
            position_profit: float=0,
            close_profit: float=0,
            curr_margin: float=0,
            init_balance: float=0,
            init_close_money: float=0,
            deposit: float=0,
            withdraw: float=0,
            pre_credit: float=0,
            pre_mortgage: float=0,
            credit: float=0,
            mortgage: float=0,
            assure_asset: float=0,
            entrust_asset: float=0,
            total_debit: float=0
    ):
        self.accountId = account_id
        self.status = status
        self.openDate = open_date
        self.tradingDate = trading_date
        self.availableMoney = available_money
        self.instrumentValue = instrument_value
        self.balance = balance
        self.marginRate = margin_rate
        self.frozenMargin = frozen_margin
        self.frozenCash = frozen_cash
        self.frozenCommission = frozen_commission
        self.riskRate = risk_rate
        self.netValue = net_value
        self.preBalance = pre_balance
        self.commission = commission
        self.positionProfit = position_profit
        self.closeProfit = close_profit
        self.currMargin = curr_margin
        self.initBalance = init_balance
        self.initCloseMoney = init_close_money
        self.deposit = deposit
        self.withdraw = withdraw
        self.preCredit = pre_credit
        self.preMortgage = pre_mortgage
        self.credit = credit
        self.mortgage = mortgage
        self.assureAsset = assure_asset
        self.entrustAsset = entrust_asset
        self.totalDebit = total_debit


class StrategyError(BaseBean, RuntimeError):
    def __init__(
            self,
            error_id: int=0,
            error_msg: str=None
    ):
        self.errorId = error_id
        self.errorMsg = error_msg


# class StrategyAccountDetailResultBean(BaseBean):
# _types = {
# "data": ArrayStrategyFinanceAccountDetails,
# "error": StrategyError
# }
#
#     def __init__(
#             self,
#             data: ArrayStrategyFinanceAccountDetails=None,
#             error: StrategyError=None
#     ):
#         self.data = data
#         self.error = error


class StrategyConnectionInfo(BaseBean):
    _types = {
        "tcfs": agent_type.AgentType
    }

    def __init__(
            self,
            ip: str=None,
            port: str=None,
            account_id: str=None,
            strategy_id: str=None,
            password: str=None,
            tcfs: agent_type.AgentType=None,
            strategy_client_id: str=None
    ):
        self.ip = ip
        self.port = port
        self.accountId = account_id
        self.strategyId = strategy_id
        self.password = password
        self.tcfs = tcfs
        self.strategyClientID = strategy_client_id


class QuoteDataCategory(BaseBean):
    def __init__(
            self,
            data_symbol: str=None,
            begin_time: str=None,
            end_time: str=None,
    ):
        self.dataSymbol = data_symbol
        self.beginTime = begin_time
        self.endTime = end_time


        # //////////确定数据类型////////////////
        # public String market;
        # public String symbol;
        # //数据周期：tick,秒线、分钟、日线、周线、月线、季线、半年线、年线,见QuoteDataType
        # public int dataType;//数据类型
        # //周期数量：dataType取值为：秒、分钟、日线、周线、月线时，这个字段有效。
        # public int cycCount;
        # //自动填充：仅1秒钟线、1分钟线支持这个标志，（1：补齐；0：不补齐）
        # public int autoFill;
        # //开始日期(交易日，<0:从上市日期开始； 0:从今天开始)
        # public int beginDate;
        # //结束日期(交易日，<=0:跟nBeginDate一样)
        # public int endDate;
        # //开始时间，<=0表示从开始，格式：（HHMMSSmmm）例如94500000 表示 9点45分00秒000毫秒
        # public int beginTime;
        # //结束时间，<=0表示到结束，格式：（HHMMSSmmm）例如94500000 表示 9点45分00秒000毫秒
        # public int endTime;
        #
        # ////////////除权复权标识，只有在数据请求的时候有效///////////////
        #
        # //除权标志：不复权，向前复权，向后复权
        # public int cqFlag;
        # //复权日期(<=0:全程复权) 格式：YYMMDD，例如20130101表示2013年1月1日
        # public int cqDate;
        # //全价标志(债券)(0:净价 1:全价)
        # public int qjFlag;


class StrategyQuoteDataRequest(BaseBean):
    def __init__(
            self,
            market="",
            symbol=None,
            dataType=None,
            cycCount=None,
            autoFill=0,
            beginDate=-1,
            endDate=-1,
            beginTime=-1,
            endTime=-1,
            cqFlag=0,
            cqDate=-1,
            qjFlag=0
    ):
        self.market = market
        self.symbol = symbol
        self.dataType = dataType
        self.cycCount = cycCount
        self.autoFill = autoFill
        self.beginDate = beginDate
        self.endDate = endDate
        self.beginTime = beginTime
        self.endTime = endTime
        self.cqFlag = cqFlag
        self.cqDate = cqDate
        self.qjFlag = qjFlag


class StrategyCancelOrder(BaseBean):
    def __init__(
            self,
            account_id: str=None,
            session_id: str=None,
            front_id: str=None,
            order_ref_id: str=None,
            request_id: int=0,
            order_id: str=None,
    ):
        self.accountId = account_id
        self.sessionId = session_id
        self.frontId = front_id
        self.orderRefId = order_ref_id
        self.requestId = request_id
        self.orderId = order_id


class StrategyConfiguration(BaseBean):
    _types = {
        "strategyConnectionInfo": StrategyConnectionInfo
    }

    def __init__(
            self,
            host: str=None,
            port: int=0,
            read_timeout: int=0,
            conn_timeout: int=0,
            usage_type: int=0,
            strategy_connection_info: StrategyConnectionInfo=None,
    ):
        self.host = host
        self.port = port
        self.readTimeout = read_timeout
        self.connTimeout = conn_timeout
        self.usageType = usage_type
        self.strategyConnectionInfo = strategy_connection_info


class StrategyOrder(BaseBean):
    _types = {
        "m_ePriceType": PriceType,
        "m_eOperationType": OperationType,
        "m_eHedgeFlag": HedgeFlagType
    }

    def __init__(
            self,
            m_str_account_id: str=None,
            m_s_strategy_id: str=None,
            m_d_price: float=0,
            m_d_super_price: float=0,
            m_n_volume: int=0,
            m_str_market: str=None,
            m_str_product: str=None,
            m_str_instrument: str=None,
            m_e_price_type: PriceType=None,
            m_e_operation_type: OperationType=None,
            m_e_hedge_flag: HedgeFlagType=None
    ):
        self.m_strAccountID = m_str_account_id
        self.m_sStrategyID = m_s_strategy_id
        self.m_dPrice = m_d_price
        self.m_dSuperPrice = m_d_super_price
        self.m_nVolume = m_n_volume
        self.m_strMarket = m_str_market
        self.m_strProduct = m_str_product
        self.m_strInstrument = m_str_instrument
        self.m_ePriceType = m_e_price_type
        self.m_eOperationType = m_e_operation_type
        self.m_eHedgeFlag = m_e_hedge_flag


class StrategyOrderCancel(BaseBean):
    def __init__(
            self,
            account_id: str=None,
            request_id: int=0,
            order_id: str=None
    ):
        self.accountId = account_id
        self.requestId = request_id
        self.orderId = order_id


class StrategyOrderCancelError(BaseBean):
    def __init__(
            self,
            account_id: str=None,
            error_code: int=0,
            error_msg: str=None,
            request_id: int=0,
            order_id: str=None
    ):
        self.accountId = account_id
        self.errorCode = error_code
        self.errorMsg = error_msg
        self.requestId = request_id
        self.orderId = order_id


class StrategyOrderDetail(BaseBean):
    _types = {
        "direction": EntrustBS,
        "offsetFlag": OffsetFlagType,
        "hedgeFlag": HedgeFlagType,
        "orderPriceType": PriceType,
        "orderSubmitStatus": EntrustSubmitStatus,
        "orderStatus": EntrustStatus
    }

    def __init__(
            self,
            account_id: str=None,
            exchange_id: str=None,
            exchange_name: str=None,
            product_id: str=None,
            product_name: str=None,
            instrument_id: str=None,
            instrument_name: str=None,
            limit_price: float=0,
            volume_total_original: int=0,
            order_id: str=None,
            volume_traded: int=0,
            volume_total: int=0,
            frozen_margin: float=0,
            frozen_commission: float=0,
            traded_price: float=0,
            cancel_amount: float=0,
            trade_amount: float=0,
            error_code: int=0,
            error_msg: str=None,
            insert_date: str=None,
            insert_time: str=None,
            opt_name: str=None,
            direction: EntrustBS=None,
            offset_flag: OffsetFlagType=None,
            hedge_flag: HedgeFlagType=None,
            order_price_type: PriceType=None,
            order_submit_status: EntrustSubmitStatus=None,
            order_status: EntrustStatus=None
    ):
        self.accountId = account_id
        self.exchangeId = exchange_id
        self.exchangeName = exchange_name
        self.productId = product_id
        self.productName = product_name
        self.instrumentId = instrument_id
        self.instrumentName = instrument_name
        self.limitPrice = limit_price
        self.volumeTotalOriginal = volume_total_original
        self.orderId = order_id
        self.volumeTraded = volume_traded
        self.volumeTotal = volume_total
        self.frozenMargin = frozen_margin
        self.frozenCommission = frozen_commission
        self.tradedPrice = traded_price
        self.cancelAmount = cancel_amount
        self.tradeAmount = trade_amount
        self.errorCode = error_code
        self.errorMsg = error_msg
        self.insertDate = insert_date
        self.insertTime = insert_time
        self.optName = opt_name
        self.direction = direction
        self.offsetFlag = offset_flag
        self.hedgeFlag = hedge_flag
        self.orderPriceType = order_price_type
        self.orderSubmitStatus = order_submit_status
        self.orderStatus = order_status


class StrategyOrderError(BaseBean):
    def __init__(
            self,
            account_id: str=None,
            error_code: int=0,
            error_msg: str=None,
            request_id: int=0,
            order_id: str=None
    ):
        self.accountId = account_id
        self.errorCode = error_code
        self.errorMsg = error_msg
        self.requestId = request_id
        self.orderId = order_id


# class StrategyPositionDetailResultBean(BaseBean):
#     _types = {
#         "data": ArrayStrategyPositionDetails,
#         "error": StrategyError
#     }
#
#     def __init__(
#             self,
#             data: ArrayStrategyPositionDetails=None,
#             error: StrategyError=None
#     ):
#         self.data = data
#         self.error = error


# class StrategyPositionStaticsResultBean(BaseBean):
#     _types = {
#         "data": ArrayStrategyPositionStatics,
#         "strategy_error": StrategyError
#     }
#
#     def __init__(
#             self,
#             data: ArrayStrategyPositionStatics=None,
#             strategy_error: StrategyError=None
#     ):
#         self.data = data
#         self.strategyError = strategy_error


class StrategyPriceData(BaseBean):
    def __init__(
            self,
            trading_day: str=None,
            exchange_id: str=None,
            instrument_id: str=None,
            instrument_name: str=None,
            exchange_inst_id: str=None,
            last_price: float=0,
            up_down: float=0,
            up_down_rate: float=0,
            average_price: float=0,
            volume: int=0,
            turnover: float=0,
            pre_close_price: float=0,
            pre_settlement_price: float=0,
            pre_open_interest: float=0,
            open_interest: float=0,
            settlement_price: float=0,
            open_price: float=0,
            highest_price: float=0,
            lowest_price: float=0,
            close_price: float=0,
            upper_limit_price: float=0,
            lower_limit_price: float=0,
            pre_delta: float=0,
            curr_delta: float=0,
            update_time: str=None,
            update_millisec: int=0,
            bid_price1: float=0,
            bid_volume1: int=0,
            ask_price1: float=0,
            ask_volume1: int=0,
            bid_price2: float=0,
            bid_volume2: int=0,
            ask_price2: float=0,
            ask_volume2: int=0,
            bid_price3: float=0,
            bid_volume3: int=0,
            ask_price3: float=0,
            ask_volume3: int=0,
            bid_price4: float=0,
            bid_volume4: int=0,
            ask_price4: float=0,
            ask_volume4: int=0,
            bid_price5: float=0,
            bid_volume5: int=0,
            ask_price5: float=0,
            ask_volume5: int=0,
            bid_price6: float=0,
            bid_volume6: int=0,
            ask_price6: float=0,
            ask_volume6: int=0,
            pre_price: float=0
    ):
        self.tradingDay = trading_day
        self.exchangeId = exchange_id
        self.instrumentId = instrument_id
        self.instrumentName = instrument_name
        self.exchangeInstID = exchange_inst_id
        self.lastPrice = last_price
        self.upDown = up_down
        self.upDownRate = up_down_rate
        self.averagePrice = average_price
        self.volume = volume
        self.turnover = turnover
        self.preClosePrice = pre_close_price
        self.preSettlementPrice = pre_settlement_price
        self.preOpenInterest = pre_open_interest
        self.openInterest = open_interest
        self.settlementPrice = settlement_price
        self.openPrice = open_price
        self.highestPrice = highest_price
        self.lowestPrice = lowest_price
        self.closePrice = close_price
        self.upperLimitPrice = upper_limit_price
        self.lowerLimitPrice = lower_limit_price
        self.preDelta = pre_delta
        self.currDelta = curr_delta
        self.updateTime = update_time
        self.updateMillisec = update_millisec
        self.bidPrice1 = bid_price1
        self.bidVolume1 = bid_volume1
        self.askPrice1 = ask_price1
        self.askVolume1 = ask_volume1
        self.bidPrice2 = bid_price2
        self.bidVolume2 = bid_volume2
        self.askPrice2 = ask_price2
        self.askVolume2 = ask_volume2
        self.bidPrice3 = bid_price3
        self.bidVolume3 = bid_volume3
        self.askPrice3 = ask_price3
        self.askVolume3 = ask_volume3
        self.bidPrice4 = bid_price4
        self.bidVolume4 = bid_volume4
        self.askPrice4 = ask_price4
        self.askVolume4 = ask_volume4
        self.bidPrice5 = bid_price5
        self.bidVolume5 = bid_volume5
        self.askPrice5 = ask_price5
        self.askVolume5 = ask_volume5
        self.bidPrice6 = bid_price6
        self.bidVolume6 = bid_volume6
        self.askPrice6 = ask_price6
        self.askVolume6 = ask_volume6
        self.prePrice = pre_price


# class StrategyQuoteDataRequest(BaseBean):
#     def __init__(
#             self,
#             data_type: str=None,
#             begin_date: str=None,
#             end_date: str=None
#     ):
#         self.dataType = data_type
#         self.beginDate = begin_date
#         self.endDate = end_date


class StrategyQuoteDataResult(BaseBean):
    _types = {
        "strategyError": StrategyError
    }

    def __init__(
            self,
            strategy_error: StrategyError=None,
            data_type: str=None,
            data=None
    ):
        self.strategyError = strategy_error
        self.dataType = data_type
        self.data = data


class StrategyRequestOrder(BaseBean):
    _types = {
        "priceType": PriceType,
        "hedgeFlag": HedgeFlagType,
        "orderOperationType": OperationType,
        "interfaceType": InterfaceType
    }

    def __init__(
            self,
            account_id: str=None,
            price: float=0,
            volume: int=0,
            strategy_id: str=None,
            market: str=None,
            product: str=None,
            instrument: str=None,
            price_type: PriceType=None,
            hedge_flag: HedgeFlagType=None,
            order_operation_type: OperationType=None,
            interface_type: InterfaceType=None
    ):
        self.accountId = account_id
        self.price = price
        self.volume = volume
        self.strategyId = strategy_id
        self.market = market
        self.product = product
        self.instrument = instrument
        self.priceType = price_type
        self.hedgeFlag = hedge_flag
        self.orderOperationType = order_operation_type
        self.interfaceType = interface_type
        self.strategyClientID = None  # type: str


class StrategyTradeDetail(BaseBean):
    _types = {
        "direction": EntrustBS,
        "offsetFlag": OffsetFlagType,
        "hedgeFlag": HedgeFlagType,
        "orderPriceType": PriceType
    }

    def __init__(
            self,
            account_id: str=None,
            exchange_id: str=None,
            exchange_name: str=None,
            product_id: str=None,
            product_name: str=None,
            instrument_id: str=None,
            instrument_name: str=None,
            trade_id: str=None,
            order_id: str=None,
            price: float=0,
            volume: int=0,
            trade_date: str=None,
            trade_time: str=None,
            comssion: float=0,  # FIXME 可能原java代码拼写错误
            trade_amount: float=0,
            opt_name: str=None,
            direction: EntrustBS=None,
            offset_flag: OffsetFlagType=None,
            hedge_flag: HedgeFlagType=None,
            order_price_type: PriceType=None
    ):
        self.accountId = account_id
        self.exchangeId = exchange_id
        self.exchangeName = exchange_name
        self.productID = product_id
        self.productName = product_name
        self.instrumentId = instrument_id
        self.instrumentName = instrument_name
        self.tradeId = trade_id
        self.orderId = order_id
        self.price = price
        self.volume = volume
        self.tradeDate = trade_date
        self.tradeTime = trade_time
        self.comssion = comssion
        self.tradeAmount = trade_amount
        self.optName = opt_name
        self.direction = direction
        self.offsetFlag = offset_flag
        self.hedgeFlag = hedge_flag
        self.orderPriceType = order_price_type


class TickFiveLevelData(BaseBean):
    def __init__(
            self,
            trading_day: str=None,
            exchange_id: str=None,
            instrument_id: str=None,
            instrument_name: str=None,
            exchange_inst_id: str=None,
            last_price: float=0,
            up_down: float=0,
            up_down_rate: float=0,
            average_price: float=0,
            volume: int=0,
            turnover: float=0,
            pre_close_price: float=0,
            pre_settlement_price: float=0,
            pre_open_interest: float=0,
            open_interest: float=0,
            settlement_price: float=0,
            open_price: float=0,
            highest_price: float=0,
            lowest_price: float=0,
            close_price: float=0,
            upper_limit_price: float=0,
            lower_limit_price: float=0,
            pre_delta: float=0,
            curr_delta: float=0,
            update_time: str=None,
            update_millisec: int=0,
            bid_price1: float=0,
            bid_volume1: int=0,
            ask_price1: float=0,
            ask_volume1: int=0,
            bid_price2: float=0,
            bid_volume2: int=0,
            ask_price2: float=0,
            ask_volume2: int=0,
            bid_price3: float=0,
            bid_volume3: int=0,
            ask_price3: float=0,
            ask_volume3: int=0,
            bid_price4: float=0,
            bid_volume4: int=0,
            ask_price4: float=0,
            ask_volume4: int=0,
            bid_price5: float=0,
            bid_volume5: int=0,
            ask_price5: float=0,
            ask_volume5: int=0,
            bid_price6: float=0,
            bid_volume6: int=0,
            ask_price6: float=0,
            ask_volume6: int=0,
            pre_price: float=0
    ):
        self.tradingDay = trading_day
        self.exchangeId = exchange_id
        self.instrumentId = instrument_id
        self.instrumentName = instrument_name
        self.exchangeInstID = exchange_inst_id
        self.lastPrice = last_price
        self.upDown = up_down
        self.upDownRate = up_down_rate
        self.averagePrice = average_price
        self.volume = volume
        self.turnover = turnover
        self.preClosePrice = pre_close_price
        self.preSettlementPrice = pre_settlement_price
        self.preOpenInterest = pre_open_interest
        self.openInterest = open_interest
        self.settlementPrice = settlement_price
        self.openPrice = open_price
        self.highestPrice = highest_price
        self.lowestPrice = lowest_price
        self.closePrice = close_price
        self.upperLimitPrice = upper_limit_price
        self.lowerLimitPrice = lower_limit_price
        self.preDelta = pre_delta
        self.currDelta = curr_delta
        self.updateTime = update_time
        self.updateMillisec = update_millisec
        self.bidPrice1 = bid_price1
        self.bidVolume1 = bid_volume1
        self.askPrice1 = ask_price1
        self.askVolume1 = ask_volume1
        self.bidPrice2 = bid_price2
        self.bidVolume2 = bid_volume2
        self.askPrice2 = ask_price2
        self.askVolume2 = ask_volume2
        self.bidPrice3 = bid_price3
        self.bidVolume3 = bid_volume3
        self.askPrice3 = ask_price3
        self.askVolume3 = ask_volume3
        self.bidPrice4 = bid_price4
        self.bidVolume4 = bid_volume4
        self.askPrice4 = ask_price4
        self.askVolume4 = ask_volume4
        self.bidPrice5 = bid_price5
        self.bidVolume5 = bid_volume5
        self.askPrice5 = ask_price5
        self.askVolume5 = ask_volume5
        self.bidPrice6 = bid_price6
        self.bidVolume6 = bid_volume6
        self.askPrice6 = ask_price6
        self.askVolume6 = ask_volume6
        self.prePrice = pre_price


class SimpleStringMessage(BaseBean):
    def __init__(
            self,
            data: str=None
    ):
        self.data = data


class TestBean(unittest.TestCase):
    def test_init_StrategyFinanceAccountDetail(self):
        return StrategyFinanceAccountDetail(account_id="123", frozen_cash=1, commission=1.1)

    def test_set_StrategyFinanceAccountDetail(self):
        self.test_init_StrategyFinanceAccountDetail()

    def test_from_methods(self):
        class A(BaseBean):
            def __init__(self, a: int=0):
                self.a = a

            def __str__(self):
                return "A(a=%d)" % self.a

        class B(BaseBean):
            _types = {
                "a_list": List[A]
            }

            def __init__(self, a_list: List[A]=None):
                self.a_list = a_list

        # s = "{\"a\":1}"
        s = """{"a":1}"""
        s1 = "{\"a_list\":[{\"a\":1},{\"a\":2}]}"
        a = A().from_json(s)
        print(a)
        b = B().from_json(s1)
        print(b.a_list, b.a_list[0])

        print(a.to_json())
        print(b.to_json())
