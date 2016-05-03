# -*- coding: utf-8 -*-
u"""
Created on 2016-1-4

@author: cheng.li
"""

import copy
import math
import datetime as dt
import functools
import scipy.optimize as opt
import pandas as pd
import numpy as np
from PyFin.POpt.Calculators import calculate_annualized_return
from PyFin.POpt.Calculators import calculate_volatility
from PyFin.POpt.Calculators import calculate_sharp
from PyFin.POpt.Calculators import calculate_sortino
from PyFin.POpt.Calculators import calculate_max_drawdown
from PyFin.POpt.Optimizer import portfolio_optimization
from DataAPI.Utilities import createEngine
from DataAPI.Utilities import NAMES_SETTINGS
from DataAPI.Utilities import list_to_str
from DataAPI.Utilities import enableCache
from DataAPI.Utilities import cleanColsForUnicode
from DataAPI.Utilities import _setTimeStamp
from DataAPI.Utilities import BAR_TYPE
from DataAPI.Utilities import ASSET_TYPE
from DataAPI.SqlExpressions import Condition


@enableCache
@cleanColsForUnicode
def GetHedgeFundInfo(instruments=None, instrumentName=None, field='*', firstInvestType=None, forceUpdate=True):
    u"""

    获取对冲基金基础信息

    :param instruments: 基金代码列表，例如：'XT1515141.XT'。默认为None，获取所有的基金信息
    :param field: 需要获取的字段类型，例如：['firstInvestType']，不填的话，默认获取所有字段；
                  可用的field包括：[instrumentID, fullName, firstInvestType, investScope,
                  maturityDate, advisory]
    :param firstInvestType: 需要获取的基金所属的投资类型列表，例如: [u'期货型']
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :return: pandas.DataFrame
    """

    table_name = 'HEDGEFUND_DESC'

    engine = createEngine('hedge_funds')
    names_mapping = NAMES_SETTINGS[table_name]

    field = list_to_str(field, sep=u'', default_names=names_mapping)

    ins_condition = None
    if instruments:
        instruments_str = list_to_str(instruments)
        ins_condition = Condition(names_mapping[u"instrumentID"], instruments_str, u"in")

    first_invest_condition = None
    if firstInvestType:
        first_invest_srt = list_to_str(firstInvestType)
        first_invest_condition = Condition(names_mapping[u"firstInvestType"], first_invest_srt, u"in")

    name_condition = None
    if instrumentName:
        name_condition = Condition(names_mapping[u"fullName"], "'%" + instrumentName + "%'", u"like")

    sql = u"select {0} from {1}".format(field, table_name)

    whole_condition = None
    if ins_condition:
        whole_condition = ins_condition & first_invest_condition & name_condition
    elif first_invest_condition:
        whole_condition = first_invest_condition & name_condition
    elif name_condition:
        whole_condition = name_condition

    if whole_condition:
        sql += u" where " + whole_condition.__str__()
    data = pd.read_sql(sql, engine)

    if 'instrumentID' in data:
        return data.sort_values('instrumentID').reset_index(drop=True)
    else:
        return data


@enableCache
@cleanColsForUnicode
def GetHedgeFundBarWeek(instruments=None,
                        startDate='2003-01-01',
                        endDate='2015-12-31',
                        field='*',
                        forceUpdate=True,
                        instrumentIDasCol=False):
    u"""

    获取对冲基金历史表现信息(周）

    :param instruments: 基金代码列表，例如：'XT1515141.XT'。默认为None，获取所有基金历史表现
    :param field: 需要获取的字段类型，例如：['logRetAcc']，不填的话，默认获取所有字段；
                  可用的field包括：[tradingDate, instrumentID, navUnit, navAcc,
                  logRetUnit, logRetAcc]
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :param instrumentIDasCol: 联合使用field以及instrumentIDs作为column的名字
    :return: pandas.DataFrame
    """
    engine = createEngine('hedge_funds')

    table_name = 'HEDGEFUND_PEF_WEEK'
    names_mapping = NAMES_SETTINGS[table_name]

    field = list_to_str(field, sep=u'', default_names=names_mapping, forced_names=['tradingDate'])
    sql = u"select {0} from {1}".format(field, table_name)

    ins_condition = None
    if instruments:
        instruments_str = list_to_str(instruments)
        ins_condition = Condition(names_mapping[u"instrumentID"], instruments_str, u"in")

    left_td_condition = Condition(names_mapping[u'tradingDate'], startDate.replace('-', ''), '>=')
    right_td_condition = Condition(names_mapping[u'tradingDate'], endDate.replace('-', ''), '<=')

    whole_condition = left_td_condition & right_td_condition & ins_condition

    if whole_condition:
        sql += u" where " + whole_condition.__str__()

    data = pd.read_sql(sql, engine)
    data['tradingDate'] = data['tradingDate'].apply(lambda x: x[:4] + '-' + x[4:6] + '-' + x[6:8])
    data = _setTimeStamp(data, ASSET_TYPE.HEDGE_FUND, BAR_TYPE.EOD, instrumentIDasCol)
    if instrumentIDasCol:
        data = data[['navAcc', 'navUnit', 'logRetAcc', 'logRetUnit']]
    return data


