# encoding: utf-8
from __future__ import absolute_import
import unittest

from data.common.enum import OffsetFlagType, EntrustSubmitStatus, \
    EntrustStatus, HedgeFlagType, EntrustBS
from agent import agent_type
from strategy.bean.enum import OperationType, PriceType, InterfaceType
from utils.bean import BaseBean
from utils.typing import List

__author__ = u'yonka'


class StrategyFinanceAccountDetail(BaseBean):
    def __init__(
            self,
            account_id=None,
            status=None,
            open_date=None,
            trading_date=None,
            available_money=0,
            instrument_value=0,
            balance=0,
            margin_rate=0,
            frozen_margin=0,
            frozen_cash=0,
            frozen_commission=0,
            risk_rate=0,
            net_value=0,
            pre_balance=0,
            commission=0,
            position_profit=0,
            close_profit=0,
            curr_margin=0,
            init_close_money=0,
            deposit=0,
            withdraw=0,
            pre_credit=0,
            pre_mortgage=0,
            credit=0,
            mortgage=0,
            assure_asset=0,
            entrust_asset=0,
            total_debit=0,
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
        u"hedgeFlag": HedgeFlagType,
        u"direction": EntrustBS,
    }

    def __init__(
            self,
            account_id=None,
            exchange_id=None,
            exchange_name=None,
            product_id=None,
            product_name=None,
            instrument_id=None,
            instrument_name=None,
            open_date=None,
            trade_id=None,
            volume=0,
            open_price=0,
            trading_day=None,
            margin=0,
            open_cost=0,
            settlement_price=0,
            close_volume=0,
            close_amount=0,
            float_profit=0,
            close_profit=0,
            market_value=0,
            position_cost=0,
            position_profit=0,
            last_settlement_price=0,
            instrument_value=0,
            is_today=False,
            order_id=None,
            frozen_volume=0,
            can_use_volume=0,
            on_road_volume=0,
            yesterday_volume=0,
            last_price=0,
            profit_rate=0,
            hedge_flag=None,
            direction=None,
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
            account_id=None,
            exchange_id=None,
            exchange_name=None,
            product_id=None,
            instrument_id=None,
            instrument_name=None,
            yesterday_position=0,
            today_position=0,
            open_cost=0,
            position_cost=0,
            close_profit=0,
            float_profit=0,
            open_price=0,
            can_close_vol=0,
            used_margin=0,
            used_commission=0,
            frozen_margin=0,
            frozen_commission=0,
            instrument_value=0,
            open_times=0,
            open_volume=0,
            cancel_times=0,
            frozen_volume=0,
            can_use_volume=0,
            on_road_volume=0,
            settlement_price=0,
            profit_rate=0,
            hedge_flag=None,
            direction=None,
            create_time=None,
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
            account_id=None,
            error_code=0,
            error_msg=None,
            session_id=None,
            front_id=None,
            order_ref_id=None,
            request_id=0,
            order_id=None,
            order_sys_id=None,
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
            account_id=None,
            status=None,
            open_date=None,
            trading_date=None,
            available_money=0,
            instrument_value=0,
            balance=0,
            margin_rate=0,
            frozen_margin=0,
            frozen_cash=0,
            frozen_commission=0,
            risk_rate=0,
            net_value=0,
            pre_balance=0,
            commission=0,
            position_profit=0,
            close_profit=0,
            curr_margin=0,
            init_balance=0,
            init_close_money=0,
            deposit=0,
            withdraw=0,
            pre_credit=0,
            pre_mortgage=0,
            credit=0,
            mortgage=0,
            assure_asset=0,
            entrust_asset=0,
            total_debit=0
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
            error_id=0,
            error_msg=None
    ):
        self.errorId = error_id
        self.errorMsg = error_msg


# class StrategyAccountDetailResultBean(BaseBean):
# _types = {
# u"data": ArrayStrategyFinanceAccountDetails,
# u"error": StrategyError
#     }
#
#     def __init__(
#             self,
#             data=None,
#             error=None
#     ):
#         self.data = data
#         self.error = error


class StrategyConnectionInfo(BaseBean):
    def __init__(
            self,
            ip=None,
            port=None,
            account_id=None,
            strategy_id=None,
            password=None,
            strategy_client_id=None
    ):
        self.ip = ip
        self.port = port
        self.accountId = account_id
        self.strategyId = strategy_id
        self.password = password
        self.strategyClientID = strategy_client_id


