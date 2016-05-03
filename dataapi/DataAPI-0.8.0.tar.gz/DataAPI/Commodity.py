# -*- coding: utf-8 -*-
u"""
Created on 2016-2-16

@author: cheng.li, weijun.shen
"""

import pandas as pd
from DataAPI.Utilities import enableCache
from DataAPI.Utilities import cleanColsForUnicode
from DataAPI.Utilities import createEngine
from DataAPI.Utilities import NAMES_SETTINGS
from DataAPI.Utilities import field_names_mapping
from DataAPI.Utilities import list_to_str
from DataAPI.Utilities import _setTimeStamp
from DataAPI.Utilities import ASSET_TYPE
from DataAPI.Utilities import BAR_TYPE
from DataAPI.SqlExpressions import Condition


def _format_data(data, names_mapping, raw_names, names):
    data[names_mapping[u'tradingDate']] = data[names_mapping[u'tradingDate']].apply(lambda x: x[:4] + '-'
                                                                                              + x[4:6]
                                                                                              + '-'
                                                                                              + x[6:])
    data = data[list(raw_names)]
    data = data.rename(columns=dict(names))
    return data


@enableCache
@cleanColsForUnicode
def GetCommodityStocksInfo(productIDList, startDate, endDate, wareHouse=u'*', field="*", forceUpdate=True):
    u"""

    获取商品期货的每日仓单库存信息

    :param productIDList: 证券名或者列表，例如：'IF'或者['IF', 'IH']
    :param startDate: 开始日期，格式：'YYYY-MM-DD'
    :param endDate: 结束日期，格式：'YYYY-MM-DD'
    :param wareHouse: 所在仓库，例如：[u'江苏:中储无锡']。默认为'*'，获取全部仓库的信息
    :param field: 需要获取的字段类型，例如：['closePrice']，不填的话，默认获取所有字段；
                  可用的field包括：[productID, tradingDate, wareHouse, stocks]
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :return: pandas.DataFrame
    """
    engine = createEngine('WindDB')
    sql = u"select * from CFUTURESWAREHOUSESTOCKS"
    names_mapping = NAMES_SETTINGS['future_stocks']

    if field != "*":
        if isinstance(field, str):
            field = [field]

        if 'productID' not in field:
            field.append('productID')

        if 'tradingDate' not in field:
            field.append('tradingDate')

    if wareHouse != '*':
        if isinstance(wareHouse, str):
            wareHouse = [wareHouse]

    names = field_names_mapping(field, names_mapping)
    raw_names, alias = zip(*names)

    if isinstance(productIDList, str):
        productIDList = [productIDList]

    product_str = list_to_str(productIDList, sep=u"'")
    ins_condition = Condition(names_mapping[u'productID'], product_str, u"in")

    wareHouse_condition = None
    if wareHouse != '*':
        wareHouse_str = list_to_str(wareHouse, sep=u"'")
        wareHouse_condition = Condition(names_mapping[u'wareHouse'], wareHouse_str, u"in")

    left_td_condition = Condition(names_mapping[u'tradingDate'], startDate.replace('-', ''), '>=')
    right_td_condition = Condition(names_mapping[u'tradingDate'], endDate.replace('-', ''), '<=')

    whole_conditon = ins_condition & wareHouse_condition & left_td_condition & right_td_condition
    sql += u" where " + whole_conditon.__str__()
    sql += " order by " + names_mapping[u'tradingDate']

    data = pd.read_sql(sql.encode('utf8'), engine)

    data = _format_data(data, names_mapping, raw_names, names)
    data = _setTimeStamp(data,  ASSET_TYPE.FUTURES_CON, BAR_TYPE.EOD)
    del data['tradingTime']
    return data
