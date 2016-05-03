# -*- coding: utf-8 -*-
u"""
Created on 2015-12-16

@author: cheng.li, weijun.shen, yuchen.lai
"""

from __future__ import division
import datetime as dt
import pandas as pd
from PyFin.api import isBizDay
from DataAPI.Utilities import createEngine
from DataAPI.Utilities import list_to_str
from DataAPI.Utilities import NAMES_SETTINGS
from DataAPI.Utilities import field_names_mapping
from DataAPI.Utilities import _generateSecurityID
from DataAPI.Utilities import ASSET_TYPE
from DataAPI.SqlExpressions import Condition


def _extractCodeInformation(instrumentDescList):
    if isinstance(instrumentDescList, str):
        return [instrumentDescList.upper().replace('*', '%')]
        # Switch to uppercase, and replace * with %
    else:
        return [instrument.upper().replace('*', '%') for instrument in instrumentDescList]


def _dbConfiguration(instrumentDescList, field):
    if instrumentDescList != None:
        instrumentDescList = _extractCodeInformation(instrumentDescList)

    if field != '*':
        if isinstance(field, str):
            field = [field]
        if 'instrumentID' not in field:
            field.append('instrumentID')

    names_mapping = NAMES_SETTINGS['future_info']

    field = list_to_str(field, sep=u'', default_names=names_mapping)

    return instrumentDescList, field


def _createInstrumetsyntax(instrumentDesc):
    if '%' not in instrumentDesc:
        return "S_INFO_CODE = '" + instrumentDesc + "'"
    else:
        return "S_INFO_CODE LIKE '" + instrumentDesc + "'"


def _createSqlQuery(instrumentDescList, field, refdate=None):

    if not refdate:
        if instrumentDescList:
            return ["select {0:s} from CFUTURESDESCRIPTION where {1:s}" \
                        .format(field, _createInstrumetsyntax(s)) for s in instrumentDescList]
        else:
            return ["select {0:s} from datacenter_futures.dbo.INSTRUMENT_INFO as A" \
                        .format(field)]
    else:
        refdate = refdate.replace('-', '')
        if instrumentDescList:
            return ["select {0:s} from CFUTURESDESCRIPTION as B " \
                    "where {1:s} and B.S_INFO_LISTDATE <= {2:s} and " \
                    "B.S_INFO_DELISTDATE >= {2:s}" \
                        .format(field, _createInstrumetsyntax(s), refdate) for s in instrumentDescList]
        else:
            return ["select {0:s} from CFUTURESDESCRIPTION as B " \
                    "where B.S_INFO_LISTDATE <= {1:s} and " \
                    "B.S_INFO_DELISTDATE >= {1:s}" \
                        .format(field, refdate)]


def _getBucketSymbolsData(instrumentDescList, field, refdate=None):
    sqls = _createSqlQuery(instrumentDescList, field, refdate)
    engine = createEngine('WindDB')
    res = []
    for sql in sqls:
        res.append(pd.read_sql(sql, engine))
    data = pd.concat(res)
    return data


def getFutureInstrumentInfo(instrumentDescList=None, field='*', refdate=None):

    if refdate == None:
        instrumentDescList, field = _dbConfiguration(instrumentDescList, field)
        data = _getBucketSymbolsData(instrumentDescList, field)
        return data
    else:
        if not isBizDay('China.SSE', dt.datetime.strptime(refdate, '%Y-%m-%d')):
            return pd.DataFrame()
        else:
            instrumentDescList, field = _dbConfiguration(instrumentDescList, field)
            data = _getBucketSymbolsData(instrumentDescList, field, refdate)
            return data

# ===========================================
# 股票信息
# ===========================================


def getEquityInstrumentInfo(instruments=None, boardName=None, field='*', refDate=None):

    names_mapping = NAMES_SETTINGS['equity_info']

    engine = createEngine('datacenter_eqy')
    field_str = list_to_str(field, sep=u"", default_names=names_mapping)
    sql = u"""select {fields} from ASHAREDESCRIPTION
        """.format(fields=field_str)

    instruments_str = list_to_str(instruments, limit_size=6)
    ins_condition = None
    if instruments_str:
        ins_condition = Condition(names_mapping[u'instrumentID'], instruments_str, u"in")

    board_str = list_to_str(boardName)
    board_condition = None
    if board_str:
        board_condition = Condition(names_mapping[u'listBoardName'], board_str, u"in")

    and_statement = None
    if refDate:
        refDate = refDate.replace(u"-", u"")
        date_str = u"'" + refDate + u"'"
        lower_condition = Condition(names_mapping[u'listDate'], date_str, u'<=')
        upper_condition = Condition(names_mapping[u'delistDate'], date_str, u'>')
        null_condition = Condition(names_mapping[u'delistDate'], u"NULL", u'is')

        and_statement = lower_condition & (upper_condition | null_condition)

    if ins_condition:
        whole_conditon = ins_condition & board_condition & and_statement
    elif board_condition:
        whole_conditon = board_condition & and_statement
    else:
        whole_conditon = and_statement

    if whole_conditon:
        sql += u" where " + whole_conditon.__str__()
    data = pd.read_sql(sql.encode('utf-8'), engine)

    return data

# ===========================================
# 指数成分信息
# ===========================================


def getIndexConstitutionInfo(indexID, refDate=None, field='*'):
    engine = createEngine('WindDB')
    names_mapping = NAMES_SETTINGS['index_members']
    names = field_names_mapping(field, names_mapping)
    raw_names, alias = zip(*names)

    sql = u"select * from AINDEXMEMBERS"

    index_str = list_to_str(indexID, limit_size=6, sep=u"'", suffix=u'%')
    ins_condition = Condition(names_mapping[u'windCode'], index_str, u"like")

    if not refDate:
        current_date = dt.datetime.today()
        refDate = current_date.strftime("%Y-%m-%d")

    refDate = refDate.replace(u"-", u"")
    date_str = u"'" + refDate + u"'"
    lower_condition = Condition(names_mapping[u'inDate'], date_str, u'<=')
    upper_condition = Condition(names_mapping[u'outDate'], date_str, u'>')
    null_condition = Condition(names_mapping[u'outDate'], u"NULL", u'is')

    and_statement = lower_condition & (upper_condition | null_condition)

    whole_conditon = ins_condition & and_statement
    sql += u" where " + whole_conditon.__str__()
    data = pd.read_sql(sql.encode('utf-8'), engine)
    data['instrumentID'] = data[names_mapping[u'windCode']].apply(lambda x: x[:6])
    data['conInstrumentID'] = data[names_mapping[u'conWindCode']].apply(lambda x: x[:6])
    data['conSecurityID'] = _generateSecurityID(data['conInstrumentID'], ASSET_TYPE.EQUITY)
    data = data[list(raw_names)]
    data.rename(columns=dict(names), inplace=True)
    return data
