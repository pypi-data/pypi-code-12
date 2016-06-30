'''
@license: GNU Lesser General Public License v3.0 (see LICENSE)
'''
from __future__ import unicode_literals
from __future__ import absolute_import

from .transaction import Transaction


#: conversion table CSB - Homebank for pay modes
PAYMODES = {'01': '2',
            '02': '2',
            '04': '3',
            '12': '5'}


def convertFromCsb(csb):
    '''
    Convert a CSB43 file into a HomeBank CSV file

    :param csb: a CSB43 file
    :type csb: :class:`csb43.csb43.File`

    :rtype: :class:`list` of :class:`Transaction`

    >>> # Homebank
    >>> from csb43 import csb_43, homebank
    >>> #
    >>> csbFile = csb_43.File(open("movimientos.csb"), strict=False)
    >>> #
    >>> # print to stdout
    >>> for line in homebank.convertFromCsb(csbFile):
    ...    print line
    ...
    '''

    dec = csb.str_decode

    for ac in csb.accounts:

        hbTrans = []

        for t in ac.transactions:
            record = Transaction()
            record.date = t.valueDate
            record.mode = PAYMODES.get(dec(t.sharedItem), '')
            record.info = dec(t.ownItem)
            record.payee = dec(t.reference1).rstrip(' ')

            info = [
                "%s: %s" % (dec(x.item1).rstrip(' '), dec(x.item2).rstrip(' '))
                for x in t.optionalItems
            ]
            record.description = "/".join(info)
            record.amount = "%1.2f" % t.amount

            hbTrans.append(record)

        return hbTrans
