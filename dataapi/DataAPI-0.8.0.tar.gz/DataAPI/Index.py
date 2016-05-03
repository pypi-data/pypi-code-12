# -*- coding: utf-8 -*-
u"""
Created on 2015-11-12

@author: cheng.li, weijun.shen
"""

import pandas as pd
from DataAPI.MarketDataLoader import getBarData
from DataAPI.MarketDataLoader import ASSET_TYPE
from DataAPI.MarketDataLoader import BAR_TYPE
from DataAPI.MasterDataLoader import getIndexConstitutionInfo
from DataAPI.MarketDataLoader import _setTimeStamp
from DataAPI.MarketDataLoader import _fillnanValue
from DataAPI.Equity import _format_data
from DataAPI.Utilities import enableCache
from DataAPI.Utilities import cleanColsForUnicode
from DataAPI.Utilities import createEngine
from DataAPI.Utilities import list_to_str
from DataAPI.Utilities import NAMES_SETTINGS
from DataAPI.Utilities import field_names_mapping
from DataAPI.Utilities import _generateSecurityID
from DataAPI.Utilities import ASSET_TYPE
from DataAPI.SqlExpressions import Condition


@enableCache
@cleanColsForUnicode
def GetIndexBarMin1(instrumentIDList, startDate, endDate, field="*", chunksize=None, forceUpdate=True, instrumentIDasCol=False):
    u"""

    获取指数1分钟线数据

    :param instrumentIDList: 证券名或者列表，例如：'000300'或者['000300']
    :param startDate: 开始日期，格式：'YYYY-MM-DD'
    :param endDate: 结束日期，格式：'YYYY-MM-DD'
    :param field: 需要获取的字段类型，例如：['closePrice']，不填的话，默认获取所有字段；
                  可用的field包括：[productID, instrumentID, tradingDate, tradingTime,
                  openPrice, highPrice, lowPrice, closePrice, volume, turnover]
    :param chunksize: 以分段的形式获取chunksize大小的数据
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :param instrumentIDasCol: 联合使用field以及instrumentIDs作为column的名字
    :return: pandas.DataFrame
    """
    return getBarData(instrumentIDList, startDate, endDate, ASSET_TYPE.INDEX, BAR_TYPE.MIN1, field, chunksize, None, instrumentIDasCol)


@enableCache
@cleanColsForUnicode
def GetIndexBarMin5(instrumentIDList, startDate, endDate, field="*", chunksize=None, forceUpdate=True, instrumentIDasCol=False):
    u"""

    获取指数5分钟线数据

    :param instrumentIDList: 证券名或者列表，例如：'000300'或者['000300']
    :param startDate: 开始日期，格式：'YYYY-MM-DD'
    :param endDate: 结束日期，格式：'YYYY-MM-DD'
    :param field: 需要获取的字段类型，例如：['closePrice']，不填的话，默认获取所有字段；
                  可用的field包括：[productID, instrumentID, tradingDate, tradingTime,
                  openPrice, highPrice, lowPrice, closePrice, volume, turnover]
    :param chunksize: 以分段的形式获取chunksize大小的数据
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :param instrumentIDasCol: 联合使用field以及instrumentIDs作为column的名字
    :return: pandas.DataFrame
    """
    return getBarData(instrumentIDList, startDate, endDate, ASSET_TYPE.INDEX, BAR_TYPE.MIN5, field, chunksize, None, instrumentIDasCol)


def _return_data_in_chunk(generator,
                          instrumentIDList,
                          startDate,
                          endDate,
                          instrumentIDasCol,
                          names_mapping,
                          raw_names,
                          names):
    for chunk in generator:
        chunk = _format_data(chunk, names_mapping, raw_names, names)
        chunk = _setTimeStamp(chunk, ASSET_TYPE.INDEX, BAR_TYPE.EOD, instrumentIDasCol)
        chunk['securityID'] = _generateSecurityID(chunk[u'instrumentID'], ASSET_TYPE.INDEX)
        if instrumentIDasCol:
            yield _fillnanValue(chunk)
        else:
            yield chunk



@enableCache
@cleanColsForUnicode
def GetIndexBarEOD(instrumentIDList, startDate, endDate, field="*", chunksize=None, forceUpdate=True, instrumentIDasCol=False):
    u"""

    获取指数日线线数据

    :param instrumentIDList: 证券名或者列表，例如：'000300'或者['000300']
    :param startDate: 开始日期，格式：'YYYY-MM-DD'
    :param endDate: 结束日期，格式：'YYYY-MM-DD'
    :param field: 需要获取的字段类型，例如：['closePrice']，不填的话，默认获取所有字段；
                  可用的field包括：[productID, instrumentID, tradingDate, tradingTime,
                  openPrice, highPrice, lowPrice, closePrice, volume, turnover]
    :param chunksize: 以分段的形式获取chunksize大小的数据
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :param instrumentIDasCol: 联合使用field以及instrumentIDs作为column的名字
    :return: pandas.DataFrame
    """
    engine = createEngine('WindDB')
    sql = u"select * from AINDEXEODPRICES"
    names_mapping = NAMES_SETTINGS['index_eod']
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
        if ins.startswith('0'):
            ins = ins[:6] + '.SH'
        elif ins.startswith('3'):
            ins = ins[:6] + '.SZ'
        else:
            ins = ins[:6] + '.CSI'
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
        data['securityID'] = _generateSecurityID(data[u'instrumentID'], ASSET_TYPE.INDEX)
        data = _setTimeStamp(data, ASSET_TYPE.INDEX, BAR_TYPE.EOD, instrumentIDasCol)

        if instrumentIDasCol:
            return _fillnanValue(data)
        else:
            return data

        return data
    else:
        return _return_data_in_chunk(data,
                                     suffixed_instrument_ids,
                                     startDate,
                                     endDate,
                                     instrumentIDasCol,
                                     names_mapping,
                                     raw_names,
                                     names)


def GetIndexConstitutionInfo(instrumentIDList, refDate=None, field='*', forceUpdate=True):
    u"""

    获取指定日的指数成分股信息

    :param instrumentIDList: 证券名或者列表，例如：'000300'或者['000300']
    :param refDate: 基准日，格式：'YYYY-MM-DD'
    :param field: 需要获取的字段类型，例如：['inDate']，不填的话，默认获取所有字段；
                  可用的field包括：[instrumentID, windCode, conInstrumentID,
                  conWindCode, inDate, outDate]
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :return: pandas.DataFrame
    """
    return getIndexConstitutionInfo(instrumentIDList, refDate, field)