class QuoteDataCategory(BaseBean):
    def __init__(
            self,
            data_symbol=None,
            begin_time=None,
            end_time=None,
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
            account_id=None,
            session_id=None,
            front_id=None,
            order_ref_id=None,
            request_id=0,
            order_id=None,
    ):
        self.accountId = account_id
        self.sessionId = session_id
        self.frontId = front_id
        self.orderRefId = order_ref_id
        self.requestId = request_id
        self.orderId = order_id


class StrategyConfiguration(BaseBean):
    _types = {
        u"strategyConnectionInfo": StrategyConnectionInfo
    }

    def __init__(
            self,
            host=None,
            port=0,
            read_timeout=0,
            conn_timeout=0,
            usage_type=0,
            strategy_connection_info=None,
    ):
        self.host = host
        self.port = port
        self.readTimeout = read_timeout
        self.connTimeout = conn_timeout
        self.usageType = usage_type
        self.strategyConnectionInfo = strategy_connection_info


class StrategyOrder(BaseBean):
    _types = {
        u"m_ePriceType": PriceType,
        u"m_eOperationType": OperationType,
        u"m_eHedgeFlag": HedgeFlagType
    }

    def __init__(
            self,
            m_str_account_id=None,
            m_s_strategy_id=None,
            m_d_price=0,
            m_d_super_price=0,
            m_n_volume=0,
            m_str_market=None,
            m_str_product=None,
            m_str_instrument=None,
            m_e_price_type=None,
            m_e_operation_type=None,
            m_e_hedge_flag=None
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
            account_id=None,
            request_id=0,
            order_id=None
    ):
        self.accountId = account_id
        self.requestId = request_id
        self.orderId = order_id


class StrategyOrderCancelError(BaseBean):
    def __init__(
            self,
            account_id=None,
            error_code=0,
            error_msg=None,
            request_id=0,
            order_id=None
    ):
        self.accountId = account_id
        self.errorCode = error_code
        self.errorMsg = error_msg
        self.requestId = request_id
        self.orderId = order_id


class StrategyOrderDetail(BaseBean):
    def __init__(
            self,
            account_id=None,
            exchange_id=None,
            exchange_name=None,
            product_id=None,
            product_name=None,
            instrument_id=None,
            instrument_name=None,
            limit_price=0,
            volume_total_original=0,
            order_id=None,
            volume_traded=0,
            volume_total=0,
            frozen_margin=0,
            frozen_commission=0,
            traded_price=0,
            cancel_amount=0,
            trade_amount=0,
            error_code=0,
            error_msg=None,
            insert_date=None,
            insert_time=None,
            opt_name=None,
            direction=None,
            offset_flag=None,
            hedge_flag=None,
            order_price_type=None,
            order_submit_status=None,
            order_status=None
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
            account_id=None,
            error_code=0,
            error_msg=None,
            request_id=0,
            order_id=None
    ):
        self.accountId = account_id
        self.errorCode = error_code
        self.errorMsg = error_msg
        self.requestId = request_id
        self.orderId = order_id


# class StrategyPositionDetailResultBean(BaseBean):
#     _types = {
#         u"data": ArrayStrategyPositionDetails,
#         u"error": StrategyError
#     }
#
#     def __init__(
#             self,
#             data=None,
#             error=None
#     ):
#         self.data = data
#         self.error = error


# class StrategyPositionStaticsResultBean(BaseBean):
#     _types = {
#         u"data": ArrayStrategyPositionStatics,
#         u"strategy_error": StrategyError
#     }
#
#     def __init__(
#             self,
#             data=None,
#             strategy_error=None
#     ):
#         self.data = data
#         self.strategyError = strategy_error


