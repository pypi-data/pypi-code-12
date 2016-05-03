# -*- coding: utf-8 -*-
u"""
Created on 2016-1-11

@author: cheng.li, weijun.shen, yuchen.lai
"""

import tushare as ts
import pandas as pd
from DataAPI.Utilities import Settings
from DataAPI.Utilities import enableCache
from DataAPI.Utilities import cleanColsForUnicode
from DataAPI.Utilities import str_to_list


class MarketWrapper:
    def __init__(self):
        self.market = ts.Market()

    def IndustryTickRTSnapshot(self, *args, **kwargs):
        try:
            return self.market.IndustryTickRTSnapshot(*args, **kwargs)
        except TypeError:
            raise ValueError('Please set the token for DataYes (using api.Settings.set_tocken(...)')


@enableCache
@cleanColsForUnicode
def GetIndustryNetCashSnapshot(industryID=None, industryName=None, forceUpdate=True):
    u"""

    获取行业资金流向的快照

    :param industryID: 证监会行业分类id，可以为列表，例如: ['J66', 'J68']
    :param industryName: 证监会分类行业名称，例如：'保险业'
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :return: pandas.DataFrame
    """

    market = Settings.market()

    if industryID is not None:
        industryID = str_to_list(industryID)

        industryID = [ind.upper() for ind in industryID]
        industryID = ','.join(industryID)

        rawData = market.IndustryTickRTSnapshot(securityID=industryID)
        if rawData.empty:
            raise ValueError('No data returned for cash snapshot. '
                             'It may due to missing privilege or service not available')
        specific = rawData[['netInflowXL',
                            'netInflowL',
                            'netInflowM',
                            'netInflowS',
                            'dataDate',
                            'dataTime',
                            'type',
                            'shortNM']]
    elif industryName is not None:
        rawData = market.IndustryTickRTSnapshot()
        if rawData.empty:
            raise ValueError('No data returned for cash snapshot. '
                             'It may due to missing privilege or service not available')
        specific = rawData[rawData['shortNM'] == industryName] \
            [['netInflowXL', 'netInflowL', 'netInflowM', 'netInflowS', 'dataDate', 'dataTime', 'type', 'shortNM']]
    else:
        specific = market.IndustryTickRTSnapshot()
        if specific.empty:
            raise ValueError('No data returned for cash snapshot. '
                             'It may due to missing privilege or service not available')
        specific = specific \
            [['netInflowXL', 'netInflowL', 'netInflowM', 'netInflowS', 'dataDate', 'dataTime', 'type', 'shortNM']]

    res = {'netCashFlow': specific[['netInflowXL', 'netInflowL', 'netInflowM', 'netInflowS']].sum(axis=1),
           'industryName': specific['shortNM'],
           'industryID': specific['type'],
           'dateTime': pd.to_datetime(specific['dataDate'] + ' ' + specific['dataTime'], format="%Y-%m-%d %H:%M:%S")}

    return pd.DataFrame(res)