@enableCache
@cleanColsForUnicode
def GetHedgeFundBarMonth(instruments=None,
                         startDate='2003-01-01',
                         endDate='2015-12-31',
                         field='*',
                         forceUpdate=True,
                         instrumentIDasCol=False):
    u"""

    获取对冲基金历史表现信息(月）

    :param instruments: 基金代码列表，例如：'XT1515141.XT'。默认为None，获取所有基金历史表现
    :param field: 需要获取的字段类型，例如：['logRetAcc']，不填的话，默认获取所有字段；
                  可用的field包括：[tradingDate, instrumentID, navUnit, navAcc,
                  logRetUnit, logRetAcc]
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :param instrumentIDasCol: 联合使用field以及instrumentIDs作为column的名字
    :return: pandas.DataFrame
    """
    engine = createEngine('hedge_funds')

    table_name = 'HEDGEFUND_PEF_MONTH'
    names_mapping = NAMES_SETTINGS[table_name]

    field = list_to_str(field, sep=u'', default_names=names_mapping, forced_names=['tradingDate'])
    sql = u"select {0} from {1}".format(field, table_name)

    ins_condition = None
    if instruments:
        instruments_str = list_to_str(instruments)
        ins_condition = Condition(names_mapping[u"instrumentID"], instruments_str, u"in")

    left_td_condition = Condition(names_mapping[u'tradingDate'], startDate.replace('-', ''), '>=')
    right_td_condition = Condition(names_mapping[u'tradingDate'], endDate.replace('-', ''), '<=')

    whole_condition = left_td_condition & right_td_condition & ins_condition

    if whole_condition:
        sql += u" where " + whole_condition.__str__()

    data = pd.read_sql(sql, engine)
    data['tradingDate'] = data['tradingDate'].apply(lambda x: x[:4] + '-' + x[4:6] + '-' + x[6:8])
    data = _setTimeStamp(data, ASSET_TYPE.HEDGE_FUND, BAR_TYPE.EOD, instrumentIDasCol)
    return data


@enableCache
@cleanColsForUnicode
def GetHedgeFundPool(field='*', refDate=None, forceUpdate=True):
    u"""

    获取指定日期下，基金备选池的信息

    :param field: 需要获取的字段类型，例如：['logRetAcc']，不填的话，默认获取所有字段；
                  可用的field包括：[tradingDate, instrumentID, navUnit, navAcc,
                  logRetUnit, logRetAcc]
    :param refDate: 指定日期，将查询范围限制于当日在基金备选池中的基金，格式为：YYYY-MM-DD；
                    不填的话，默认查询最新的备选池信息
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :return: pandas.DataFrame
    """
    engine = createEngine('hedge_funds')
    table_name = 'HEDGEFUND_POOL'
    names_mapping = NAMES_SETTINGS[table_name]

    ref_condition = None
    if refDate:
        ref_condition = Condition(names_mapping[u'eventDate'], refDate.replace(u'-', u''), u"<=")

    sql = u'select * from {0}'.format(table_name)
    if ref_condition:
        sql += u" where " + ref_condition.__str__()

    data = pd.read_sql(sql, engine)
    data = data.groupby(names_mapping['instrumentID']).last()
    data = data[data.eventType == 'A'][['eventDate']]

    # get the detail info of the instruments
    if field != '*':
        if isinstance(field, str):
            field = [field]
        if 'instrumentID' not in field:
            field.append('instrumentID')

    info_data = GetHedgeFundInfo(list(data.index.values), field=field)
    data = pd.merge(data, info_data, left_index=True, right_on='instrumentID')
    return data.sort_values('instrumentID')