class StrategyPriceData(BaseBean):
    def __init__(
            self,
            trading_day=None,
            exchange_id=None,
            instrument_id=None,
            instrument_name=None,
            exchange_inst_id=None,
            last_price=0,
            up_down=0,
            up_down_rate=0,
            average_price=0,
            volume=0,
            turnover=0,
            pre_close_price=0,
            pre_settlement_price=0,
            pre_open_interest=0,
            open_interest=0,
            settlement_price=0,
            open_price=0,
            highest_price=0,
            lowest_price=0,
            close_price=0,
            upper_limit_price=0,
            lower_limit_price=0,
            pre_delta=0,
            curr_delta=0,
            update_time=None,
            update_millisec=0,
            bid_price1=0,
            bid_volume1=0,
            ask_price1=0,
            ask_volume1=0,
            bid_price2=0,
            bid_volume2=0,
            ask_price2=0,
            ask_volume2=0,
            bid_price3=0,
            bid_volume3=0,
            ask_price3=0,
            ask_volume3=0,
            bid_price4=0,
            bid_volume4=0,
            ask_price4=0,
            ask_volume4=0,
            bid_price5=0,
            bid_volume5=0,
            ask_price5=0,
            ask_volume5=0,
            bid_price6=0,
            bid_volume6=0,
            ask_price6=0,
            ask_volume6=0,
            pre_price=0
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
#             data_type=None,
#             begin_date=None,
#             end_date=None
#     ):
#         self.dataType = data_type
#         self.beginDate = begin_date
#         self.endDate = end_date


class StrategyQuoteDataResult(BaseBean):
    _types = {
        u"strategyError": StrategyError
    }

    def __init__(
            self,
            strategy_error=None,
            data_type=None,
            data=None
    ):
        self.strategyError = strategy_error
        self.dataType = data_type
        self.data = data


class StrategyRequestOrder(BaseBean):
    _types = {
        u"priceType": PriceType,
        u"hedgeFlag": HedgeFlagType,
        u"orderOperationType": OperationType,
        u"interfaceType": InterfaceType
    }

    def __init__(
            self,
            account_id=None,
            price=0,
            volume=0,
            strategy_id=None,
            market=None,
            product=None,
            instrument=None,
            price_type=None,
            hedge_flag=None,
            order_operation_type=None,
            interface_type=None
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
        u"direction": EntrustBS,
        u"offsetFlag": OffsetFlagType,
        u"hedgeFlag": HedgeFlagType,
        u"orderPriceType": PriceType
    }

    def __init__(
            self,
            account_id=None,
            exchange_id=None,
            exchange_name=None,
            product_id=None,
            product_name=None,
            instrument_id=None,
            instrument_name=None,
            trade_id=None,
            order_id=None,
            price=0,
            volume=0,
            trade_date=None,
            trade_time=None,
            comssion=0,  # FIXME 可能原java代码拼写错误
            trade_amount=0,
            opt_name=None,
            direction=None,
            offset_flag=None,
            hedge_flag=None,
            order_price_type=None
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
            trading_day=None,
            exchange_id=None,
            instrument_id=None,
            instrument_name=None,
            exchange_inst_id=None,
            last_price=0,
            up_down=0,
            up_down_rate=0,
            average_price=0,
            volume=0,
            turnover=0,
            pre_close_price=0,
            pre_settlement_price=0,
            pre_open_interest=0,
            open_interest=0,
            settlement_price=0,
            open_price=0,
            highest_price=0,
            lowest_price=0,
            close_price=0,
            upper_limit_price=0,
            lower_limit_price=0,
            pre_delta=0,
            curr_delta=0,
            update_time=None,
            update_millisec=0,
            bid_price1=0,
            bid_volume1=0,
            ask_price1=0,
            ask_volume1=0,
            bid_price2=0,
            bid_volume2=0,
            ask_price2=0,
            ask_volume2=0,
            bid_price3=0,
            bid_volume3=0,
            ask_price3=0,
            ask_volume3=0,
            bid_price4=0,
            bid_volume4=0,
            ask_price4=0,
            ask_volume4=0,
            bid_price5=0,
            bid_volume5=0,
            ask_price5=0,
            ask_volume5=0,
            bid_price6=0,
            bid_volume6=0,
            ask_price6=0,
            ask_volume6=0,
            pre_price=0
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
            data=None
    ):
        self.data = data


class TestBean(unittest.TestCase):
    def test_init_StrategyFinanceAccountDetail(self):
        return StrategyFinanceAccountDetail(account_id=u"123", frozen_cash=1, commission=1.1)

    def test_set_StrategyFinanceAccountDetail(self):
        self.test_init_StrategyFinanceAccountDetail()

    def test_init_ArrayStrategyFinanceAccountDetails(self):
        return ArrayStrategyFinanceAccountDetails([self.test_init_StrategyFinanceAccountDetail()])

    def test_from_methods(self):
        class A(BaseBean):
            def __init__(self, a=0):
                self.a = a

            def __str__(self):
                return u"A(a=%d)" % self.a

        class B(BaseBean):
            _types = {
                u"a_list": List[A]
            }

            def __init__(self, a_list=None):
                self.a_list = a_list

        # s = "{\"a\":1}"
        s = u"""{"a":1}"""
        s1 = u"{\"a_list\":[{\"a\":1},{\"a\":2}]}"
        a = A().from_json(s)
        print a
        b = B().from_json(s1)
        print b.a_list, b.a_list[0]

        print a.to_json()
        print b.to_json()
