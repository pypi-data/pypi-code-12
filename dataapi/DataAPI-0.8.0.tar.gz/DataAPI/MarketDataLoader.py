# -*- coding: utf-8 -*-
u"""
Created on 2015-11-12

@author: cheng.li, weijun.shen
"""

from __future__ import division
import warnings
import pandas as pd
from DataAPI.Utilities import createEngine
from DataAPI.Utilities import list_to_str
from DataAPI.Utilities import NAMES_SETTINGS
from DataAPI.Utilities import SH_INDEX_MAPPINGS
from DataAPI.Utilities import REV_SH_INDEX_MAPPINGS
from DataAPI.Utilities import ASSET_TYPE
from DataAPI.Utilities import BAR_TYPE
from DataAPI.Utilities import _generateSecurityID
from DataAPI.Utilities import str_to_list
from DataAPI.Utilities import _setTimeStamp


warnings.simplefilter('always', UserWarning)


def _createSqlQuery(field, tableName, inst, startDate, endDate, aType):
    if tableName == 'datacenter_futures.dbo.FUT_EOD_PATCH' or tableName == 'datacenter_futures.dbo.FUT_EOD_CONTINUING':
        return "select {0:s} from {1:s} where {2:s} and tradingDate >='{3:s}' and tradingDate <='{4:s}'" \
            .format(field,
                    tableName,
                    _createInstrumetsList(inst, aType),
                    startDate,
                    endDate)

    return "select {0:s} from {1:s} where {2:s} and tradingDate >='{3:s}' and tradingDate <='{4:s}'" \
        .format(field,
                tableName,
                _createInstrumetsList(inst, aType),
                startDate,
                endDate)


def _adjustFutDataByMultiplier(data):
    if 'openPrice' in data:
        data['openPrice'] *= data['multiplier']
    if 'highPrice' in data:
        data['highPrice'] *= data['multiplier']
    if 'lowPrice' in data:
        data['lowPrice'] *= data['multiplier']
    if 'closePrice' in data:
        data['closePrice'] *= data['multiplier']
    return data


def _getBucketSymbolsData(params):
    s = params[0]
    if len(s) == 0:
        return pd.DataFrame()
    tableName = params[1]
    startDate = params[2]
    endDate = params[3]
    field = params[4]
    tag = params[5]
    aType = params[6]
    sql = _createSqlQuery(field, tableName, s, startDate, endDate, aType)
    engine = createEngine(tag)
    data = pd.read_sql(sql, engine)
    if aType == ASSET_TYPE.FUTURES_CON:
        data = _adjustFutDataByMultiplier(data)
    return data


def _createInstrumetsList(instrumentIDList, aType):
    if aType == ASSET_TYPE.FUTURES_CON:
        return "productID in (" + ",".join(["'" + str(s) + "'" for s in instrumentIDList]) + ")"
    else:
        return "instrumentID in (" + ",".join(["'" + str(s) + "'" for s in instrumentIDList]) + ")"


def _extractCodeInformation(instrumentIDList, tag):
    instrumentIDList = str_to_list(instrumentIDList)

    if tag == "EQY":
        return [instrument[:6] for instrument in instrumentIDList]
    elif tag == "INDEX":
        instruments = [instrument[:6] for instrument in instrumentIDList]

        for i, ins in enumerate(instruments):
            if ins in SH_INDEX_MAPPINGS:
                ins = SH_INDEX_MAPPINGS[ins]
            elif ins.startswith('00'):
                ins = '99' + ins[2:]
            elif ins.startswith('99'):
                try:
                    official_code = REV_SH_INDEX_MAPPINGS[ins[:6]]
                except KeyError:
                    official_code = '00' + ins[2:6]
                warnings.warn("legacy codes {0} is used for an index in SSE. "
                              "The official code should be {1}.zicn. "
                              "These legacy codes will be removed in the future"
                              .format(ins, official_code), UserWarning)
            instruments[i] = ins
        return instruments
    else:
        return [instrument for instrument in instrumentIDList]