@enableCache
@cleanColsForUnicode
def GetHedgeFundStylePerf(styleName=None, startDate='2012-01-01', endDate='2015-12-31', instrumentIDasCol=False,
                          forceUpdate=True):
    u"""

    获取特定风格的基金类型的历史表现

    :param styleName: 基金风格类型，可选的风格有：[u'债券型', u'多空仓型', u'宏观策略', u'市场中性', u'管理期货', u'股票型', u'货币型']
    :param startDate: 历史表现起始日期
    :param endDate: 历史表现结束日期
    :param instrumentIDasCol: 联合使用field以及instrumentIDs作为column的名字
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :return: pandas.DataFrame
    """
    engine = createEngine('hedge_funds')
    table_name = 'HOWBUY_STYLE_RET'
    names_mapping = NAMES_SETTINGS[table_name]

    ins_condition = None
    if styleName:
        index_str = list_to_str(styleName, sep=u"'")
        ins_condition = Condition(names_mapping[u'howbuyStrategy'], index_str, u"in")

    left_td_condition = Condition(names_mapping[u'tradingDate'], "'" + startDate + "'", '>=')
    right_td_condition = Condition(names_mapping[u'tradingDate'], "'" + endDate + "'", '<=')

    sql = u'select * from {0}'.format(table_name)

    whole_condition = left_td_condition & right_td_condition & ins_condition

    sql += u" where " + whole_condition.__str__()
    data = pd.read_sql(sql, engine)
    data = data.rename(columns={'howbuyStrategy': 'instrumentID'})
    data = _setTimeStamp(data, ASSET_TYPE.HEDGE_FUND, BAR_TYPE.EOD, instrumentIDasCol)
    data.sort_index(inplace=True)
    return data


def score_data(data):
    # 年化收益得分
    data[u'年化收益得分'] = 0.0

    def return_score(x):
        if x > 0.25:
            return 15.0
        elif x > 0.20:
            return 10.
        elif x > 0.10:
            return 8.
        elif x > 0.05:
            return 4.
        else:
            return 0.

    data[u'年化收益得分'] = data[u'年化收益'].apply(return_score)

    # 夏普比率得分
    data[u'sharp得分'] = 0.0

    def sharp_score(x):
        if x > 2.:
            return 20.0
        elif x > 1.5:
            return 16.
        elif x > 1.0:
            return 10.
        elif x > 0.7:
            return 4.
        else:
            return 0.

    data[u'sharp得分'] = data[u'sharp'].apply(sharp_score)

    # 最大回撤得分
    data[u'最大回撤得分'] = 0.0

    def max_drawdown_score(x):
        if x < 0.03 or np.isnan(x):
            return 10.0
        elif x < 0.05:
            return 8.
        elif x < 0.10:
            return 5.
        elif 0.10 < x < 0.15:
            return 2.
        else:
            return 0.

    data[u'最大回撤得分'] = data[u'最大回撤'].apply(max_drawdown_score)

    # sortino得分
    data[u'sortino得分'] = 0.0

    def sortino_score(x, median):
        if x > median or np.isnan(x):
            return 10.
        else:
            return 5.

    median = data[u'sortino'].median()
    data[u'sortino得分'] = data[u'sortino'].apply(functools.partial(sortino_score, median=median))

    # 收益回撤比得分
    data[u'收益回撤比得分'] = 0.0

    def return_to_max_drawdown_score(x):
        if x > 2.5 or np.isnan(x):
            return 10.0
        elif x > 2:
            return 8.
        elif x > 1.5:
            return 5.
        elif x > 1.0:
            return 2.
        else:
            return 0.

    data[u'收益回撤比得分'] = data[u'收益回撤比'].apply(return_to_max_drawdown_score)

    # 波动率得分
    data[u'波动率得分'] = 0.0

    def volatility_score(x, median):
        if x < median:
            return 5.
        else:
            return 2.

    median = data[u'波动率'].median()
    data[u'波动率得分'] = data[u'波动率'].apply(functools.partial(volatility_score, median=median))

    data[u'总分'] = data[u'年化收益得分'] + data[u'sharp得分'] + data[u'最大回撤得分'] + data[u'sortino得分'] + data[u'收益回撤比得分'] + data[
        u'波动率得分']


def interpolate_nav(nav_table, freq='w'):
    dfs = []

    if freq == 'w':
        freq_format = 'W-FRI'
    else:
        freq_format = 'MS'

    for col in nav_table.columns:
        single_df = nav_table[[col]].dropna()
        if single_df.empty:
            continue
        date_index = pd.date_range(single_df.index[0], single_df.index[-1], freq=freq_format)
        new_index = single_df.index.union(date_index)
        single_df = single_df.reindex(new_index)
        single_df = single_df.interpolate(method='time').ix[date_index]
        if len(single_df) >= 2:
            dfs.append(single_df.interpolate(method='time').ix[date_index])
    return pd.concat(dfs, axis=1)


def calculate_log_return(nav_table):
    return np.log(nav_table / nav_table.shift(1))


