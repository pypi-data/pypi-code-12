# -*- coding: utf-8 -*-
u"""
Created on 2015-11-12

@author: cheng.li, weijun.shen
"""

import pandas as pd
from DataAPI.MarketDataLoader import getBarData
from DataAPI.MarketDataLoader import BAR_TYPE
from DataAPI.MarketDataLoader import _getAdjustPriceTable
from DataAPI.MarketDataLoader import _adjustPrice
from DataAPI.MarketDataLoader import _fillnanValue
from DataAPI.Utilities import enableCache
from DataAPI.Utilities import cleanColsForUnicode
from DataAPI.Utilities import createEngine
from DataAPI.Utilities import list_to_str
from DataAPI.Utilities import NAMES_SETTINGS
from DataAPI.Utilities import field_names_mapping
from DataAPI.Utilities import _generateSecurityID
from DataAPI.Utilities import ASSET_TYPE
from DataAPI.Utilities import _setTimeStamp
from DataAPI.SqlExpressions import Condition


@enableCache
@cleanColsForUnicode
def GetEquityBarMin1(instrumentIDList, startDate, endDate, field="*", chunksize=None, baseDate=None, forceUpdate=True,
                     instrumentIDasCol=False):
    u"""

    获取股票1分钟线数据

    :param instrumentIDList: 证券名或者列表，例如：'600000'或者['600000', '000001']
    :param startDate: 开始日期，格式：'YYYY-MM-DD'
    :param endDate: 结束日期，格式：'YYYY-MM-DD'
    :param field: 需要获取的字段类型，例如：['closePrice']，不填的话，默认获取所有字段；
                  可用的field包括：[productID, instrumentID, tradingDate, tradingTime,
                  openPrice, highPrice, lowPrice, closePrice, volume, turnover]
    :param chunksize: 以分段的形式获取chunksize大小的数据
    :param baseDate: 获取复权数据时的默认基准日，可填：日期，'start'，'end'，以及None，默认为None：不复权
                     'YYYY-MM-DD'：以固定日期为复权基准日。若该日不是交易日，向前调整至最近的交易日；
                     'start'：以startDate起始日期为基准日。若该日不是交易日，向前调整至最近的交易日；
                     'end'：以endDate结束日期为基准日。若该日不是交易日，向前调整至最近的交易日；
                     None：不复权
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :param instrumentIDasCol: 联合使用field以及instrumentIDs作为column的名字
    :return: pandas.DataFrame
    """
    return getBarData(instrumentIDList, startDate, endDate, ASSET_TYPE.EQUITY, BAR_TYPE.MIN1, field, chunksize,
                      baseDate, instrumentIDasCol)


@enableCache
@cleanColsForUnicode
def GetEquityBarMin5(instrumentIDList, startDate, endDate, field="*", chunksize=None, baseDate=None, forceUpdate=True,
                     instrumentIDasCol=False):
    u"""

    获取股票5分钟线数据

    :param instrumentIDList: 证券名或者列表，例如：'600000'或者['600000', '000001']
    :param startDate: 开始日期，格式：'YYYY-MM-DD'
    :param endDate: 结束日期，格式：'YYYY-MM-DD'
    :param field: 需要获取的字段类型，例如：['closePrice']，不填的话，默认获取所有字段；
                  可用的field包括：[productID, instrumentID, tradingDate, tradingTime,
                  openPrice, highPrice, lowPrice, closePrice, volume, turnover]
    :param chunksize: 以分段的形式获取chunksize大小的数据
    :param baseDate: 获取复权数据时的默认基准日，可填：日期，'start'，'end'，以及None，默认为None：不复权
                     'YYYY-MM-DD'：以固定日期为复权基准日。若该日不是交易日，向前调整至最近的交易日；
                     'start'：以startDate起始日期为基准日。若该日不是交易日，向前调整至最近的交易日；
                     'end'：以endDate结束日期为基准日。若该日不是交易日，向前调整至最近的交易日；
                     None：不复权
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :param instrumentIDasCol: 联合使用field以及instrumentIDs作为column的名字
    :return: pandas.DataFrame
    """
    return getBarData(instrumentIDList, startDate, endDate, ASSET_TYPE.EQUITY, BAR_TYPE.MIN5, field, chunksize,
                      baseDate, instrumentIDasCol)


def _format_data(data, names_mapping, raw_names, names):
    data[names_mapping[u'tradingDate']] = data[names_mapping[u'tradingDate']].apply(lambda x: x[:4] + '-'
                                                                                              + x[4:6]
                                                                                              + '-'
                                                                                              + x[6:])
    data[names_mapping[u'instrumentID']] = data[names_mapping[u'instrumentID']].apply(lambda x: x[:6])
    data[names_mapping[u'productID']] = data[names_mapping[u'instrumentID']]
    data[names_mapping[u'volume']] *= 100.
    data[names_mapping[u'turnover']] *= 1000.
    data[names_mapping[u'tradingTime']] = u"15:00:00.0000000"
    data = data[list(raw_names)]
    data = data.rename(columns=dict(names))
    return data