def _fillnanValue(data):
    # instruments = data.columns.get_level_values(1).unique()
    #
    # for instrument in instruments:
    #     inst_data = data.loc[:, pd.IndexSlice[:, instrument]]
    #     fields = inst_data.columns.get_level_values(0)
    #     firstValidCloseIndex = data.loc[:, pd.IndexSlice['closePrice', instrument]].first_valid_index()
    #     lastValidCloseIndex = data.loc[:, pd.IndexSlice['closePrice', instrument]].last_valid_index()
    #     data.loc[firstValidCloseIndex:lastValidCloseIndex, pd.IndexSlice['closePrice', instrument]] = \
    #         inst_data.loc[firstValidCloseIndex:lastValidCloseIndex, pd.IndexSlice['closePrice', instrument]].fillna(method='pad')
    #     filledClose = data.loc[:, pd.IndexSlice['closePrice', instrument]]
    #     if 'openPrice' in fields:
    #         data.loc[firstValidCloseIndex:lastValidCloseIndex, pd.IndexSlice['openPrice', instrument]] = \
    #             inst_data.loc[firstValidCloseIndex:lastValidCloseIndex, pd.IndexSlice['openPrice', instrument]].fillna(value=filledClose)
    #     if 'highPrice' in fields:
    #         data.loc[firstValidCloseIndex:lastValidCloseIndex, pd.IndexSlice['highPrice', instrument]] = \
    #             inst_data.loc[firstValidCloseIndex:lastValidCloseIndex, pd.IndexSlice['highPrice', instrument]].fillna(value=filledClose)
    #     if 'lowPrice' in fields:
    #         data.loc[firstValidCloseIndex:lastValidCloseIndex, pd.IndexSlice['lowPrice', instrument]] = \
    #             inst_data.loc[firstValidCloseIndex:lastValidCloseIndex, pd.IndexSlice['lowPrice', instrument]].fillna(value=filledClose)
    #     if 'volume' in fields:
    #         data.loc[firstValidCloseIndex:lastValidCloseIndex, pd.IndexSlice['volume', instrument]] = \
    #             inst_data.loc[firstValidCloseIndex:lastValidCloseIndex, pd.IndexSlice['volume', instrument]].fillna(value=0)
    #     if 'turnover' in fields:
    #         data.loc[firstValidCloseIndex:lastValidCloseIndex, pd.IndexSlice['turnover', instrument]] = \
    #             inst_data.loc[firstValidCloseIndex:lastValidCloseIndex, pd.IndexSlice['turnover', instrument]].fillna(value=0)
    return data


def _dbConfiguration(instrumentIDList, aType, bType, field="*"):

    if aType == ASSET_TYPE.FUTURES and bType == BAR_TYPE.EOD:
        names_mapping = NAMES_SETTINGS['future_eod']
    elif aType == ASSET_TYPE.FUTURES_CON and bType == BAR_TYPE.EOD:
        names_mapping = NAMES_SETTINGS['future_eod_con']
    elif aType == ASSET_TYPE.FUTURES_CON and bType == BAR_TYPE.MIN5:
        names_mapping = NAMES_SETTINGS['market_data_con']
    else:
        names_mapping = NAMES_SETTINGS['market_data']

    if aType == ASSET_TYPE.EQUITY:
        tag = "EQY"
        _DB = "datacenter_eqy"
    elif aType == ASSET_TYPE.FUTURES or aType == ASSET_TYPE.FUTURES_CON:
        tag = "FUT"
        _DB = "datacenter_futures"
    elif aType == ASSET_TYPE.INDEX:
        tag = "INDEX"
        _DB = "datacenter_eqy"
    elif aType == ASSET_TYPE.OPTION:
        tag = "OPTION"

    if aType != ASSET_TYPE.EQUITY and aType != ASSET_TYPE.FUTURES and aType != ASSET_TYPE.FUTURES_CON:
        if bType == BAR_TYPE.EOD:
            tabName = "EOD"
        elif bType == BAR_TYPE.MIN5:
            tabName = "5MIN"
        elif bType == BAR_TYPE.MIN1:
            tabName = "1MIN"
    elif aType == ASSET_TYPE.FUTURES_CON:
        if bType == BAR_TYPE.EOD:
            tabName = "EOD_CONTINUING"
        elif bType == BAR_TYPE.MIN5:
            tabName = "5MIN_CONTINUING"
        else:
            raise ValueError("There is not bar type other than EOD or 5Min.")
    else:
        if bType == BAR_TYPE.EOD:
            tabName = "EOD_PATCH"
        elif bType == BAR_TYPE.MIN5:
            tabName = "5MIN_PATCH"
        elif bType == BAR_TYPE.MIN1:
            tabName = "1MIN_PATCH_2016"

    instrumentIDList = _extractCodeInformation(instrumentIDList, tag)

    tableName = _DB + ".dbo." + tag + "_" + tabName

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
        if aType == ASSET_TYPE.FUTURES_CON:
            if 'multiplier' not in field:
                field.append('multiplier')
            if 'productID' not in field:
                field.append('productID')
    field = list_to_str(field, sep=u'', default_names=names_mapping)

    return instrumentIDList, tableName, field, _DB


