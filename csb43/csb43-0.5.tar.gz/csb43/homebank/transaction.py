# -*- coding: utf-8 -*-
'''
@license: GNU Lesser General Public License v3.0 (see LICENSE)
'''
from __future__ import absolute_import
from __future__ import unicode_literals

import datetime as date
import datetime

from ..utils import check_strict, raiseCsb43Exception
from ..i18n import tr as _

'''
0. tarjeta de credito
1. cheque
2. efectivo
3. transferencia
4. transferencia interna
5. tarjeta de debito
6. orden de posicion
7. pago electronico
8. deposito
9. honorarios FI
'''


class Transaction(object):
    '''
    Hombebank CSV transaction

    - Creating a record::

        >>> from csb43.homebank import Transaction
        >>> t = Transaction()
        >>> t.amount = 12.45
        >>> from datetime import datetime
        >>> t.date = datetime.now()
        >>> print t
        19-03-13;;;;;12.45;

    - Parsing a record::

        >>> t = Transaction("19-03-13;;;;;12.45;")
        >>> t.amount
        12.45
        >>> t.date
        datetime.datetime(2013, 3, 19, 0, 0)


    '''

    def __init__(self, record=None):
        '''
        :param record: a Hombeank csv record
        :type record: :class:`str`

        :raises: :class:`csb43.utils.Csb43Exception`
        '''
        self.__date = None
        self.__mode = None
        self.__info = None
        self.__payee = None
        self.__description = None
        self.__amount = None
        self.__category = None

        if record is not None:
            fields = record.split(";")
            if len(fields) < 6:
                raiseCsb43Exception(_("bad format, 6 fields expected, but"
                                    "%d found") % len(fields), True)

            self._set_date_str(fields[0])
            self.mode = fields[1]
            self.info = fields[2]
            self.payee = fields[3]
            self.description = fields[4]
            self.amount = fields[5]
            if len(fields) >= 7:
                self.category = fields[6]
            else:
                self.category = None

    @property
    def date(self):
        "date of transaction (:class:`datetime.datetime`)"
        return self.__date

    @date.setter
    def date(self, value):
        #import datetime
        if not isinstance(value, datetime.date):
            raiseCsb43Exception(_("datetime.date expected"), strict=True)
        self.__date = value

    @property
    def mode(self):
        "mode of transaction"
        return self.__mode

    @mode.setter
    def mode(self, value):
        self.__mode = int(value) if value != '' else None

    @property
    def info(self):
        "transaction's info"
        return self.__info

    @info.setter
    def info(self, value):
        self.__info = value

    @property
    def payee(self):
        "payee of the transaction"
        return self.__payee

    @payee.setter
    def payee(self, value):
        self.__payee = value

    @property
    def description(self):
        "description of the transaction"
        return self.__description

    @description.setter
    def description(self, value):
        self.__description = value

    @property
    def amount(self):
        "amount of the transaction"
        return self.__amount

    @amount.setter
    def amount(self, value):
        self.__amount = float(value)

    @property
    def category(self):
        "transaction category, according to HomeBank"
        return self.__category

    @category.setter
    def category(self, value):
        self.__category = value

    @check_strict(r"^(\d{2}\-\d{2}\-\d{2})?$")
    def _set_date_str(self, value, strict=True):
        if value == '':
            self.__date = None
        else:
            self.__date = date.datetime.strptime(value, "%d-%m-%y")

    def __str__(self):
        '''
        :rtype: :class:`str` representation of this record as a row of a \
        Homebank CSV file
        '''
        def f(x):
            return '' if x is None else str(x)

        if self.__date is not None:
            mdate = self.__date.strftime("%d-%m-%y")
        else:
            mdate = None

        l = (f(x) for x in [mdate,
                            self.mode,
                            self.info,
                            self.payee,
                            self.description,
                            "%.2f" % self.amount,
                            self.category])

        return ";".join(l)
