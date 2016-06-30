# -*- coding: utf-8 -*-
'''
.. note::

    license: GNU Lesser General Public License v3.0 (see LICENSE)
'''

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from ..utils.compat import (m3_unicode,
                            m3_bytes,
                            m3_next,
                            m3_is_string)
from ..utils import (check_strict,
                     raiseCsb43Exception,
                     currencyISO,
                     b_left_pad,
                     b_right_pad)
from ..utils import messages as msg
from ..i18n import tr as _
from .transaction import Transaction
from .record import (RecordSequence,
                     NextMixin)

import re


_CUR_NUM = re.compile(r'^\d{3}$')
_CUR_LET = re.compile(r'^[a-zA-Z]{3}$')


class Account(RecordSequence):
    '''
    A Csb43 account / (es) Cuenta

    - Create an :class:`Account` object from a `CSB43` string record::

        >>> from csb43.csb43 import Account
        >>> a = Account(record)

    - From an empty object to a `CSB43` string record::

        >>> a = Account()
        >>> str(a)
        '11                  00000000000000000000000000000\
0                              '
    '''

    def __init__(self, record=None,
                 **record_settings):
        '''
        :param record: csb record
        :type record: :class:`basestring` or `None`

        :param \*\*record_settings: see :class:`csb43.csb43.RecordSequence`

        :raises: :class:`csb43.utils.Csb43Exception`

        '''
        super(Account, self).__init__(**record_settings)
        self.__transactions = []
        self.__closing = None

        self.__bankCode = None
        self.__branchCode = None
        self.__accountNumber = None
        self.__initialBalance = None
        self.__debitOrCredit = None
        self.__initialDate = None
        self.__finalDate = None
        self.__shortName = None
        self.__currencyCode = None
        self.__padding = None
        self.__informationMode = None

        if record is not None:
            chk_args = self._get_check_args()

            record = self.str_encode(record)
            if not Account.is_valid(record):
                raiseCsb43Exception(msg.BAD_RECORD(record), **chk_args)

            # base 1
            # clave de banco: 3-6, N
            self._set_bank_code(record[2:6], **chk_args)
            # clave de oficina: 7-10 N
            self._set_branch_code(record[6:10], **chk_args)
            # num. de cuenta: 11-20
            self._set_account_number(record[10:20], **chk_args)
            # fecha inicial: 21-26
            self._set_initial_date(record[20:26], **chk_args)
            # fecha final: 27-32
            self._set_final_date(record[26:32], **chk_args)
            # debe o haber: 33-33
            self._set_expense_or_income(record[32:33], **chk_args)
            # saldo inicial: 34-47
            self._set_initial_balance(record[33:47], **chk_args)
            # clave divisa: 48-50
            self._set_currency_code(record[47:50], **chk_args)
            # modalidad de informacion: 51-51
            self._set_information_mode(record[50:51], **chk_args)
            # nombre abreviado
            self._set_short_name(record[51:77], **chk_args)
            # padding
            self._set_padding(record[77:80], **chk_args)

    @staticmethod
    def is_valid(record):
        return m3_is_string(record)\
            and (77 <= len(record) <= 80) and (record[0:2] == b'11')

    # account number
    #
    # repr: bytes
    # user in: text
    # user out: bytes

    @check_strict(br'^[ \d]{10}$')
    def _set_account_number(self, value, **chk_args):
        self.__accountNumber = value

    @property
    def accountNumber(self):
        """account number / (es) numero de cuenta
:rtype: :class:`str`

>>> a.accountNumber = '0000000000'
>>> a.accountNumber
b'0000000000'"""
        return self.__accountNumber

    @accountNumber.setter
    def accountNumber(self, value):
        field = self._enc_left_pad(value, n=10, fill=b"0")
        self._set_account_number(field)

    # bank code
    #
    # repr: bytes
    # user in: text
    # user out: text

    @check_strict(br'^\d{4}$')
    def _set_bank_code(self, value, **chk_args):
        self.__bankCode = value

    @property
    def bankCode(self):
        """bank code / (es) codigo de banco

:rtype: :class:`str`

>>> a.bankCode = '0000'
>>> a.bankCode
b'0000'"""
        return self.__bankCode

    @bankCode.setter
    def bankCode(self, value):
        field = self._enc_left_pad(value, n=4, fill=b"0")
        self._set_bank_code(field)

    # branch code
    #
    # repr: bytes
    # user in: text
    # user out: text

    @check_strict(br'^[ \d]{4}$')
    def _set_branch_code(self, value, **chk_args):
        self.__branchCode = value

    @property
    def branchCode(self):
        """branch code / (es) codigo de sucursal u oficina

:rtype: :class:`str`

>>> a.branchCode = '0000'
>>> a.branchCode
b'0000'"""
        return self.__branchCode

    @branchCode.setter
    def branchCode(self, value):
        field = self._enc_left_pad(value, n=4)
        self._set_branch_code(field)

    # currency
    #
    # repr: bytes
    # user in: text, int, pycountry
    # user out pycountry

    @check_strict(br'^[ \d]{3}$')
    def _set_currency_code(self, value, **chk_args):
        self.__currencyCode = value

    def _get_currency_code(self):
        return self.__currencyCode

    @property
    def currency(self):
        """currency object / (es) objecto de divisa

:rtype: :class:`pycountry.db.Currency`

`ISO 4217` codes can be assigned::

    >>> a.currency = 'USD'
    >>> a.currency.letter
    u'USD'
    >>> a.currency.numeric
    u'840'
    >>> a.currency = '978'
    >>> a.currency.letter
    u'EUR'"""
        if self.__currencyCode is None:
            return None
        return currencyISO(self.str_decode(self.__currencyCode))

    @currency.setter
    def currency(self, value):
        value = self._parse_currency_code(value)
        if value:
            self._set_currency_code(value)

    # information mode
    #
    #
    # repr: bytes
    # user in: text, int
    # user out: bytes

    @check_strict(br'^[ \d]$')
    def _set_information_mode(self, value, **chk_args):
        """information mode / (es) modalidad de informacion

>>> a.informationMode = 1
>>> a.informationMode
'1'
>>> a.informationMode = '2'
>>> a.informationMode
'2'"""
        self.__informationMode = value

    def _get_information_mode(self):
        return self.__informationMode

    @property
    def informationMode(self):
        if self.__informationMode is None:
            return None
        #elif self.__informationMode == b' ':
            #return None
        return self.__informationMode

    @informationMode.setter
    def informationMode(self, value):
        value = self._text2field(value)
        self._set_information_mode(value)

    # short name
    #
    # repr: bytes
    # user in: text
    # user out: bytes

    @check_strict(br'^[\x20-\xFF]{26}$')
    def _set_short_name(self, value, **chk_args):
        """
        value -- (enc: latin1)
        """

        # internal is unicode
        self.__shortName = value.rstrip(b' ')

    @property
    def shortName(self):
        """abbreviated name of the client / (es) nombre abreviado del cliente

:rtype: :class:`str`"""
        return self.__shortName

    @shortName.setter
    def shortName(self, value):
        #if value is None:
            #value = ''
        value = self.str_encode(value).ljust(26)
        self._set_short_name(value)

    # padding
    #
    # repr: bytes
    # user in: text
    # user out: bytes

    @check_strict(br'^.{3}$')
    def _set_padding(self, value, **chk_args):
        self.__padding = value.rstrip(b' ')

    @property
    def padding(self):
        """padding"""
        return self.__padding

    @padding.setter
    def padding(self, value):
        value = self.str_encode(value)
        field = b_right_pad(value, 3)
        self._set_padding(field)

    # initial balance
    # debitOrCredit -> sign
    #
    # repr: bytes, bytes
    # user in: text, number
    # user out: int

    @check_strict(br'^\d{14}$')
    def _set_initial_balance(self, value, **chk_args):
        self.__initialBalance = value

    def _get_initial_balance(self):
        return self.__initialBalance

    @property
    def initialBalance(self):
        """initial balance amount / (es) montante del balance inicial

Quantities can be assigned as numbers or strings, and they will be truncated
to adjust the decimal format set for the object::

    >>> a.initialBalance = 123
    >>> a.initialBalance
    123.0
    >>> a.initialBalance = 123.45
    >>> a.initialBalance
    123.45
    >>> a.initialBalance = '1234.56'
    >>> a.initialBalance
    1234.56
    >>> a.initialBalance = 1.2345
    >>> a.initialBalance
    1.23"""
        if self.__initialBalance is None:
            return None
        return self._format_currency(self.__initialBalance,
                                     self.__debitOrCredit)

    @initialBalance.setter
    def initialBalance(self, value):
        bal, sign = self._unformat_currency(float(value))
        field = "%014d" % bal
        self._set_initial_balance(self.str_encode(field))
        self._set_expense_or_income(self.str_encode(sign))

    # debit or credit
    ##
    def _get_expense_or_income(self):
        return self.__debitOrCredit

    @check_strict(br'^[12]$')
    def _set_expense_or_income(self, value, **chk_args):
        self.__debitOrCredit = value

    # initial date
    #
    # repr: bytes
    # user in: datetime
    # user out: datetime

    def _get_initial_date(self):
        return self.__initialDate

    @check_strict(br'^\d{6}$')
    def _set_initial_date(self, value, **chk_args):
        self.__initialDate = value

    @property
    def initialDate(self):
        """Start date of the period to which the information corresponds /
        (es) fecha de comienzo del periodo al que corresponde la informacion

:rtype: :class:`datetime.datetime`

Setting a date::

    >>> a.initialDate = datetime.datetime(year=2012,month=2,day=13).date()
    >>> a.initialDate
    datetime.datetime(2012, 2, 13, 0, 0)"""
        if self.__initialDate is None:
            return None
        return self._format_date(self.str_decode(self.__initialDate))

    @initialDate.setter
    def initialDate(self, value):
        value = self.str_encode(self._unformat_date(value))
        self._set_initial_date(value)

    # final date
    #
    # repr: bytes
    # user in: datetime
    # user out: datetime

    @check_strict(br'^\d{6}$')
    def _set_final_date(self, value, **chk_args):
        self.__finalDate = value

    def _get_final_date(self):
        return self.__finalDate

    @property
    def finalDate(self):
        """End date of the period to which the information corresponds /
        (es) fecha de fin del periodo al que corresponde la informacion

:rtype: :class:`datetime.datetime`

Setting a date::

    >>> a.finalDate = datetime.datetime(year=2012,month=2,day=13).date()
    >>> a.finalDate
    datetime.datetime(2012, 2, 13, 0, 0)"""
        if self.__finalDate is None:
            return None
        return self._format_date(self.str_decode(self.__finalDate))

    @finalDate.setter
    def finalDate(self, value):
        value = self.str_encode(self._unformat_date(value))
        self._set_final_date(value)

    # transactions
    #
    # repr: [transaction]
    #
    # user in: none
    # user out: [transaction]

    @property
    def transactions(self):
        ":class:`list` of transactions / (es) lista de movimientos"
        return self.__transactions

    def get_last_transaction(self):
        '''
        :rtype: the last added :class:`Transaction`
        '''
        return self.__transactions[-1]

    def add_transaction(self, record):
        '''
        Add a new transaction to the account

        :param record: transaction record
        :type record: :class:`Transaction` or :class:`basestring`

        :raises: :class:`csb43.utils.Csb43Exception`
        '''

        if isinstance(record, Transaction):
            record.informationMode = self.informationMode
            self.__transactions.append(record)
        else:
            self.__transactions.append(
                Transaction(
                    record,
                    informationMode=self.informationMode,
                    **self._settings()
                )
            )

    def add_item(self, record):
        '''
        Add a new additional item record to the transaction

        :param record: item record
        :type record: :class:`Item` or :class:`basestring`

        :raises: :class:`csb43.utils.Csb43Exception` when the record is \
        impossible to parse, or if the maximum number of complementary \
        items has been reached

        .. seealso::

            :func:`Transaction.add_item`
        '''
        self.get_last_transaction().add_item(record)

    def get_account_key(self):
        '''
        :rtype: :class:`int` two-digits checksum for the bank account / (es) \
        digitos de control
        '''

        def fixDigit(x):
            return 1 if x == 10 else x

        def sumprod(l1, l2):
            return sum(int(x) * y for x, y in zip(l1, l2))

        weights = (10, 9, 7, 3, 6, 1, 2, 4, 8, 5)
        c1 = weights[2:6]
        c2 = weights[6:]

        dig1 = fixDigit((sumprod(self.str_decode(self.bankCode), c1) +
                         sumprod(self.str_decode(self.branchCode), c2)) % 11)

        dig2 = fixDigit(
            sumprod(self.str_decode(self.accountNumber), weights) % 11
        )

        return self.str_encode("%d%d" % (dig1, dig2))

    def close_account(self, record=None, update=False):
        '''
        Close the current account and generate an abstract object

        :param record: csb record
        :type record: :class:`ClosingAccount`, :class:`basestring` or `None`

        :param update: update the abstract if already present
        :type record: :class:`bool`

        :raises: :class:`csb43.utils.Csb43Exception` if invalid record or \
        incongruent abstract
        '''
        chk_args = self._get_check_args()

        if (self.__closing is not None) and not update:
            raiseCsb43Exception(
                _("trying to close an already closed account"),
                **chk_args
            )

        def equal_f(a, bal):
            return abs(a - bal) < 10 ** (-self._s_decimal)

        balance = self.initialBalance or 0
        pBalance = 0
        nBalance = 0
        negRecords = 0
        posRecords = 0
        for t in self.__transactions:
            tAmount = t.amount
            balance += tAmount
            if tAmount >= 0:
                posRecords += 1
                pBalance += tAmount
            else:
                negRecords += 1
                nBalance += tAmount

        closing = None

        if m3_is_string(record):
            closing = ClosingAccount(record,
                                     **self._settings())
        elif isinstance(record, ClosingAccount):
            closing = record
        elif record is not None:
            raiseCsb43Exception(msg.INCOMPATIBLE_OBJECT(record,
                                                        "ClosingAccount",
                                                        "basestring"), True)

        if closing:
            rBalance = closing.balance
            rPBalance = closing.income
            rNBalance = -closing.expense
            rPositive = closing.incomeEntries
            rNegative = closing.expenseEntries

            if not equal_f(balance, rBalance):
                raiseCsb43Exception(
                    _("balance (%1.2f) mismatch in closing account "
                      "record (%1.2f)") % (balance, rBalance),
                    **chk_args
                )
            if not equal_f(pBalance, rPBalance):
                raiseCsb43Exception(
                    _("income amount (%1.2f) mismatch in closing "
                      "account record (%1.2f)") % (pBalance,
                                                   rPBalance),
                    **chk_args
                )
            if not equal_f(nBalance, rNBalance):
                raiseCsb43Exception(
                    _("expense amount (%1.2f) mismatch in closing "
                      "account record (%1.2f)") % (nBalance,
                                                   rNBalance),
                    **chk_args
                )
            if posRecords != rPositive:
                raiseCsb43Exception(
                    _("income entries (%d) mismatch in closing "
                      "account record (%d)") % (posRecords,
                                                rPositive),
                    **chk_args
                )
            if negRecords != rNegative:
                raiseCsb43Exception(
                    _("expense entries (%d) mismatch in closing "
                      "account record (%d)") % (negRecords,
                                                rNegative),
                    **chk_args
                )
        else:
            closing = ClosingAccount(**self._settings())
            closing.balance = balance
            closing.income = pBalance
            closing.expense = -nBalance
            closing.incomeEntries = posRecords
            closing.expenseEntries = negRecords
            if self.currency:
                closing.currency = self.currency
            if self.accountNumber:
                closing.accountNumber = self.accountNumber
            if self.bankCode:
                closing.bankCode = self.bankCode
            if self.branchCode:
                closing.branchCode = self.branchCode

        self.__closing = closing

    def is_closed(self):
        '''
        :rtype: :class:`bool` `True`  if this :class:`Account` has been \
        properly closed
        '''
        return self.__closing is not None

    @property
    def abstract(self):
        ":rtype: :class:`ClosingAccount` account abstract"
        return self.__closing

    def add_exchange(self, record, update=False):
        '''
        Add a new additional exchange record to the last added transaction

        :param record: csb exchange record or object
        :type record: :class:`Exchange` or :class:`basestring`

        :param update: update the current exchange object if it exists
        :type update: :class:`bool`

        :raises: :class:`csb43.utils.Csb43Exception`

        .. seealso::

            :func:`Transaction.add_exchange`

        '''
        self.get_last_transaction().add_exchange(record, update)

    def as_dict(self):
        '''
        :rtype: a representation of this object as a :class:`dict`. The keys \
        will be localised
        '''

        d = {
            msg.T_INITIAL_DATE: (m3_unicode(self.initialDate.date())
                                 if self.initialDate else None),
            msg.T_FINAL_DATE: (m3_unicode(self.finalDate.date())
                               if self.finalDate else None),
            msg.T_INITIAL_BALANCE: self.initialBalance,
            msg.T_CURRENCY: (m3_unicode(self.currency.letter)
                             if self.currency else None),
            msg.T_SHORT_NAME: self.str_decode(self.shortName),
            msg.T_ACCOUNT_NUMBER: self.str_decode(self.accountNumber),
            msg.T_BANK_CODE: self.str_decode(self.bankCode),
            msg.T_BRANCH_CODE: self.str_decode(self.branchCode),
            msg.T_INFORMATION_MODE: self.str_decode(self.informationMode),
        }

        if self.accountNumber:
            d[msg.T_ACCOUNT_KEY] = m3_unicode(self.get_account_key())

        if len(self.transactions) > 0:
            d[_("transactions")] = [x.as_dict() for x in self.transactions]

        if self.abstract:
            d.update(self.abstract.as_dict())

        return d

    def __main_str(self):
        #name = self.shortName or b''
        #return (b"11"
                #b"{b_code: >4}{of_code: >4}{ac_num: >10}{in_date:0>6}"
                #b"{fin_date:0>6}{e_i:0>1}{bal:0>14}{cur:0>3}{info: >1}"
                #b"{nom: <26}{padding: <3}".format(
                    #b_code=self.bankCode or b'',
                    #of_code=self.branchCode or b'',
                    #ac_num=self.accountNumber or b'',
                    #in_date=self._get_initial_date() or b'',
                    #fin_date=self._get_final_date() or b'',
                    #e_i=self._get_expense_or_income() or b'',
                    #bal=self._get_initial_balance() or b'',
                    #cur=self._get_currency_code() or b'',
                    #info=self._get_information_mode() or b'',
                    #nom=name or b'',
                    #padding=self.padding or b''
                #))

        return (b"11" +
                b_left_pad(self.bankCode or b'', 4) +
                b_left_pad(self.branchCode or b'', 4) +
                b_left_pad(self.accountNumber or b'', 10) +
                b_left_pad(self._get_initial_date() or b'', 6, b"0") +
                b_left_pad(self._get_final_date() or b'', 6, b"0") +
                b_left_pad(self._get_expense_or_income() or b'', 1, b"0") +
                b_left_pad(self._get_initial_balance() or b'', 14, b"0") +
                b_left_pad(self._get_currency_code() or b'', 3, b"0") +
                b_left_pad(self._get_information_mode() or b'', 1) +
                b_right_pad(self.shortName or b'', 26) +
                b_right_pad(self.padding or b'', 3))

    def __iter__(self):
        ''':rtype: iterator of all the `CSB43` records that this object \
        represents'''
        return _AccountIter(self, self.__main_str())

    def __bytes__(self):
        ''':rtype: representation of this object as `CSB43` records (using \
        `\\\\n` as separator)'''
        return b'\n'.join([x for x in self])