def _getAdjustPriceTable(baseDate, startDate, endDate, _DB, instrumentIDList):

    baseDate = ''.join(baseDate.split('-'))
    startDate = ''.join(startDate.split('-'))
    endDate = ''.join(endDate.split('-'))

    if baseDate.lower() == 'start':
        baseDate = startDate
    elif baseDate.lower() == 'end':
        baseDate = endDate
    else:
        baseDate = ''.join(baseDate.split('-'))

    instrumentIDList = [s[:6] + '.sh' if s.startswith('6') else s[:6] + '.sz' for s in instrumentIDList]

    tableName = _DB + ".dbo.ASHAREEODPRICES"

    # get the base date factor
    sql = "SELECT LEFT(B.S_INFO_WINDCODE,6) as instrumentID, B.S_DQ_ADJFACTOR AS baseFactor " \
          "FROM {0:s} B " \
          "WHERE B.S_INFO_WINDCODE IN {1:s} " \
          "AND B.TRADE_DT = {2:s}" \
          .format(tableName,
                  "("+(",".join("'"+inst+"'" for inst in instrumentIDList))+")",
                  baseDate)

    baseFactor = pd.read_sql(sql, createEngine(_DB)).groupby('instrumentID', as_index=False).first()

    # get the factor in the date range
    sql = "SELECT LEFT(B.S_INFO_WINDCODE,6) " \
          "as instrumentID, CAST(B.TRADE_DT AS DATE) as tradingDate, B.S_DQ_ADJFACTOR as factor " \
          "FROM {0:s} B " \
          "WHERE B.S_INFO_WINDCODE IN {1:s} " \
          "AND B.TRADE_DT >= {2:s} " \
          "AND B.TRADE_DT <= {3:s}" \
          .format(tableName,
                  "("+(",".join("'"+inst+"'" for inst in instrumentIDList))+")",
                  startDate,
                  endDate)

    dateRangeFactors = pd.read_sql(sql, createEngine(_DB))
    return baseFactor, dateRangeFactors


def _adjustPrice(baseFactor, dateRangeFactors, rawData):

    data = rawData.merge(baseFactor, left_on='instrumentID', right_on='instrumentID', how='left')

    data = data.merge(dateRangeFactors,
                      left_on=['instrumentID', 'tradingDate'],
                      right_on=['instrumentID', 'tradingDate'],
                      how='left')

    data['adjuster'] = data['factor'].values.astype(float) / data['baseFactor'].values.astype(float)

    if 'openPrice' in data:
        data['openPrice'] *= data['adjuster']
    if 'highPrice' in data:
        data['highPrice'] *= data['adjuster']
    if 'closePrice' in data:
        data['closePrice'] *= data['adjuster']
    if 'lowPrice' in data:
        data['lowPrice'] *= data['adjuster']
    import numpy as np
    if np.min(data.closePrice) < 1e-10:
        warnings.warn("There is some thing wrong with adjust data", UserWarning)
    data = data.drop(['baseFactor', 'factor', 'adjuster'], axis=1)
    return data


def _transform_instrument_id(x):
    if x.startswith('99'):
        if x in REV_SH_INDEX_MAPPINGS:
            return REV_SH_INDEX_MAPPINGS[x]
        else:
            return '00' + x[2:]
    return x


def _revert_back_instrument_id(data, aType):
    if aType == ASSET_TYPE.INDEX:
        if 'instrumentID' in data:
            data['instrumentID'] = data['instrumentID'].apply(_transform_instrument_id)
        if 'productID' in data:
            data['productID'] = data['productID'].apply(_transform_instrument_id)

    return data


