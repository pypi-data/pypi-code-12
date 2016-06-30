'''
@license: GNU Lesser General Public License v3.0 (see LICENSE)
'''
from __future__ import absolute_import
from __future__ import unicode_literals

from ..utils.compat import m3_unicode
from .ofx_file import (BankAccount,
                       File,
                       Response,
                       Balance,
                       TransactionList,
                       Transaction)

#: conversion table OFX - Homebank for pay modes
PAYMODES = {'01': 10,
            '02': 0,
            '03': 5,
            '04': 9,
            '05': 3,
            # '06':
            '07': 15,
            '08': 3,
            # '09':
            '10': 10,
            '11': 7,
            '12': 8,
            # '13':
            # '14':
            '15': 9,
            # '16':
            '17': 2,
            # '98':
            '99': 16}

DEFAULT_NAME = "-"
DEFAULT_MEMO = "-"


def convertFromCsb(csb, sgml=False):
    '''
    Convert a File file into an OFX file

    :param csb: a CSB43 file
    :type csb: :class:`csb43.csb43.File`

    :rtype: :class:`csb43.ofx.File`

    >>> # OFX
    >>> from csb43 import csb_43, ofx
    >>> #
    >>> csbFile = csb_43.File(open("movimientos.csb"), strict=False)
    >>> #
    >>> # print to stdout
    >>> print ofx.convertFromCsb(csbFile)

    '''
    ofxFile = File(sgml=sgml)

    dec = csb.str_decode

    for ac in csb.accounts:

        r = Response(sgml=sgml)
        # currency
        r.set_currency(ac.currency)
        # account
        bAcc = BankAccount(sgml=sgml)
        bAcc.set_bank(dec(ac.bankCode))
        bAcc.set_branch(dec(ac.branchCode))
        bAcc.set_id(dec(ac.accountNumber))
        bAcc.set_key(dec(ac.get_account_key()))

        r.set_bank_account_from(bAcc)

        # balance (ledger)
        bal = Balance(sgml=sgml)

        bal.set_amount(ac.abstract.balance)
        bal.set_date(ac.initialDate)

        r.set_ledger_balance(bal)

        # balance (available)
        # r.set_available_balance(bal)

        # transactions
        tList = TransactionList(sgml=sgml)
        tList.set_date_start(ac.initialDate)
        tList.set_date_end(ac.finalDate)

        for idx, t in enumerate(ac.transactions):
            trans = Transaction(sgml=sgml)

            trans.set_type(
                Transaction.TYPE[PAYMODES.get(dec(t.sharedItem), -1)])
            trans.set_date_posted(t.transactionDate)
            trans.set_date_available(t.valueDate)
            # composing a unique transaction id
            t_id = "-".join((dec(ac.bankCode),
                            dec(ac.branchCode),
                            dec(ac.get_account_key()),
                            dec(ac.accountNumber),
                            t.transactionDate.strftime("%Y%m%d"),
                            m3_unicode(idx)))
            trans.set_transaction_id(t_id)
            trans.set_ref_num(dec(t.reference2))
            trans.set_payeeid(dec(t.reference1))
            # trans.set_name(t.commonItem)
            # trans.set_extended_name(t.particularItem)
            name = ", ".join(
                [dec(x.item1).rstrip(' ') for x in t.optionalItems])
            if not name:
                name = DEFAULT_NAME
            trans.set_name(name)
            extdname = ", ".join(
                [dec(x.item2).rstrip(' ') for x in t.optionalItems])
            if not extdname:
                extdname = DEFAULT_MEMO
            trans.set_memo(extdname)

            trans.set_amount(t.amount)

            if t.exchange is not None:
                trans.set_origin_currency(t.exchange.sourceCurrency)

            tList.add_transaction(trans)

        r.set_transaction_list(tList)

        ofxFile.add_response(r)

    return ofxFile
