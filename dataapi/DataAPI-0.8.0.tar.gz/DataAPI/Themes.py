# -*- coding: utf-8 -*-
u"""
Created on 2016-1-7

@author: cheng.li, weijun.shen, yuchen.lai
"""

import sys
import pandas as pd
from PyFin.DateUtilities import Date
from DataAPI.Utilities import NAMES_SETTINGS
from DataAPI.Utilities import field_names_mapping
from DataAPI.Utilities import enableCache
from DataAPI.Utilities import cleanColsForUnicode
from DataAPI.Utilities import Settings


@enableCache
@cleanColsForUnicode
def GetThemeInfo(themeName=None,
                 themeID=None,
                 field='*',
                 forceUpdate=True):
    u"""

    获取相关的主题列表

    :param themeName: 关注的主题名，支持模糊查找，默认查找全部主题
    :param themeID: 关注的主题id，为整数，与themeName二选一输入
    :param field: 需要获取的字段类型，例如：['newsNumPercent']，不填的话，默认获取所有字段；
                  可用的field包括：[themeID, themeName, isActive, insertTime, updateTime]
    :param forceUpdate:
    :return:
    """

    names_mapping = NAMES_SETTINGS['theme_info']
    names = field_names_mapping(field, names_mapping)
    raw_names, alias = zip(*names)

    if not themeName:
        themeName = ''

    if not themeID:
        themeID = ''

    subject = Settings.subject()

    if sys.version_info < (3, 0, 0) and isinstance(themeName, unicode):
        themeName = themeName.encode('utf8')

    theme_info = subject.ThemesContent(themeName=themeName, themeID=themeID)

    if theme_info.empty:
        return theme_info

    theme_info = theme_info[list(raw_names)]
    theme_info.rename(columns=dict(names), inplace=True)
    return theme_info


@enableCache
@cleanColsForUnicode
def GetThemeHotness(themeName,
                    startDate,
                    endDate,
                    field='*',
                    forceUpdate=True):
    u"""

    获取主题热度时间序列

    :param themeName: 主题名称，例如：u'金融'
    :param startDate: 起始日，格式：YYYY-MM-DD
    :param endDate: 结束日，格式：YYYY-MM-DD
    :param field: 需要获取的字段类型，例如：['newsNumPercent']，不填的话，默认获取所有字段；
                  可用的field包括：[themeID, themeName, date, newsNum, newsNumPercent]
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :return: pandas.DataFrame
    """
    names_mapping = NAMES_SETTINGS['theme_hotness']
    names = field_names_mapping(field, names_mapping)
    raw_names, alias = zip(*names)

    startDate = startDate.replace('-', '')
    endDate = endDate.replace('-', '')

    subject = Settings.subject()

    if sys.version_info < (3, 0, 0) and isinstance(themeName, unicode):
        themeName = themeName.encode('utf8')

    theme_heat = subject.ThemesHeat(themeName=themeName,
                                    beginDate=startDate,
                                    endDate=endDate)

    if theme_heat.empty:
        return theme_heat

    theme_heat = theme_heat[list(raw_names)]

    theme_heat.rename(columns=dict(names), inplace=True)
    return theme_heat


@enableCache
@cleanColsForUnicode
def GetStocksByTheme(themeName,
                     refDate=None,
                     field='*',
                     forceUpdate=True):
    u"""

    获取指定主题相关的股票

    :param themeName: 主题名称，例如：u'金融'
    :param refDate: 参考日，格式：YYYY-MM-DD
    :param field: 需要获取的字段类型，例如：['instrumentID']，不填的话，默认获取所有字段；
                  可用的field包括：[themeID, themeName, instrumentID, cnName,
                  exchangeName, score]
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :return: pandas.DataFrame
    """
    names_mapping = NAMES_SETTINGS['stocks_by_theme']
    names = field_names_mapping(field, names_mapping, forced_names=['instrumentID'])
    raw_names, alias = zip(*names)

    if not refDate:
        refDate = Date.todaysDate().toDateTime().strftime("%Y%m%d")
    else:
        refDate = refDate.replace('-', '')

    subject = Settings.subject()

    if sys.version_info < (3, 0, 0) and isinstance(themeName, unicode):
        themeName = themeName.encode('utf8')

    tickers = subject.TickersByThemes(themeName=themeName,
                                      beginDate=refDate,
                                      endDate=refDate)

    if tickers.empty:
        return tickers

    tickers = tickers[list(raw_names)]

    tickers.rename(columns=dict(names), inplace=True)
    tickers['instrumentID'] = tickers['instrumentID'].apply(lambda x: x[:6])
    return tickers


