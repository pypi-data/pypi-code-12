# -*- coding: utf-8 -*-
u"""
Created on Tue Dec 15 09:50:06 2015

@author: cheng.li, weijun.shen, yucheng.lai
"""
from DataAPI.MasterDataLoader import getFutureInstrumentInfo
from DataAPI.MasterDataLoader import getEquityInstrumentInfo
from DataAPI.Utilities import enableCache
from DataAPI.Utilities import cleanColsForUnicode


@enableCache
@cleanColsForUnicode
def GetFutureInstrumentInfo(instrumentDescList=None, field='*', refdate=None, forceUpdate=True):
    u"""

    获取期货基本信息数据

    :param instrumentDescList: 证券名或者列表，例如：'ZN1502'或者['ZN1502', 'A1502']；不分大小写，例如：'a1502'同'A1502'；
                               支持模糊查询，例如：'if*'返回所有以'IF'开头的证券，'*15*'返回'IF1501','ZN1502'等证券名称中包含'15'的证券及其检索信息；
                               不填的话，默认获取所有证券；
    :param field: 需要获取的字段类型，例如：['market', 'cnName']，不填的话，默认获取所有字段；
                  可用的field包括：[instrumetID, windCode, market, enName, cnName]
    :param refdate: 指定日期，将查询范围限制于当日依然处于交易状态的期货合约，例如：instrumentDescList = 'IF*', refdate=
                    '2015-11-11'时，返回IF1511，IF1512，IF1603，IF1606四份期货的信息，非交易日时返回空值；
                    不填的话，默认不限制具体某交易日；
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :return: pandas.DataFrame
    """
    return getFutureInstrumentInfo(instrumentDescList, field, refdate)


@enableCache
@cleanColsForUnicode
def GetEquityInstrumentInfo(instrumentIDList=None, boardName=None, field="*", refDate=None, forceUpdate=True):
    u"""

    获取股票基本信息数据

    :param instrumentIDList: 证券名称或者列表，例如：'600000'或者['600000', '000001']，默认为None，查询所有证券
    :param boardName: 上市板块名称或者列表，例如：'主板'或者['主板', '创业板']，默认为None，查询所有板块
    :param field: 需要获取的字段类型，例如：['instrumentID', 'windCode']，不填的话，默认获取所有字段；
    :param refDate: 指定日期，将查询范围限制于当日依然处于上市状态的证券，格式为：YYYY-MM-DD
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :return: pandas.DataFrame
    """

    return getEquityInstrumentInfo(instruments=instrumentIDList,
                                   boardName=boardName,
                                   field=field,
                                   refDate=refDate)