def _GetBarDataInChunk(instrumentIDList, startDate, endDate, aType, bType, field="*", chunksize=None, baseDate=None, instrumentIDasCol=False):

    u"""

    统一的获取bar数据的方式， 返回时间序列的DataFrame, 分段获取

    :param instrumentIDList: 证券名或者列表，例如：'600000'或者['600000', '000001']
    :param startDate: 开始日期，格式：'YYYY-MM-DD'
    :param endDate: 结束日期，格式：'YYYY-MM-DD'
    :param aType: 资产类型，例如：ASSET_TYPE.EQUITY
    :param bType: bar的类型，例如：BAR_TYPE.MIN1
    :param field: 需要获取的字段类型，例如：['closePrice']，不填的话，默认获取所有字段
    :param chunksize: 以分段的形式获取chunksize大小的数据
    :param baseDate: 获取复权数据时的默认基准日，默认为None：不复权
    :param instrumentIDasCol: 联合使用field以及instrumentIDs作为column的名字
    :return: pandas.DataFrame
    """

    instrumentIDList, tableName, field, _DB = _dbConfiguration(instrumentIDList, aType, bType, field)
    sql = _createSqlQuery(field, tableName, instrumentIDList, startDate, endDate, aType)
    datas = pd.read_sql(sql, createEngine(_DB), chunksize=chunksize)

    if baseDate != None:
        # to adjust the price data for dividends events
        baseFactor, dateRangeFactors = _getAdjustPriceTable(baseDate, startDate, endDate, _DB, instrumentIDList)

    for chunk in datas:
        if aType == ASSET_TYPE.FUTURES_CON:
            chunk = _adjustFutDataByMultiplier(chunk)
        if baseDate != None:
            chunk = _adjustPrice(baseFactor, dateRangeFactors, chunk)
        data = _setTimeStamp(chunk, aType, bType, instrumentIDasCol)
        data = _revert_back_instrument_id(data, aType)
        if aType == ASSET_TYPE.FUTURES_CON:
            data['securityID'] = _generateSecurityID(data[u'productID'], aType)
        else:
            data['securityID'] = _generateSecurityID(data[u'instrumentID'], aType)
        if instrumentIDasCol:
            yield _fillnanValue(data)
        else:
            yield data


def _GetBarDataInWhole(instrumentIDList, startDate, endDate, aType, bType, field="*", baseDate=None, instrumentIDasCol=False):
    u"""

    统一的获取bar数据的方式， 返回时间序列的DataFrame, 一次性获取所有数据

    :param instrumentIDList: 证券名或者列表，例如：'600000'或者['600000', '000001']
    :param startDate: 开始日期，格式：'YYYY-MM-DD'
    :param endDate: 结束日期，格式：'YYYY-MM-DD'
    :param aType: 资产类型，例如：ASSET_TYPE.EQUITY
    :param bType: bar的类型，例如：BAR_TYPE.MIN1
    :param field: 需要获取的字段类型，例如：['closePrice']，不填的话，默认获取所有字段
    :param baseDate: 获取复权数据时的默认基准日，默认为None：不复权
    :param instrumentIDasCol: 联合使用field以及instrumentIDs作为column的名字
    :return: pandas.DataFrame
    """

    instrumentIDList, tableName, field, _DB = _dbConfiguration(instrumentIDList, aType, bType, field)

    data = _getBucketSymbolsData((instrumentIDList, tableName, startDate, endDate, field, _DB, aType))

    if baseDate != None:
        # to adjust the price data for dividends events
        baseFactor, dateRangeFactors = _getAdjustPriceTable(baseDate, startDate, endDate, _DB, instrumentIDList)
        data = _adjustPrice(baseFactor, dateRangeFactors, data)

    data = _setTimeStamp(data, aType, bType, instrumentIDasCol)
    data = _revert_back_instrument_id(data, aType)
    if aType == ASSET_TYPE.FUTURES_CON:
        data['securityID'] = _generateSecurityID(data[u'productID'], aType)
    else:
        data['securityID'] = _generateSecurityID(data[u'instrumentID'], aType)

    if instrumentIDasCol:
        return _fillnanValue(data)
    else:
        return data


def getBarData(instrumentIDList, startDate, endDate, aType, bType, field="*", chunksize=None, baseDate=None, instrumentIDasCol=False):
    if not chunksize:
        return _GetBarDataInWhole(instrumentIDList, startDate, endDate, aType, bType, field, baseDate, instrumentIDasCol)
    else:
        return _GetBarDataInChunk(instrumentIDList, startDate, endDate, aType, bType, field, chunksize, baseDate, instrumentIDasCol)

