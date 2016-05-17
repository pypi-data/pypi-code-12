# encoding: utf-8

__author__ = 'fzh89'

from sd.utils.bean import BaseBean


class KlineBean(BaseBean):
    def __init__(
            self,
            instrumentID=None,
            tradingDay=None,
            updateTime=None,
            openPrice=None,
            highPrice=None,
            lowPrice=None,
            closePrice=None,
            volume=None,
            turover=None,
            matchItems=None,
            interest=None
    ):
        self.instrumentID = instrumentID
        self.tradingDay = tradingDay
        self.updateTime = updateTime
        self.openPrice = openPrice
        self.highPrice = highPrice
        self.lowPrice = lowPrice
        self.closePrice = closePrice
        self.volume = volume
        self.turover = turover
        self.matchItems = matchItems
        self.interest = interest


class FutureMarketBean(BaseBean):
    def __init__(
            self,
            instrumentID=None,  # 合约ID SH.rb1605
            actionDay=None,  # 业务发生日(自然日)
            tradingDay=None,  # 交易日
            lastPrice=0,  # 最新价
            preSettlementPrice=0,  # 昨结算
            preClosePrice=0,  # 昨收盘价
            preOpenInterest=0,  #昨持仓
            openPrice=0,  #开盘价
            highestPrice=0,  #最高价
            lowestPrice=0,  #最低价
            volume=0,  #成交总量
            turnover=0,  #成交总金额
            openInterest=0,  #持仓总量
            closePrice=0,  #今收盘
            settlementPrice=0,  #今结算
            upperLimitPrice=0,  #涨停价
            lowerLimitPrice=0,  #跌停价
            preDelta=0,  #昨虚实度
            currDela=0,  #今虚实度
            updateTime=None,  #交易所时间
            averagePrice=0,  #均价

            askPrice=[],  #买价
            askVolume=[],
            bidPrice=[],
            bidVolume=[],

            #期权属性
            contractID=None,  #期权合约代码
            underlyingSecurityID=None,  #标的证券代码
            callOrPut=None,  #认购认沽
            exerciseDate=None,  #行权日
    ):
        self.instrumentID = instrumentID
        self.actionDay = actionDay
        self.tradingDay = tradingDay
        self.lastPrice = lastPrice
        self.preSettlementPrice = preSettlementPrice
        self.preClosePrice = preClosePrice
        self.preOpenInterest = preOpenInterest
        self.openPrice = openPrice
        self.highestPrice = highestPrice
        self.lowestPrice = lowestPrice
        self.volume = volume
        self.turnover = turnover
        self.openInterest = openInterest
        self.closePrice = closePrice
        self.settlementPrice = settlementPrice
        self.upperLimitPrice = upperLimitPrice
        self.lowerLimitPrice = lowerLimitPrice
        self.preDelta = preDelta
        self.currDela = currDela
        self.updateTime = updateTime
        self.averagePrice = averagePrice
        self.askPrice = askPrice
        self.askVolume = askVolume
        self.bidPrice = bidPrice
        self.bidVolume = bidVolume
        self.contractID = contractID
        self.underlyingSecurityID = underlyingSecurityID
        self.callOrPut = callOrPut
        self.exerciseDate = exerciseDate


class StockMarketBean(BaseBean):
    def __init__(
            self,
            instrumentID=None,  # 合约代码 SH.00000001
            prefix=None,  # 证券信息前缀
            actionDay=None,  # 业务发生日(自然日)
            tradingDay=None,  # 交易日
            updateTime=None,  # 交易所时间
            lastPrice=0,  # 最新价
            preClosePrice=0,  #前收
            openPrice=0,  #开盘价
            highPrice=0,  #最高价
            lowPrice=0,  #最低价
            numTrades=0,  #成交笔数
            volume=0,  #成交总量
            turnover=0,  #成交总金额
            totalBidVolume=0,  #委托买入总量
            totalAskVolume=0,  #委托卖出总量
            weightedAvgBidPrice=0,  #加权平均委买价格
            weightedAvgAskPrice=0,  #加权平均委卖价格
            IOPV=0,  #IOPV净值估值
            yieldToMaturity=0,  #到期收益率
            highLimitedPrice=0,  #涨停价
            lowLimitedPrice=0,  #跌停价
            syl1=0,  #市盈率1
            syl2=0,  #市盈率2
            SD2=0,  #升跌2（对比上一笔）
            askPrice=[],
            askVolume=[],
            bidPrice=[],
            bidVolume=[]
    ):
        self.instrumentID = instrumentID
        self.prefix = prefix
        self.actionDay = actionDay
        self.tradingDay = tradingDay
        self.updateTime = updateTime
        self.lastPrice = lastPrice
        self.preClosePrice = preClosePrice
        self.openPrice = openPrice
        self.highPrice = highPrice
        self.lowPrice = lowPrice
        self.numTrades = numTrades
        self.volume = volume
        self.turnover = turnover
        self.totalBidVolume = totalBidVolume
        self.totalAskVolume = totalAskVolume
        self.weightedAvgBidPrice = weightedAvgBidPrice
        self.weightedAvgAskPrice = weightedAvgAskPrice
        self.IOPV = IOPV
        self.yieldToMaturity = yieldToMaturity
        self.highLimitedPrice = highLimitedPrice
        self.lowLimitedPrice = lowLimitedPrice
        self.syl1 = syl1
        self.syl2 = syl2
        self.SD2 = SD2
        self.askPrice = askPrice
        self.askVolume = askVolume
        self.bidPrice = bidPrice
        self.bidVolume = bidVolume
