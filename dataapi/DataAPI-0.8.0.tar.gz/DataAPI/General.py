# -*- coding: utf-8 -*-
u"""
Created on 2015-12-11

@author: cheng.li, weijun.shen
"""

import pandas as pd


from DataAPI.MarketDataLoader import BAR_TYPE
from DataAPI.MarketDataLoader import _fillnanValue
from DataAPI.Equity import GetEquityBarMin1
from DataAPI.Equity import GetEquityBarMin5
from DataAPI.Equity import GetEquityBarEOD
from DataAPI.Index import GetIndexBarMin1
from DataAPI.Index import GetIndexBarMin5
from DataAPI.Index import GetIndexBarEOD
from DataAPI.Future import GetFutureBarMin1
from DataAPI.Future import GetFutureBarMin5
from DataAPI.Future import GetFutureBarEOD
from DataAPI.Utilities import categorizeSymbols
from DataAPI.Utilities import enableCache


def route(barType):
    if barType == BAR_TYPE.MIN1:
        equity_api, future_api, index_api = GetEquityBarMin1, GetFutureBarMin1, GetIndexBarMin1
    elif barType == BAR_TYPE.MIN5:
        equity_api, future_api, index_api = GetEquityBarMin5, GetFutureBarMin5, GetIndexBarMin5
    elif barType == BAR_TYPE.EOD:
        equity_api, future_api, index_api = GetEquityBarEOD, GetFutureBarEOD, GetIndexBarEOD
    else:
        raise ValueError("Unknown bar type {0}".format(barType))

    return equity_api, future_api, index_api


@enableCache
def GetGeneralBarData(instrumentIDList,
                      startDate,
                      endDate,
                      bType,
                      field="*",
                      chunksize=None,
                      baseDate=None,
                      forceUpdate=True,
                      instrumentIDasCol=False):
    u"""

    获取一般证券的行情数据

    :param instrumentIDList: 证券列表，例如:['600000.xshg', 'if1512', '000300.zicn']
    :param startDate: 开始日期，格式：'YYYY-MM-DD'
    :param endDate: 结束日期，格式：'YYYY-MM-DD
    :param bType: bar的类型，例如：BAR_TYPE.MIN1
    :param field: 需要获取的字段类型，例如：['closePrice']，不填的话，默认获取所有字段；
                  可用的field包括：[productID, instrumentID, tradingDate, tradingTime,
                  openPrice, highPrice, lowPrice, closePrice, volume, turnover]
    :param chunksize: 以分段的形式获取chunksize大小的数据
    :param baseDate: 获取股票复权数据时的默认基准日，可填：日期，'start'，'end'，以及None，默认为None：不复权。
                     'YYYY-MM-DD'：以固定日期为复权基准日。若该日不是交易日，向前调整至最近的交易日；
                     'start'：以startDate起始日期为基准日。若该日不是交易日，向前调整至最近的交易日；
                     'end'：以endDate结束日期为基准日。若该日不是交易日，向前调整至最近的交易日；
                     None：不复权
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :param instrumentIDasCol: 联合使用field以及instrumentIDs作为column的名字
    :return: pandas.DataFrame
    """

    symbolList = [s.lower() for s in instrumentIDList]
    category = categorizeSymbols(symbolList)
    equity_api, future_api, index_api = route(bType)

    if not chunksize:
        res = pd.DataFrame()
        if category['stocks']:
            equity_res = equity_api([s[:6] for s in category['stocks']],
                                    startDate,
                                    endDate,
                                    field,
                                    baseDate=baseDate)
            res = res.append(equity_res)

        if category['futures']:
            future_res = future_api([s for s in category['futures']],
                                    startDate,
                                    endDate,
                                    field)
            res = res.append(future_res)

        if category['indexes']:
            index_res = index_api([s[:6] for s in category['indexes']],
                                  startDate,
                                  endDate,
                                  field)
            res = res.append(index_res)

        if instrumentIDasCol:
            res.drop(['tradingDate', 'tradingTime'], axis=1, inplace=True)
            if 'tradingMilliSec' in res:
                res.drop('tradingMilliSec', axis=1, inplace=True)
            res.set_index('instrumentID', append=True, inplace=True)
            res = res.unstack(level=-1)
            return _fillnanValue(res)
        else:
            return res
    else:

        def _getInChunk(category, startDate, endDate, field, baseDate, forceUpdate, chunksize, equity_api, future_api,
                        index_api):
            if category['stocks']:
                data = equity_api([s[:6] for s in category['stocks']],
                                  startDate,
                                  endDate,
                                  field,
                                  chunksize,
                                  baseDate=baseDate,
                                  forceUpdate=forceUpdate,
                                  instrumentIDasCol=instrumentIDasCol)
                while True:
                    try:
                        yield next(data)
                    except StopIteration:
                        break

            if category['futures']:
                data = future_api([s for s in category['futures']],
                                  startDate,
                                  endDate,
                                  field,
                                  chunksize,
                                  forceUpdate=forceUpdate,
                                  instrumentIDasCol=instrumentIDasCol)
                while True:
                    try:
                        yield next(data)
                    except StopIteration:
                        break

            if category['indexes']:
                data = index_api([s[:6] for s in category['indexes']],
                                 startDate,
                                 endDate,
                                 field,
                                 chunksize,
                                 forceUpdate=forceUpdate,
                                 instrumentIDasCol=instrumentIDasCol)
                while True:
                    try:
                        yield next(data)
                    except StopIteration:
                        break

        return _getInChunk(category, startDate, endDate, field, baseDate, forceUpdate, chunksize, equity_api,
                           future_api, index_api)
