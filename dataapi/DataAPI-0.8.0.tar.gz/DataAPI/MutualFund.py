# -*- coding: utf-8 -*-
u"""
Created on 2016-1-18

@author: cheng.li
"""

import pandas as pd
from DataAPI.Utilities import createEngine
from DataAPI.Utilities import NAMES_SETTINGS
from DataAPI.Utilities import cleanColsForUnicode
from DataAPI.Utilities import enableCache
from DataAPI.Utilities import field_names_mapping
from DataAPI.Utilities import str_to_list
from DataAPI.Utilities import list_to_str
from DataAPI.Utilities import _setTimeStamp
from DataAPI.Utilities import _generateSecurityID
from DataAPI.Utilities import BAR_TYPE
from DataAPI.Utilities import ASSET_TYPE
from DataAPI.SqlExpressions import Condition


def _format_data(data, names_mapping, raw_names, names):
    data = data[list(raw_names)]
    data = data.rename(columns=dict(names))
    return data


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
        chunk = _setTimeStamp(chunk, BAR_TYPE.EOD, instrumentIDasCol)
        chunk['securityID'] = _generateSecurityID(chunk[u'instrumentID'], ASSET_TYPE.EQUITY)
        yield chunk


@enableCache
@cleanColsForUnicode
def GetMutualFundBarMin5(instrumentIDList,
                         startDate,
                         endDate,
                         field="*",
                         chunksize=None,
                         forceUpdate=True,
                         instrumentIDasCol=False):
    engine = createEngine('datacenter_eqy')
    sql = u"select * from FUND_5MIN"
    names_mapping = NAMES_SETTINGS['mutual_fund_min5']
    if field != "*":
        field = str_to_list(field)

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

    instrumentIDList = str_to_list(instrumentIDList)

    index_str = list_to_str(instrumentIDList, sep=u"'")
    ins_condition = Condition(names_mapping[u'instrumentID'], index_str, u"in")

    left_td_condition = Condition(names_mapping[u'tradingDate'], u"'" + startDate + u"'", '>=')
    right_td_condition = Condition(names_mapping[u'tradingDate'], u"'" + endDate + u"'", '<=')

    whole_conditon = ins_condition & left_td_condition & right_td_condition

    sql += u" where " + whole_conditon.__str__()
    sql += " order by " + names_mapping[u'tradingDate']

    data = pd.read_sql(sql, engine, chunksize=chunksize)
    if not chunksize:
        data = _format_data(data, names_mapping, raw_names, names)
        data['securityID'] = _generateSecurityID(data[u'instrumentID'], ASSET_TYPE.MUTUALFUND)
        data = _setTimeStamp(data, BAR_TYPE.MIN5, instrumentIDasCol)
        return data
    else:
        return _return_data_in_chunk(data,
                                     instrumentIDList,
                                     startDate,
                                     endDate,
                                     instrumentIDasCol,
                                     names_mapping,
                                     raw_names,
                                     names)


if __name__ == "__main__":
    data = GetMutualFundBarMin5(['150019', '518880'], '2013-01-01', '2015-01-01', instrumentIDasCol=True)
    print(data)