@enableCache
@cleanColsForUnicode
def perf_combine(instruments, navTable, startDate, endDate, freq='w', forceUpdate=True):
    ext_data = pd.DataFrame()
    int_data = pd.DataFrame()
    if instruments and instruments != 'all':
        if freq == 'w':
            int_data = \
            GetHedgeFundBarWeek(instruments, startDate, endDate, instrumentIDasCol=True, forceUpdate=forceUpdate)[ 'logRetAcc']
        else:
            int_data = \
            GetHedgeFundBarMonth(instruments, startDate, endDate, instrumentIDasCol=True, forceUpdate=forceUpdate)[ 'logRetAcc']
    elif instruments == 'all':
        if freq == 'w':
            int_data = \
                GetHedgeFundBarWeek(None, startDate, endDate, instrumentIDasCol=True, forceUpdate=forceUpdate)['logRetAcc']
        else:
            int_data = \
                GetHedgeFundBarMonth(None, startDate, endDate, instrumentIDasCol=True, forceUpdate=forceUpdate)['logRetAcc']

    if not int_data.empty:
        int_data = int_data[startDate:endDate]
        int_data = interpolate_nav(int_data, freq)

    if not navTable.empty:
        navTable = navTable[startDate:endDate]
        navTable = interpolate_nav(navTable, freq)
        ext_data = calculate_log_return(navTable)

    if not int_data.empty and not ext_data.empty:
        data = pd.merge(int_data, ext_data, left_index=True, right_index=True, how='outer')
    elif not int_data.empty:
        data = int_data
    else:
        data = ext_data
    return data


@enableCache
@cleanColsForUnicode
def GetHedgeFundPerfComparison(instruments=None,
                               startDate='2015-01-01',
                               endDate='2015-12-31',
                               navTable=pd.DataFrame(),
                               sortBy=u'基金代码',
                               ascending=True,
                               forceUpdate=True):
    u"""

    获取指定基金的历史表现风险收益指标以及打分结果。

    :param instruments: 基金wind代码列表，可以为空。若为'all'，则获取所有在池基金的结果。
    :param startDate: 历史表现起始日
    :param endDate: 历史表现结束日
    :param navTable: 外部数据列表
    :param sortBy: 按何字段排序
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :return: pandas.DataFrame
    """
    data = perf_combine(instruments, navTable, startDate, endDate, freq='w', forceUpdate=forceUpdate)

    values = []

    for name in data.columns:
        returns = data[name]
        returns.dropna(inplace=True)
        if len(returns) >= 2:
            start = returns.index[0]
            end = returns.index[-1]
            returns = returns.values

            annualized_return = np.exp(calculate_annualized_return(returns)) - 1.0
            stddev = calculate_volatility(returns)

            max_drawdown = 1.0 - np.exp(-calculate_max_drawdown(returns))
            try:
                sharp = calculate_sharp(returns)
            except ZeroDivisionError:
                sharp = np.nan
            try:
                sortino = calculate_sortino(returns)
            except ZeroDivisionError:
                sortino = np.nan

            ret_to_drawdown = annualized_return / max_drawdown
            values.append([])
            values[-1].extend(
                [name, start, end, annualized_return, stddev, max_drawdown, sharp, sortino, ret_to_drawdown])

    data = pd.DataFrame(data=values, columns=['instrumentID',
                                              'refBegin',
                                              'refEnd',
                                              'annualizedReturn',
                                              'annualizedVolatility',
                                              'maxDrawdown',
                                              'sharp',
                                              'sortino',
                                              'returnToMaxDrawdown'])
    data = data.rename(columns={'instrumentID': u'基金代码',
                                'refBegin': u'参考起始日',
                                'refEnd': u'参考结束日',
                                'annualizedReturn': u'年化收益',
                                'annualizedVolatility': u'波动率',
                                'maxDrawdown': u'最大回撤',
                                'returnToMaxDrawdown': u'收益回撤比'})

    # do the scoring
    score_data(data)
    data.sort_values(sortBy, ascending=ascending, inplace=True)
    data.reset_index(inplace=True, drop=True)
    return data


