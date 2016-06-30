# -*- coding: utf-8 -*-
'''
.. note::

    license: GNU Lesser General Public License v3.0 (see LICENSE)
'''

#from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from ..utils.compat import (m3_unicode,
                            m3_bytes,
                            m3_next,
                            m3_long,
                            m3_is_string)
from ..utils import (raiseCsb43Exception,
                     b_left_pad,
                     b_right_pad,
                     check_strict,
                     messages as msg)
from ..i18n import tr as _
from .item import Item
from .record import (RecordSequence,
                     NextMixin)
from .exchange import Exchange


class Transaction(RecordSequence):
    '''
    A Csb43 transaction / (es) Movimiento

    - Create a :class:`Transaction` object from a `CSB43` string record::

        >>> from csb43.csb43 import Transaction
        >>> t = Transaction(record)

    - From an empty object to a `CSB43` string record::

        >>> t = Transaction()
        >>> t.amount = 123.45
        >>> str(t)
        '22    000000000000000000000200000000012345000000000000000000000\
0                '
    '''

    MAX_ITEMS = 5

    def __init__(self, record=None,
                 informationMode=3,
                 **record_settings):
        '''
        :param record: csb record
        :type record: :class:`basestring` or `None`

        :param informationMode: define mode used for transaction parsing, \
        mostly for reference checksum
        :type informationMode: :class:`int`

        :param \*\*record_settings: see :class:`csb43.csb43.RecordSequence`

        :raises: :class:`csb43.utils.Csb43Exception`

        '''
        super(Transaction, self).__init__(**record_settings)
        self.__items = []
        self.__exchange = None
        self.informationMode = informationMode

        if record is not None:
            chk_args = self._get_check_args()

            record = self.str_encode(record)
            if not Transaction.is_valid(record):
                raiseCsb43Exception(msg.BAD_RECORD(record), **chk_args)

            # base 1
            # libre 3-6 -
            self._set_padding(record[2:6], **chk_args)
            # clave oficina origen 7-10 N
            self._set_branch_code(record[6:10], **chk_args)
            # operation date
            self._set_transaction_date(record[10:16], **chk_args)
            # effective date
            self._set_effective_date(record[16:22], **chk_args)
            # concepto comun
            self._set_shared_item(record[22:24], **chk_args)
            # concepto propio
            self._set_own_item(record[24:27], **chk_args)
            # debe o haber
            self._set_expense_or_income(record[27:28], **chk_args)
            # importe
            self._set_amount(record[28:42], **chk_args)
            # num. de documento
            self._set_document_number(record[42:52], **chk_args)
            # referencia 1
            self._set_reference_1(record[52:64], **chk_args)
            # referencia 2
            self._set_reference_2(record[64:80], **chk_args)

        else:
            self.__padding = None
            self.__branchCode = None
            self.__transaction_date = None
            self.__effective_date = None
            self.__sharedItem = None
            self.__ownItem = None
            self.__debitOrCredit = None
            self.__amount = None
            self.__documentNumber = None
            self.__reference1 = None
            self.__reference2 = None

    @staticmethod
    def is_valid(record):
        return m3_is_string(record) and\
            (len(record) == 80) and (record[0:2] == b'22')

    @property
    def informationMode(self):
        return self.__informationMode

    @informationMode.setter
    def informationMode(self, value):
        if value:
            value = self._text2field(value)
        self.__informationMode = value

    # exchange
    #
    # repr: Exchange
    # user in: exchange, record
    # user out: Exchange

    @property
    def exchange(self):
        """exchange object / (es) objecto de cambio de divisa

:rtype: :class:`Exchange`"""
        return self.__exchange

    @exchange.setter
    def exchange(self, value):
        self.add_exchange(value)

    def add_exchange(self, record, update=False):
        '''
        Add a new additional exchange record to the transaction

        :param record: csb exchange record or object
        :type record: :class:`Exchange` or :class:`basestring`

        :param update: update the current exchange object if it exists
        :type update: :class:`bool`

        :raises: :class:`csb43.utils.Csb43Exception`

        Add an exchange object from a `CSB43` string record::

            >>> from csb43.csb43 import Exchange
            >>> record = '{: <80}'.format('240197800000000012345')
            >>> t.add_exchange(record)
            >>> str(t.exchange)
            '24019780000000001234\
5                                                           '

        Add an exchange object from a :class:`Exchange`::

            >>> from csb43.csb43 import Exchange
            >>> e = Exchange()
            >>> e.amount = 123.45
            >>> e.sourceCurrency = 'EUR'
            >>> t.add_exchange(e)
            >>> str(t.exchange)
            '240197800000000012345                                                           '

        '''
        if isinstance(record, Exchange):
            exchange = record
        elif m3_is_string(record):
            exchange = Exchange(record, **self._settings())
        else:
            raiseCsb43Exception(msg.INCOMPATIBLE_OBJECT(record,
                                                        "Exchange",
                                                        "basestring"), True)

        if (self.__exchange is not None) and not update:
            raiseCsb43Exception(
                _("maximum number of exchange record reached (%s)") % 1,
                **self._get_check_args()
            )
        self.__exchange = exchange

    # expense_or_income
    #
    # repr: bytes
    # user in: none (through amount)
    # user out: none (through amount)

    # debit or credit
    @check_strict(br'^[12]$')
    def _set_expense_or_income(self, value, **chk_args):
        self.__debitOrCredit = value

    def _get_expense_or_income(self):
        return self.__debitOrCredit

    # amount
    #
    # repr: bytes
    # user in: text, number
    # user out: number

    @check_strict(br'^\d{14}$')
    def _set_amount(self, value, **chk_args):
        self.__amount = value

    @property
    def amount(self):
        """amount of the transaction / (es) cantidad implicada \
en el movimiento

:rtype: :class:`float`

Quantities can be assigned as numbers or strings, and they will be truncated to
adjust the decimal format set for the object::

    >>> t.amount = 123
    >>> t.amount
    123.0
    >>> t.amount = 123.45
    >>> t.amount
    123.45
    >>> t.amount = '1234.56'
    >>> t.amount
    1234.56
    >>> t.amount = 1.2345
    >>> t.amount
    1.23"""
        if self.__amount is None:
            return None
        return self._format_currency(self.__amount,
                                     debit=self.__debitOrCredit)

    @amount.setter
    def amount(self, value):
        v = float(value)
        quantity, flag_sign = self._unformat_currency(v)
        field = "%014d" % quantity

        self._set_amount(self.str_encode(field))
        self._set_expense_or_income(self.str_encode(flag_sign))

    # document_number
    #
    # repr: bytes
    # user in: text, number
    # user out: number

    @check_strict(br'^\d{10}$')
    def _set_document_number(self, value, **chk_args):
        self.__documentNumber = value

    @property
    def documentNumber(self):
        """document number / (es) número del documento

:rtype: :class:`int`

>>> t.documentNumber = 1
>>> t.documentNumber
1"""
        if self.__documentNumber is None:
            return None
        return int(self.__documentNumber)

    @documentNumber.setter
    def documentNumber(self, value):
        field = self._enc_left_pad(value, n=10, fill=b"0")
        self._set_document_number(field)

    # reference1
    #
    # repr: bytes
    # user in: text
    # user out: text

    def _set_reference_1(self, value, **chk_args):
        # modalidad 1 y 2 = libre, modalidad 3 = checksum
        if self.informationMode == b'3':
            self._set_reference_1_mode_3(value, **chk_args)
        else:
            self._set_reference_1_other_modes(value, **chk_args)

    @check_strict(br'^\d{12}$')
    def _set_reference_1_mode_3(self, value, **chk_args):
        Transaction._validate_reference(
            self.str_decode(value),
            **chk_args
        )
        self.__reference1 = value

    @check_strict(br'^[ \w]{12}$')
    def _set_reference_1_other_modes(self, value, **chk_args):
        self.__reference1 = value.rstrip(b' ')

    @property
    def reference1(self):
        """first reference (checksummed) / (es) primera \
referencia (verificada)

When using the information mode 3, the field is checksummed.

:rtype: :class:`str`

>>> t.informationMode = 3
>>> t.reference1 = '012345678900'
>>> t.reference1
'012345678900'
>>> try:
...     t.reference1 = '012345678901'
... except Exception, e:
...     print e
...
Validación fallida para el campo de referencia '012345678901'"""
        return self.__reference1

    @reference1.setter
    def reference1(self, value):
        value = self.str_encode(value)
        self._set_reference_1(value)

    @staticmethod
    def _validate_reference(value, **chk_args):
        n = value.strip(' ')
        try:
            m3_long(n)
            control = int(n[-1])
            res = (sum([int(x) * ((i % 8) + 2) for (i, x)
                        in enumerate(reversed(n[:-1]))]) % 11) % 10

            if res != control:
                raiseCsb43Exception(
                    _("Validation failed for reference '%s'") % value,
                    **chk_args
                )

            return n
        except ValueError:
            return n

    # reference2
    #
    # repr: bytes
    # user in: text
    # user out: bytes

    @check_strict(br'^[\x20-\xFF]{16}$')
    def _set_reference_2(self, value, **chk_args):
        self.__reference2 = value.rstrip(b' ')

    @property
    def reference2(self):
        """second reference (not checksummed) / (es) \
segunda referencia (no verificada)

:rtype: :class:`str`

>>> t.reference2 = '{: >16}'.format('something')
>>> t.reference2
'       something'"""
        return self.__reference2

    @reference2.setter
    def reference2(self, value):
        value = self.str_encode(value)
        self._set_reference_2(value)

    # optional_items
    #
    # repr: [item]
    # user in: none
    # user out: [item]

    @property
    def optionalItems(self):
        """list of optional items / (es) lista de \
conceptos adicionales

:rtype: :class:`list` of :class:`Item` attached to this transaction"""
        return self.__items

    def add_item(self, record):
        '''
        Add a new optional item to the transaction.

        :param record: item record
        :type record: :class:`Item` or :class:`basestring`

        :raises: :class:`csb43.utils.Csb43Exception` when the record is \
        impossible to parse, or if the maximum number of complementary items \
        has been reached
        '''
        chk_args = self._get_check_args()

        if len(self.__items) == Transaction.MAX_ITEMS:
            raiseCsb43Exception(_("the maximum number of complementary items"
                                " for transaction has been reached: %d") %
                                Transaction.MAX_ITEMS, **chk_args)
        if m3_is_string(record):
            self.__items.append(Item(record, **chk_args))
        elif isinstance(record, Item):
            self.__items.append(record)
        else:
            raiseCsb43Exception(
                msg.INCOMPATIBLE_OBJECT(record, "Item", "basestring"),
                True
            )

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
        return self.__padding

    @padding.setter
    def padding(self, value):
        value = self.str_encode(value)
        self._set_padding(value)

    # branch_code
    #
    # repr: bytes
    # user in: text
    # user out: bytes

    @check_strict(br'^\d{4}$')
    def _set_branch_code(self, value, **chk_args):
        self.__branchCode = value

    @property
    def branchCode(self):
        """branch code / (es) código de sucursal u oficina

:rtype: :class:`str`

>>> t.branchCode = '0000'
>>> t.branchCode
'0000'"""
        return self.__branchCode

    @branchCode.setter
    def branchCode(self, value):
        field = self._enc_left_pad(value, n=4, fill=b"0")
        self._set_branch_code(field)

    # transaction_date
    #
    # repr: bytes
    # user in: datetime
    # user out: datetime

    @check_strict(br'^\d{6}$')
    def _set_transaction_date(self, value, **chk_args):
        self.__transaction_date = value

    @property
    def transactionDate(self):
        """transaction date / (es) fecha de la operación

:rtype: :class:`datetime.datetime`

Setting a date::

    >>> t.transactionDate = datetime.datetime(year=2012,month=2,day=13).date()
    >>> t.transactionDate
    datetime.datetime(2012, 2, 13, 0, 0)"""
        if self.__transaction_date is None:
            return None
        return self._format_date(self.str_decode(self.__transaction_date))

    @transactionDate.setter
    def transactionDate(self, value):
        value = self.str_encode(self._unformat_date(value))
        self._set_transaction_date(value)

    # effective date
    #
    # repr: bytes
    # user in: datetime
    # user out: datetime

    @check_strict(br'^\d{6}$')
    def _set_effective_date(self, value, **chk_args):
        self.__effective_date = value

    @property
    def valueDate(self):
        """value date / (es) fecha valor

:rtype: :class:`datetime.datetime`

Setting a date::

    >>> t.valueDate = datetime.datetime(year=2012,month=2,day=13).date()
    >>> t.valueDate
    datetime.datetime(2012, 2, 13, 0, 0)"""
        if self.__effective_date is None:
            return None
        return self._format_date(self.str_decode(self.__effective_date))

    @valueDate.setter
    def valueDate(self, value):
        value = self.str_encode(self._unformat_date(value))
        self._set_effective_date(value)

    # shared_item
    #
    # repr: bytes
    # user in: text, number
    # user out: bytes

    @check_strict(br'^\d{2}$')
    def _set_shared_item(self, value, **chk_args):
        self.__sharedItem = value

    @property
    def sharedItem(self):
        """inter-bank shared item / (es) concepto común

:rtype: :class:`str`

>>> t.sharedItem = 12
>>> t.sharedItem
'12'
>>> t.sharedItem = '04'
>>> t.sharedItem
'04'
>>> from csb43.csb43 import utils
>>> utils.CONCEPTOS[t.sharedItem]
'GIROS - TRANSFERENCIAS - TRASPASOS - CHEQUES'"""
        return self.__sharedItem

    @sharedItem.setter
    def sharedItem(self, value):
        field = self._enc_left_pad(value, n=2, fill=b"0")
        self._set_shared_item(field)

    # own item
    #
    # repr: bytes
    # user in: text, number
    # user out: bytes

    @check_strict(br'^\d{3}$')
    def _set_own_item(self, value, **chk_args):
        self.__ownItem = value

    @property
    def ownItem(self):
        """own item (given by each bank to its transactions) / \
(es) concepto propio del banco

:rtype: :class:`str`

>>> t.ownItem = 123
>>> t.ownItem
'123'
>>> t.ownItem = '125'
>>> t.ownItem
'125'"""
        return self.__ownItem

    @ownItem.setter
    def ownItem(self, value):
        field = self._enc_left_pad(value, n=3, fill=b"0")
        self._set_own_item(field)

    def __str_main_record(self):
        ':rtype: representation of this object as a `CSB43` record'
        return (b"22" +
                b_right_pad(self.padding or b'', 4) +
                b_left_pad(self.branchCode or b'', 4, b'0') +
                b_left_pad(self.__transaction_date or b'', 6, b'0') +
                b_left_pad(self.__effective_date or b'', 6, b'0') +
                b_left_pad(self.__sharedItem or b'', 2, b'0') +
                b_left_pad(self.__ownItem or b'', 3, b'0') +
                (self.__debitOrCredit or b'1') +
                b_left_pad(self.__amount or b'', 14, b'0') +
                b_left_pad(self.__documentNumber or b'', 10, b'0') +
                b_left_pad(self.__reference1 or b'', 12, b'0') +
                b_right_pad(self.__reference2 or b'', 16))

    def __iter__(self):
        ''':rtype: iterator of all the `CSB43` records that this object
        represents

>>> [x for x in t]
['22    000000000012021300000200000000123456000000000001234567890\
0       something', '2301first item recor\
d                                                           '\
, '2302second item recor\
d                                                          '\
, '24018400000000001230\
0                                                           ']

        '''
        return _TransactionIter(self, self.__str_main_record())

    def __bytes__(self):
        r''':rtype: representation of this object as `CSB43` records
        (using `\\n` as separator)

>>> str(t)
'22    000000000012021300000200000000123456000000000001234567890\
0       something\n2301first item recor\
d                                                           \n2302\
second item recor\
d                                                          \n2401840000000\
00012300                                                           '
        '''
        return b'\n'.join([x for x in self])

    def as_dict(self):
        '''
        :rtype: a representation of this object as a :class:`dict`. \
        The keys will be localised

        >>> t.as_dict()
        {u'cantidad': 123.45, u'primera_referencia': None, \
         u'segunda_referencia': None, u'concepto_propio': None, \
         u'fecha_de_operacion': None, u'numero_del_documento': None, \
         u'codigo_de_sucursal': None, u'concepto_comun': None, \
         u'fecha_valor': None}
        '''
        d = {
            msg.T_BRANCH_CODE: self.str_decode(self.branchCode),
            msg.T_TRANSACTION_DATE: (m3_unicode(self.transactionDate.date())
                                     if self.transactionDate else None),
            msg.T_VALUE_DATE: (m3_unicode(self.valueDate.date())
                               if self.valueDate else None),
            msg.T_SHARED_ITEM: self.str_decode(self.sharedItem),
            msg.T_OWN_ITEM: self.str_decode(self.ownItem),
            msg.T_AMOUNT: self.amount,
            msg.T_DOCUMENT_NUMBER: self.documentNumber,
            msg.T_REFERENCE_1: self.str_decode(self.reference1),
            msg.T_REFERENCE_2: self.str_decode(self.reference2),
        }

        if len(self.optionalItems):
            d[msg.T_OPTIONAL_ITEMS] = [x.as_dict() for x in self.optionalItems]

        if self.exchange:
            d[msg.T_EXCHANGE] = self.exchange.as_dict()

        return d


class _TransactionIter(NextMixin):

    def __init__(self, trans, mainRecord):
        self.__output = [mainRecord]
        self.__output.extend(trans.optionalItems)
        if trans.exchange:
            self.__output.append(trans.exchange)

        self.__iter = iter(self.__output)

    def __next__(self):
        return m3_bytes(m3_next(self.__iter))
