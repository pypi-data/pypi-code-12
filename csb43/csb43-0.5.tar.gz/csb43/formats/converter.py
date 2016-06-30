# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from ..i18n import tr as _
from ..utils import messages as msg
import yaml
import json
from .. import utils
from ..utils.compat import m3_unicode

import tablib


_ABSTRACT_HEADER = (msg.T_BANK_CODE,
                    msg.T_BRANCH_CODE,
                    msg.T_ACCOUNT_KEY,
                    msg.T_ACCOUNT_NUMBER,
                    msg.T_INFORMATION_MODE,
                    msg.T_SHORT_NAME,
                    msg.T_CURRENCY,
                    msg.T_INITIAL_DATE,
                    msg.T_FINAL_DATE,
                    msg.T_INITIAL_BALANCE,
                    msg.T_FINAL_BALANCE,
                    msg.T_INCOME,
                    msg.T_EXPENSES,
                    msg.T_INCOME_ENTRIES,
                    msg.T_EXPENSES_ENTRIES)

_TRANSACTION_HEADER = (msg.T_BRANCH_CODE,
                       msg.T_DOCUMENT_NUMBER,
                       msg.T_SHARED_ITEM,
                       msg.T_OWN_ITEM,
                       msg.T_ITEM_1,
                       msg.T_ITEM_2,
                       msg.T_REFERENCE_1,
                       msg.T_REFERENCE_2,
                       msg.T_TRANSACTION_DATE,
                       msg.T_VALUE_DATE,
                       msg.T_AMOUNT,
                       msg.T_ORIGINAL_CURRENCY,
                       msg.T_ORIGINAL_AMOUNT)


def _abstractRow(ac):
    dec = ac.str_decode
    return (dec(ac.bankCode),
            dec(ac.branchCode),
            dec(ac.get_account_key()),
            dec(ac.accountNumber),
            dec(ac.informationMode),
            dec(ac.shortName),
            ac.currency.letter,
            m3_unicode(ac.initialDate),
            m3_unicode(ac.finalDate),
            ac.initialBalance,
            ac.abstract.balance,
            ac.abstract.income,
            ac.abstract.expense,
            ac.abstract.incomeEntries,
            ac.abstract.expenseEntries)


def _transactionRow(t):
    dec = t.str_decode

    name = ", ".join(
        [dec(x.item1).rstrip(' ') for x in t.optionalItems])

    extdname = ", ".join(
        [dec(x.item2).rstrip(' ') for x in t.optionalItems])

    if t.exchange:
        o_currency = t.exchange.sourceCurrency.letter
        o_amount = t.exchange.amount
    else:
        o_currency = None
        o_amount = None

    return (dec(t.branchCode),
            t.documentNumber,
            dec(t.sharedItem),
            dec(t.ownItem),
            name,
            extdname,
            dec(t.reference1),
            dec(t.reference2),
            m3_unicode(t.transactionDate.date()),
            m3_unicode(t.valueDate.date()),
            t.amount,
            o_currency or '',
            o_amount or '')

#: formats supported by :mod:`tablib`
TABLIB_FORMATS = [f.__name__.rsplit('.', 1)[1].lstrip('_')
                  for f in tablib.formats.available]

#: dictionary formats
DICT_FORMATS = ['json', 'yaml']

#: available formats
FORMATS = list(set(TABLIB_FORMATS + DICT_FORMATS))


def convertFromCsb(csb, expectedFormat):
    '''
    Convert a File file into an :mod:`tablib` data object or a \
    dictionary-like object

    :param csb: a csb file
    :type  csb: :class:`csb43.csb43.File`

    :rtype: :class:`tablib.Databook`, :class:`tablib.Dataset` or a object \
    with an attribute named as `expectedFormat`
    '''

    if expectedFormat in DICT_FORMATS:
        return convertFromCsb2Dict(csb, expectedFormat)
    else:
        return convertFromCsb2Tabular(csb, expectedFormat)


class _TablibSurrogate(object):

    def __init__(self, string, expectedFormat):
        setattr(self, expectedFormat, string)


def convertFromCsb2Dict(csb, expectedFormat='json'):
    '''
    Convert from `CSB43` to a dictionary format

    :param csb: a csb file
    :type  csb: :class:`csb43.csb43.File`

    :rtype: a object with an attribute named as `expectedFormat`

    :raises: :class:`csb43.utils.Csb43Exception` when the format is unknown \
    or unsupported

    >>> from csb43.csb43 import File
    >>> import csb43.formats as formats
    >>> f = File()
    >>> o = formats.convertFromCsb2Dict(f, 'yaml')
    >>> print o.yaml
    cuentas: []

    >>> o = formats.convertFromCsb2Dict(f, 'json')
    >>> print o.json
    {"cuentas": []}

    '''

    csb_dict = csb.as_dict()

    if expectedFormat == 'yaml':
        return _TablibSurrogate(yaml.safe_dump(csb_dict), expectedFormat)
    elif expectedFormat == 'json':
        return _TablibSurrogate(json.dumps(csb_dict,
                                           indent=1,
                                           sort_keys=True), expectedFormat)
    else:
        utils.raiseCsb43Exception(
            _("unexpected format %s") % expectedFormat, True)


def convertFromCsb2Tabular(csb, expectedFormat='ods'):
    '''
    Convert a File file into an :mod:`tablib` data object

    :param csb: a csb file
    :type  csb: :class:`csb43.csb43.File`

    :rtype: :class:`tablib.Databook` or :class:`tablib.Dataset`

    '''
    datasets = []

    accountsAbstract = tablib.Dataset()

    accountsAbstract.title = _("Accounts")
    accountsAbstract.headers = _ABSTRACT_HEADER

    datasets.append(accountsAbstract)

    for ac in csb.accounts:

        accountId = (
            ac.bankCode,
            ac.branchCode,
            ac.get_account_key(),
            ac.accountNumber
        )

        accountsAbstract.append(_abstractRow(ac))

        tList = tablib.Dataset()
        tList.title = '-'.join(ac.str_decode(x) for x in accountId)

        tList.headers = _TRANSACTION_HEADER

        for t in ac.transactions:
            tList.append(_transactionRow(t))

        datasets.append(tList)

    book = tablib.Databook(datasets)

    if hasattr(book, expectedFormat):
        return book

    dataset = tablib.Dataset()

    dataset.title = _("Transactions")
    dataset.headers = _ABSTRACT_HEADER + _TRANSACTION_HEADER

    for ac in csb.accounts:

        accountAbstract = _abstractRow(ac)

        for t in ac.transactions:
            dataset.append(accountAbstract + _transactionRow(t))

    return dataset