@enableCache
@cleanColsForUnicode
def GetHedgeFundStyleAnalysis(instruments=None,
                              navTable=pd.DataFrame(),
                              startDate='2012-01-01',
                              endDate='2015-01-01',
                              forceUpdate=True):
    u"""

    获取根据基金历史表现得到的风格分析的结果

    :param instruments: 基金wind代码列表，可以为空。若为空，则使用用户输入的navTable
    :param navTable: N*（M+1）的pandas.DataFrame，表示M个基金历史上N个时间点的净值
    :param startDate: 历史表现起始日，在使用navTable时候会被忽略
    :param endDate:历史表现结束日，在使用navTable时候会被忽略
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :return: pandas.DataFrame
    """
    fund_data = perf_combine(instruments, navTable, startDate, endDate, freq='m', forceUpdate=forceUpdate)

    data = GetHedgeFundStylePerf(startDate=startDate, endDate=endDate, instrumentIDasCol=True)
    style_data = data['median_ret'][[u'债券型', u'多空仓型', u'宏观策略', u'市场中性', u'管理期货', u'股票型', u'货币型']]
    style_data.dropna(inplace=True)

    def error_function(*args):
        data = args[1]
        orig = copy.deepcopy(data[:, 7])
        for i in range(7):
            orig -= args[0][i] * data[:, i]

        res = sum(orig * orig)
        return math.sqrt(res)

    def equal_condition(*args):
        return sum(args[0]) - 1.0

    def f_ieq_condition(*args):
        res = []
        for i in range(7):
            res.append(args[0][i])
            res.append(1.0 - args[0][i])
        return res

    all_res = []
    all_index = []

    fund_data.index = map(lambda x: dt.datetime(x.year, x.month, 1), fund_data.index)

    for name in fund_data.columns:
        one_fund_data = fund_data[name]
        style_data[name] = one_fund_data * 100.
        data = style_data.dropna()
        del style_data[name]
        if len(data) >= len(style_data.columns):
            start_date = data.index[0]
            end_date = data.index[-1]
            data = (data - data.mean()) / data.std()
            data = data.values

            print("{0} style analysis with {1} data observations.".format(name, len(data)))

            res = opt.fmin_slsqp(error_function,
                                 [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                                 eqcons=(equal_condition,),
                                 f_ieqcons=f_ieq_condition,
                                 args=(data,),
                                 iprint=-1)
            all_res.append([start_date, end_date] + list(res))
        elif not data.empty:
            start_date = data.index[0]
            end_date = data.index[-1]
            all_res.append([start_date, end_date] + [np.nan] * len(style_data.columns))
        else:
            all_res.append([dt.datetime(1900, 1, 1), dt.datetime(1900, 1, 1)] + [np.nan] * len(style_data.columns))
        all_index.append(name)

    cols = [u'参考起始日', u'参考结束日'] + list(style_data.columns.values)
    return pd.DataFrame(all_res, index=all_index, columns=cols)


def aggregate_nav(instruments,
                  navTable,
                  startDate,
                  endDate,
                  forceUpdate):
    returns_data = perf_combine(instruments=instruments,
                                navTable=navTable,
                                startDate=startDate,
                                endDate=endDate,
                                forceUpdate=forceUpdate)
    returns_data.dropna(inplace=True)
    nav_data = np.exp(returns_data.cumsum())
    return nav_data


@enableCache
@cleanColsForUnicode
def GetHedgePortfolioPerf(instruments=None,
                          weights=None,
                          navTable=pd.DataFrame(),
                          startDate='2012-01-01',
                          endDate='2015-01-01',
                          forceUpdate=True):
    nav_data = aggregate_nav(instruments, navTable, startDate, endDate, forceUpdate)
    num_instruments = len(nav_data.columns)

    if weights and num_instruments != len(weights):
        raise ValueError("number of valid instruments ({0}) is not equal to number of weights ({1}."
                         .format(num_instruments, len(weights)))

    if not weights:
        weights = {col: 1.0 / num_instruments for col in nav_data.columns}

    for col in nav_data.columns:
        nav_data[col] = nav_data[col] * weights[col]
    port_nav = np.sum(nav_data, axis=1) / sum(weights.values())
    return pd.DataFrame(port_nav, columns=['portfolio'])


def GetHedgeFundOptimizedPortfolio(instruments,
                          startDate='2012-01-01',
                          endDate='2016-03-23',
                          target='sharp'):
    return_data = perf_combine(instruments, navTable=pd.DataFrame(), startDate=startDate, endDate=endDate)
    return_data.dropna(inplace=True)
    nav_data = np.exp(return_data.cumsum())
    guess = [0.1 / len(instruments)] * len(instruments)
    out, fx, its, imode, smode = portfolio_optimization(guess, nav_data, target.upper())
    return out, fx, its, imode, smode


if __name__ == '__main__':
    nav_table = pd.read_excel('../notebooks/XT1515811.xlsx', index_col=0)
    print(GetHedgeFundStyleAnalysis(navTable=nav_table, startDate=nav_table.index[0].strftime('%Y-%m-%d'), endDate=nav_table.index[-1].strftime('%Y-%m-%d')))