class _AccountIter(NextMixin):

    def __init__(self, ac, main_str):
        self.__output = [main_str]
        self.__output.extend(ac.transactions)
        if ac.abstract:
            self.__output.append(ac.abstract)

        self.__iter = iter(self.__output)
        self.__tran = None

    def __next__(self):

        if self.__tran:
            try:
                return m3_next(self.__tran)
            except StopIteration:
                self.__tran = None
        now = m3_next(self.__iter)

        if isinstance(now, Transaction):
            self.__tran = iter(now)
            return self.__next__()
        else:
            return m3_bytes(now)


class ClosingAccount(RecordSequence):
    '''
    An Account abstact, given by a termination record
    '''

    def __init__(self, record=None,
                 **record_settings):
        '''
        :param record: csb record
        :type record: :class:`basestring` or `None`

        :param strict: treat warnings as exceptions when `True`
        :type strict: :class:`bool`

        :param decimal: number of digits to be considered as the decimal part \
        in money
        :type decimal: :class:`int`

        :param yearFirst: switch between YYMMD [`True`] and DDMMYY [`False`] \
        date formats
        :type yearFirst: :class:`bool`

        :raises: :class:`csb43.utils.Csb43Exception`
        '''
        super(ClosingAccount, self).__init__(**record_settings)

        self.__bankCode = None
        self.__branchCode = None
        self.__accountNumber = None
        self.__debitEntries = None
        self.__creditEntries = None
        self.__debitAmount = None
        self.__creditAmount = None
        self.__totalAmountCode = None
        self.__totalAmount = None
        self.__currencyCode = None
        self.__padding = None

        if record is not None:
            chk_args = self._get_check_args()

            record = self.str_encode(record)
            if not ClosingAccount.is_valid(record):
                raiseCsb43Exception(msg.BAD_RECORD(record), **chk_args)

            # base 1
            # clave de banco: 3-6, N
            self._set_bank_code(record[2:6], **chk_args)
            # clave de oficina: 7-10 N
            self._set_branch_code(record[6:10], **chk_args)
            # num. de cuenta: 11-20
            self._set_account_number(record[10:20], **chk_args)
            # apuntes debe: 21-25, N
            self._set_expense_entries(record[20:25], **chk_args)
            # importes debe: 26-39, N
            self._set_expense_amount(record[25:39], **chk_args)
            # apuntes haber: 40-44 N
            self._set_income_entries(record[39:44], **chk_args)
            # importes haber: 45-58 N
            self._set_income_amount(record[44:58], **chk_args)
            # codigo saldo final 59-59 N
            self._set_total_balance_code(record[58:59], **chk_args)
            # saldo finak
            self._set_total_balance(record[59:73], **chk_args)
            # clave divisa
            self._set_currency_code(record[73:76], **chk_args)
            # libre
            self._set_padding(record[76:80], **chk_args)

    @staticmethod
    def is_valid(record):
        return m3_is_string(record) and\
            (76 <= len(record) <= 80) and (record[0:2] == b'33')

    # expense entries
    #
    # repr: bytes
    # user in: text, int
    # user out: int
    @check_strict(br'^\d{5}$')
    def _set_expense_entries(self, value, **chk_args):
        self.__debitEntries = value

    def _get_expense_entries(self):
        return self.__debitEntries

    @property
    def expenseEntries(self):
        """number of debit entries / (es) numero de entradas en el debe"""
        if self.__debitEntries is None:
            return None
        return int(self.__debitEntries)

    @expenseEntries.setter
    def expenseEntries(self, value):
        field = self._enc_left_pad(value, n=5, fill=b"0")
        self._set_expense_entries(field)

    # income entries
    #
    # repr: bytes
    # user in: text, int
    # user out: int

    @check_strict(br'^\d{5}$')
    def _set_income_entries(self, value, **chk_args):
        self.__creditEntries = value

    def _get_income_entries(self):
        return self.__creditEntries

    @property
    def incomeEntries(self):
        """number of credit entries / (es) numero de entradas en el haber"""
        if self.__creditEntries is None:
            return None
        return int(self.__creditEntries)

    @incomeEntries.setter
    def incomeEntries(self, value):
        value = self._enc_left_pad(value, n=5, fill=b"0")
        self._set_income_entries(value)

    # expense
    #
    # repr: bytes
    # user in: text, int
    # user out: float

    @check_strict(br'^\d{14}$')
    def _set_expense_amount(self, value, **chk_args):
        self.__debitAmount = value

    def _get_expense_amount(self):
        return self.__debitAmount

    @property
    def expense(self):
        """total debit amounts / (es) montante total en el debe"""
        if self.__debitAmount is None:
            return None
        return self._format_currency(self.__debitAmount)

    @expense.setter
    def expense(self, value):
        bal, _ = self._unformat_currency(float(value))
        field = "%014d" % bal
        self._set_expense_amount(self.str_encode(field))

    # income
    #
    # repr: bytes
    # user in: text, int
    # user out: float

    @check_strict(br'^\d{14}$')
    def _set_income_amount(self, value, **chk_args):
        self.__creditAmount = value

    def _get_income_amount(self):
        return self.__creditAmount

    @property
    def income(self):
        """total credit amounts / (es) montante total en el haber"""
        if self.__creditAmount is None:
            return None
        return self._format_currency(self.__creditAmount)

    @income.setter
    def income(self, value):
        bal, _ = self._unformat_currency(float(value))
        field = "%014d" % bal
        self._set_income_amount(self.str_encode(field))

    # balance:
    # total_balance, total_balance_code
    #
    # repr: bytes
    # user in: text, number
    # user out: number

    @check_strict(br'^\d{14}$')
    def _set_total_balance(self, value, **chk_args):
        self.__totalAmount = value

    def _get_total_balance(self):
        return self.__totalAmount

    @check_strict(br'^[12]$')
    def _set_total_balance_code(self, value, **chk_args):
        self.__totalAmountCode = value

    def _get_total_balance_code(self):
        return self.__totalAmountCode

    @property
    def balance(self):
        """final balance / (es) balance final"""
        if self.__totalAmount is None:
            return None
        return self._format_currency(self.__totalAmount,
                                     self.__totalAmountCode)

    @balance.setter
    def balance(self, value):
        bal, sign = self._unformat_currency(float(value))
        field = "%014d" % bal
        self._set_total_balance(self.str_encode(field))
        self._set_total_balance_code(self.str_encode(sign))

    # currency
    #
    # repr: bytes
    # user in: text, number, pycountry
    # user out: pycountry

    @check_strict(br'^\d{3}$')
    def _set_currency_code(self, value, **chk_args):
        self.__currencyCode = value

    def _get_currency_code(self):
        return self.__currencyCode

    @property
    def currency(self):
        """currency object (:class:`pycountry.db.Currency`) /
        (es) objecto de divisa"""
        if self.__currencyCode is None:
            return None
        return currencyISO(self.str_decode(self.__currencyCode))

    @currency.setter
    def currency(self, value):
        value = self._parse_currency_code(value)
        if value:
            self._set_currency_code(value)

    # padding
    #
    # repr: bytes
    # user in: text
    # user out: bytes

    @check_strict(br'^.{4}$')
    def _set_padding(self, value, **chk_args):
        self.__padding = value.rstrip(b' ')

    @property
    def padding(self):
        """padding"""
        return self.__padding

    @padding.setter
    def padding(self, value):
        value = self.str_encode(value)
        field = b_right_pad(value, 4)
        self._set_padding(field)

    # account number
    #
    # repr: bytes
    # user in: text, number
    # user out: bytes

    @check_strict(br'^\d{10}$')
    def _set_account_number(self, value, **chk_args):
        self.__accountNumber = value

    @property
    def accountNumber(self):
        """account number / (es) numero de cuenta"""
        return self.__accountNumber

    @accountNumber.setter
    def accountNumber(self, value):
        value = self.str_encode(value)
        self._set_account_number(value)

    # bank code
    #
    # repr: bytes
    # user in: test, number
    # user out: bytes

    @check_strict(br'^\d{4}$')
    def _set_bank_code(self, value, **chk_args):
        self.__bankCode = value

    @property
    def bankCode(self):
        """bank code / (es) codigo de banco"""
        return self.__bankCode

    @bankCode.setter
    def bankCode(self, value):
        value = self.str_encode(value)
        self._set_bank_code(value)

    # branch code
    #
    # repr: bytes
    # user in: text, number
    # user out: bytes

    @check_strict(br'^\d{4}$')
    def _set_branch_code(self, value, **chk_args):
        self.__branchCode = value

    @property
    def branchCode(self):
        """branch code / (es) codigo de sucursal u oficina"""
        return self.__branchCode

    @branchCode.setter
    def branchCode(self, value):
        field = self._enc_left_pad(value, n=4, fill=b"0")
        self._set_branch_code(field)

    def __bytes__(self):
        return (b"33" +
                b_left_pad(self.bankCode or b'', 4) +
                b_left_pad(self.branchCode or b'', 4) +
                b_left_pad(self.accountNumber or b'', 10) +
                b_left_pad(self._get_expense_entries() or b'', 5, b"0") +
                b_left_pad(self._get_expense_amount() or b'', 14, b"0") +
                b_left_pad(self._get_income_entries() or b'', 5, b"0") +
                b_left_pad(self._get_income_amount() or b'', 14, b"0") +
                b_left_pad(self._get_total_balance_code() or b'', 1, b"0") +
                b_left_pad(self._get_total_balance() or b'', 14, b"0") +
                b_left_pad(self._get_currency_code() or b'', 3, b"0") +
                b_right_pad(self.padding or b'', 4))

    def as_dict(self):
        return {
            msg.T_EXPENSES_ENTRIES: self.expenseEntries,
            msg.T_INCOME_ENTRIES: self.incomeEntries,
            msg.T_EXPENSES: self.expense,
            msg.T_INCOME: self.income,
            msg.T_FINAL_BALANCE: self.balance
        }
