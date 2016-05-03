# -*- coding: utf-8 -*-
u"""
Created on 2015-11-12

@author: cheng.li, weijun.shen
"""

from DataAPI.MarketDataLoader import getBarData
from DataAPI.MarketDataLoader import ASSET_TYPE
from DataAPI.MarketDataLoader import BAR_TYPE
from DataAPI.Utilities import enableCache
from DataAPI.Utilities import cleanColsForUnicode


@enableCache
@cleanColsForUnicode
def GetFutureBarMin1(instrumentIDList, startDate, endDate, field="*", chunksize=None, forceUpdate=True, instrumentIDasCol=False):
    u"""

    获取期货1分钟线数据

    :param instrumentIDList: 证券名或者列表，例如：'IF1506'或者['IF1502', 'IH1506']
    :param startDate: 开始日期，格式：'YYYY-MM-DD'
    :param endDate: 结束日期，格式：'YYYY-MM-DD'
    :param field: 需要获取的字段类型，例如：['closePrice']，不填的话，默认获取所有字段；
                  可用的field包括：[productID, instrumentID, tradingDate, tradingTime,
                  openPrice, highPrice, lowPrice, closePrice, volume, turnover, matchItems]
    :param chunksize: 以分段的形式获取chunksize大小的数据
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :param instrumentIDasCol: 联合使用field以及instrumentIDs作为column的名字
    :return: pandas.DataFrame
    """
    return getBarData(instrumentIDList, startDate, endDate, ASSET_TYPE.FUTURES, BAR_TYPE.MIN1, field, chunksize, None, instrumentIDasCol)


@enableCache
@cleanColsForUnicode
def GetFutureBarMin5(instrumentIDList, startDate, endDate, field="*", chunksize=None, forceUpdate=True, instrumentIDasCol=False):
    u"""

    获取期货5分钟线数据

    :param instrumentIDList: 证券名或者列表，例如：'IF1506'或者['IF1502', 'IH1506']
    :param startDate: 开始日期，格式：'YYYY-MM-DD'
    :param endDate: 结束日期，格式：'YYYY-MM-DD'
    :param field: 需要获取的字段类型，例如：['closePrice']，不填的话，默认获取所有字段；
                  可用的field包括：[productID, instrumentID, tradingDate, tradingTime,
                  openPrice, highPrice, lowPrice, closePrice, volume, turnover, matchItems]
    :param chunksize: 以分段的形式获取chunksize大小的数据
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :param instrumentIDasCol: 联合使用field以及instrumentIDs作为column的名字
    :return: pandas.DataFrame
    """
    return getBarData(instrumentIDList, startDate, endDate, ASSET_TYPE.FUTURES, BAR_TYPE.MIN5, field, chunksize, None, instrumentIDasCol)


@enableCache
@cleanColsForUnicode
def GetFutureBarMin5Continuing(productIDList, startDate, endDate, field="*", chunksize=None, forceUpdate=True, productIDasCol=False):
    u"""

    获取期货连续合约5分钟线数据

    :param productIDList: 证券名或者列表，例如：'IF'或者['IF', 'IH']
    :param startDate: 开始日期，格式：'YYYY-MM-DD'
    :param endDate: 结束日期，格式：'YYYY-MM-DD'
    :param field: 需要获取的字段类型，例如：['closePrice']，不填的话，默认获取所有字段；
                  可用的field包括：[productID, instrumentID, tradingDate, tradingTime,
                  openPrice, highPrice, lowPrice, closePrice, volume, turnover, matchItems]
    :param chunksize: 以分段的形式获取chunksize大小的数据
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :param productIDasCol: 联合使用field以及productIDs作为column的名字
    :return: pandas.DataFrame
    """
    return getBarData(productIDList, startDate, endDate, ASSET_TYPE.FUTURES_CON, BAR_TYPE.MIN5, field, chunksize, None, productIDasCol)


@enableCache
@cleanColsForUnicode
def GetFutureBarEOD(instrumentIDList, startDate, endDate, field="*", chunksize=None, forceUpdate=True, instrumentIDasCol=False):
    u"""

    获取期货日线数据

    :param instrumentIDList: 证券名或者列表，例如：'IF1506'或者['IF1502', 'IH1506']
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
    return getBarData(instrumentIDList, startDate, endDate, ASSET_TYPE.FUTURES, BAR_TYPE.EOD, field, chunksize, None, instrumentIDasCol)


@enableCache
@cleanColsForUnicode
def GetFutureBarEODContinuing(productIDList, startDate, endDate, field="*", chunksize=None, forceUpdate=True, productIDasCol=False):
    u"""

    获取期货连续合约日线数据

    :param productIDList: 证券名或者列表，例如：'IF'或者['IF', 'IH']
    :param startDate: 开始日期，格式：'YYYY-MM-DD'
    :param endDate: 结束日期，格式：'YYYY-MM-DD'
    :param field: 需要获取的字段类型，例如：['closePrice']，不填的话，默认获取所有字段；
                  可用的field包括：[productID, instrumentID, tradingDate, tradingTime,
                  openPrice, highPrice, lowPrice, closePrice, volume, turnover]
    :param chunksize: 以分段的形式获取chunksize大小的数据
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :param productIDasCol: 联合使用field以及productIDs作为column的名字
    :return: pandas.DataFrame
    """
    return getBarData(productIDList, startDate, endDate, ASSET_TYPE.FUTURES_CON, BAR_TYPE.EOD, field, chunksize, None, productIDasCol)