@enableCache
@cleanColsForUnicode
def GetActiveThemesRelatedStocks(refDate=None,
                                 windows=None,
                                 topThemes=20,
                                 topStocks=20,
                                 field='*',
                                 forceUpdate=True):
    u"""

    获取指定数量的热门主题高相关度的股票

    :param refDate: 参考日，格式：YYYY-MM-DD。默认为None，取当前日期
    :param windows: 参考周期，可填写正数表示日；或者字符串形式的时间长度，例如：1m。默认为None，只取1日
    :param topThemes: 选取排名靠前多少的主题，默认值为20
    :param topStocks: 在同主题下选取排名靠前多少的股票，默认值为20
    :param field: 需要获取的字段类型，例如：['instrumentID']，不填的话，默认获取所有字段；
                  可用的field包括：[themeID, themeName, instrumentID, cnName,
                  date, themeHotness，score]
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :return: pandas.DataFrame
    """
    names_mapping = NAMES_SETTINGS['active_theme_related_stocks']
    names = field_names_mapping(field, names_mapping)
    raw_names, alias = zip(*names)

    if not refDate:
        end_date = Date.todaysDate()
    else:
        end_date = Date.strptime(refDate, '%Y-%m-%d')

    if windows:
        start_date = end_date - windows + 1
    else:
        start_date = end_date

    theme_list = Settings.global_theme_list.themeID.values.astype(str)

    subject = Settings.subject()
    output = []

    theme_length = len(theme_list)
    start_date_str = start_date.toDateTime().strftime('%Y%m%d')
    end_date_str = end_date.toDateTime().strftime('%Y%m%d')

    start = 0
    chunk = 10
    res = []
    while start < theme_length:
        sub_theme_list = ','.join(theme_list[start:start + chunk])
        theme_heat = subject.ThemesHeat(themeID=sub_theme_list, beginDate=start_date_str, endDate=end_date_str)
        start += chunk
        res.append(theme_heat)

    total_table = pd.concat(res)
    if total_table.empty:
        return total_table
    total_table = total_table.groupby('themeName').mean().sort_values('newsNum', ascending=False)
    hot_themes_id, hot_themes_name, hot_themes_scale = \
        total_table['themeID'], total_table.index, total_table['newsNum']

    count_theme_number = 0
    for theme_id, theme_name, theme_hot in zip(hot_themes_id, hot_themes_name, hot_themes_scale):
        related_stocks = subject.TickersByThemes(themeID=theme_id, beginDate=end_date_str, endDate=end_date_str)
        if related_stocks.empty:
            continue
        else:
            count_theme_number += 1
            related_stocks = related_stocks.sort_values('returnScore', ascending=False)[:topStocks]

        related_stocks['date'] = end_date.toDateTime()
        related_stocks['themeHotness'] = theme_hot
        related_stocks['score'] = related_stocks['returnScore']

        if sys.version_info < (3, 0, 0):
            related_stocks['themeName'] = related_stocks['themeName'].str.decode('utf8')
            related_stocks['secShortName'] = related_stocks['secShortName'].str.decode('utf8')
        output.append(related_stocks[['secID', 'secShortName', 'themeID', 'themeName',
                                      'date', 'themeHotness', 'score']])

        if count_theme_number >= topThemes:
            break

    summary = pd.concat(output)
    summary.reset_index(drop=True, inplace=True)
    summary = summary[list(raw_names)]
    summary.rename(columns=dict(names), inplace=True)
    summary['instrumentID'] = summary['instrumentID'].apply(lambda x: x[:6])
    return summary