def _return_data_in_chunk(generator,
                          baseDate,
                          instrumentIDList,
                          startDate,
                          endDate,
                          instrumentIDasCol,
                          names_mapping,
                          raw_names,
                          names):
    if baseDate:
        # to adjust the price data for dividends events
        instrumentIDList = [ins[:6] for ins in instrumentIDList]
        baseFactor, dateRangeFactors = _getAdjustPriceTable(baseDate, startDate, endDate, 'WindDB', instrumentIDList)
    for chunk in generator:
        chunk = _format_data(chunk, names_mapping, raw_names, names)
        if baseDate:
            chunk = _adjustPrice(baseFactor, dateRangeFactors, chunk)
        chunk = _setTimeStamp(chunk, ASSET_TYPE.EQUITY, BAR_TYPE.EOD, instrumentIDasCol)
        chunk['securityID'] = _generateSecurityID(chunk[u'instrumentID'], ASSET_TYPE.EQUITY)
        if instrumentIDasCol:
            yield _fillnanValue(chunk)
        else:
            yield chunk


@enableCache
@cleanColsForUnicode
def GetEquityBarEOD(instrumentIDList, startDate, endDate, field="*", chunksize=None, baseDate=None, forceUpdate=True,
                    instrumentIDasCol=False):
    u"""

    获取股票日线数据

    :param instrumentIDList: 证券名或者列表，例如：'600000'或者['600000', '000001']
    :param startDate: 开始日期，格式：'YYYY-MM-DD'
    :param endDate: 结束日期，格式：'YYYY-MM-DD'
    :param field: 需要获取的字段类型，例如：['closePrice']，不填的话，默认获取所有字段；
                  可用的field包括：[productID, instrumentID, tradingDate, tradingTime,
                  openPrice, highPrice, lowPrice, closePrice, volume, turnover]
    :param chunksize: 以分段的形式获取chunksize大小的数据
    :param baseDate: 获取复权数据时的默认基准日，可填：日期，'start'，'end'，以及None，默认为None：不复权。
                     'YYYY-MM-DD'：以固定日期为复权基准日。若该日不是交易日，向前调整至最近的交易日；
                     'start'：以startDate起始日期为基准日。若该日不是交易日，向前调整至最近的交易日；
                     'end'：以endDate结束日期为基准日。若该日不是交易日，向前调整至最近的交易日；
                     None：不复权
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :param instrumentIDasCol: 联合使用field以及instrumentIDs作为column的名字
    :return: pandas.DataFrame
    """

    engine = createEngine('WindDB')
    sql = u"select * from ASHAREEODPRICES"
    names_mapping = NAMES_SETTINGS['equity_eod']
    if field != "*":
        if isinstance(field, str):
            field = [field]

        if 'instrumentID' not in field:
            field.append('instrumentID')
        if 'tradingDate' not in field:
            field.append('tradingDate')
        if 'tradingTime' not in field:
            field.append('tradingTime')
        if 'closePrice' not in field:
            field.append('closePrice')

    names = field_names_mapping(field, names_mapping)
    raw_names, alias = zip(*names)

    if isinstance(instrumentIDList, str):
        instrumentIDList = [instrumentIDList]

    suffixed_instrument_ids = []
    for i, ins in enumerate(instrumentIDList):
        if ins.startswith('6'):
            ins = ins[:6] + '.SH'
        else:
            ins = ins[:6] + '.SZ'
        suffixed_instrument_ids.append(ins)

    index_str = list_to_str(suffixed_instrument_ids, sep=u"'")
    ins_condition = Condition(names_mapping[u'instrumentID'], index_str, u"in")

    left_td_condition = Condition(names_mapping[u'tradingDate'], startDate.replace('-', ''), '>=')
    right_td_condition = Condition(names_mapping[u'tradingDate'], endDate.replace('-', ''), '<=')

    whole_conditon = ins_condition & left_td_condition & right_td_condition
    sql += u" where " + whole_conditon.__str__()
    sql += " order by " + names_mapping[u'tradingDate']

    data = pd.read_sql(sql, engine, chunksize=chunksize)

    if not chunksize:
        data = _format_data(data, names_mapping, raw_names, names)
        if baseDate:
        # to adjust the price data for dividends events
            instrumentIDList = [ins[:6] for ins in suffixed_instrument_ids]
            baseFactor, dateRangeFactors = _getAdjustPriceTable(baseDate, startDate, endDate, 'WindDB', instrumentIDList)
            data = _adjustPrice(baseFactor, dateRangeFactors, data)

        data['securityID'] = _generateSecurityID(data[u'instrumentID'], ASSET_TYPE.EQUITY)
        data = _setTimeStamp(data,  ASSET_TYPE.EQUITY, BAR_TYPE.EOD, instrumentIDasCol)

        if instrumentIDasCol:
            return _fillnanValue(data)
        else:
            return data

        return data
    else:
        return _return_data_in_chunk(data,
                                     baseDate,
                                     suffixed_instrument_ids,
                                     startDate,
                                     endDate,
                                     instrumentIDasCol,
                                     names_mapping,
                                     raw_names,
                                     names)

