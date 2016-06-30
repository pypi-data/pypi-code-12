# -*- coding: utf-8 -*-
'''
.. note::
    license: GNU Lesser General Public License v3.0 (see LICENSE)
'''

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from .account import Account
from ..utils.compat import (m3_next,
                            m3_bytes,
                            m3_is_string,
                            m3_enc)
from ..utils import (check_strict,
                     b_left_pad,
                     b_right_pad,
                     raiseCsb43Exception)
from ..utils import messages as msg
from ..i18n import tr as _
from .record import (RecordSequence,
                     NextMixin)
import sys


class File(RecordSequence):
    '''
    A CSB43 file

    - Create a :class:`File` object from a file descriptor::

        >>> from csb43.csb43 import File
        >>> with open("csb_file.csb") as fd:
        ...     f = File(fd)
        ...     # do something with f
        ...

    - Create an empty :class:`File` object::

        >>> f = File()

    '''

    def __init__(self,
                 fd=None,
                 **record_settings):
        '''
        :param fd: a csb file
        :type fd: :class:`file`

        :param \*\*record_settings: see :class:`csb43.csb43.RecordSequence`

        :raises: :class:`csb43.utils.Csb43Exception`
        '''

        super(File, self).__init__(**record_settings)
        self.__accounts = []
        self.__closing = None
        self.__numRecords = 0
        self.__fromFile = False

        if fd is not None:

            self.__fromFile = True

            def skip():
                pass

            launcher = {b'00': skip,
                        b'11': self.add_account,
                        b'22': self.add_transaction,
                        b'23': self.add_item,
                        b'24': self.add_exchange,
                        b'33': self.close_account,
                        b'88': self.close_file}

            for line in fd:
                line = self.str_encode(line).rstrip(b'\n\r')
                launcher.get(line[0:2], self.__unknownRecord)(line)
                self.__numRecords += 1

            self.__fromFile = False
        #else:
            #pass

    def __unknownRecord(self, line=b''):
        raiseCsb43Exception(msg.BAD_RECORD(line), **self._get_check_args())

    # accounts
    #
    # repr: [Account]

    @property
    def accounts(self):
        ":rtype: :class:`list` of accounts"
        return self.__accounts

    def get_last_account(self):
        '''
        :rtype: the last added :class:`Account`
        '''
        return self.__accounts[-1]

    def add_account(self, record):
        '''
        Add a new account

        :param record: account record
        :type record: :class:`Account` or :class:`basestring`

        :raises: :class:`csb43.utils.Csb43Exception` if `record` is not valid
        '''
        if isinstance(record, Account):
            self.__accounts.append(record)
        else:
            self.__accounts.append(
                Account(
                    record,
                    **self._settings()
                )
            )

    def add_transaction(self, record):
        '''
        Add a new transaction to the last added account

        :param record: transaction record
        :type record: :class:`Transaction` or :class:`basestring`

        :raises: :class:`csb43.utils.Csb43Exception`

        .. seealso::

            :func:`Account.add_transaction`
        '''
        self.get_last_account().add_transaction(record)

    def add_item(self, record):
        '''
        Add a new additional item record to the last added transaction

        :param record: item record
        :type record: :class:`Item` or :class:`basestring`

        :raises: :class:`csb43.utils.Csb43Exception` when the record is \
        impossible to parse, or if the maximum number of complementary items \
        has been reached

        .. seealso::

            :func:`Transaction.add_item`
        '''
        self.get_last_account().add_item(record)

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
        self.get_last_account().add_exchange(record, update)

    def close_account(self, record=None):
        '''
        Close the current account

        :param record: csb record
        :type record: :class:`ClosingAccount` or :class:`basestring`

        :raises: :class:`csb43.utils.Csb43Exception` if `record` is not valid

        .. seealso::

            :func:`csb43.csb43.Account.close_account`
        '''
        self.get_last_account().close_account(record)

    def close_file(self, record=None):
        '''
        Close the file with a termination record

        :param record: csb record
        :type record: :class:`ClosingFile` or :class:`basestring`

        :raises: :class:`csb43.utils.Csb43Exception` if `record` is not valid

        If record is `None`, a new abstract is generated::

            >>> c = csb.File()
            >>> c.is_closed()
            False
            >>> c.close_file()
            >>> c.is_closed()
            True
            >>> c.abstract.totalRecords
            0
            >>> c.add_account(csb.Account())
            >>> c.abstract.totalRecords
            0
            >>> c.close_file()
            >>> c.abstract.totalRecords
            1
            >>> c.is_closed()
            True

        If record is not empty, the number of records of `File` must be
        coincident with the quantity given in `record`::

            >>> cf = csb.ClosingFile()
            >>> cf.totalRecords = 5
            >>> c.close_file(cf)
            Traceback (most recent call last):
            File "<stdin>", line 1, in <module>
            File "csb43/csb43/csb_file.py", line 200, in close_file

            File "csb43/utils/utils.py", line 25, in raiseCsb43Exception
                raise exc
            csb43.utils.utils.Csb43Exception: registro de cierre de fichero \
incongruente: total de registros 5 != 1
            >>>
        '''
        chk_args = self._get_check_args()

        if self.__fromFile and (self.__closing is not None):
            raiseCsb43Exception(
                _("trying to close an already closed file"),
                **chk_args
            )

        if record is not None:
            if isinstance(record, ClosingFile):
                self.__closing = record
            else:
                self.__closing = ClosingFile(record, **chk_args)

            n_r1 = int(self.__closing.totalRecords)
            n_r2 = self._get_num_records()
            if n_r1 != n_r2:
                raiseCsb43Exception(
                    _('incongruent closing record of file: '
                      'total records %d != %d') % (n_r1, n_r2),
                    **chk_args
                )
        else:
            self.__closing = ClosingFile(**chk_args)
            self.__closing.totalRecords = self._get_num_records()

    def _get_num_records(self):
        if self.__fromFile:
            return self.__numRecords
        else:
            return sum([len([x for x in ac]) for ac in self.accounts])

    def is_closed(self):
        '''
        :rtype: `True` if this File has been properly closed
        '''
        return self.__closing is not None

    @property
    def abstract(self):
        ":rtype: :class:`ClosingFile` file abstract"
        return self.__closing

    def as_dict(self):
        '''
        :rtype: a representation of this object as a :class:`dict`. The keys \
        will be localised

        >>> import csb43.csb43 as csb
        >>> f = csb.File()
        >>> f.add_account(csb.Account())
        >>> f.add_transaction(csb.Transaction())
        >>> import pprint
        >>> pprint.pprint(f.as_dict())
        {u'cuentas': [{u'balance_inicial': None,
                    u'codigo_de_entidad': None,
                    u'codigo_de_sucursal': None,
                    u'divisa': None,
                    u'fecha_de_comienzo': None,
                    u'fecha_de_fin': None,
                    u'modalidad_de_informacion': None,
                    u'movimientos': [{u'cantidad': None,
                                        u'codigo_de_sucursal': None,
                                        u'concepto_comun': None,
                                        u'concepto_propio': None,
                                        u'fecha_de_operacion': None,
                                        u'fecha_valor': None,
                                        u'numero_del_documento': None,
                                        u'primera_referencia': None,
                                        u'segunda_referencia': None}],
                    u'nombre_abreviado': None,
                    u'numero_de_cuenta': None}]}
        '''
        return {
            _("accounts"): [x.as_dict() for x in self.accounts]
        }

    def __iter__(self):
        ''':rtype: iterator of all the `CSB43` records that this object \
        represents

        >>> import csb43.csb43 as csb
        >>> f = csb.File()
        >>> f.add_account(csb.Account())
        >>> f.add_transaction(csb.Transaction())
        >>> for x in f:
        ...     print x
        ...
        11                  000000000000000000000000000000
        22    0000000000000000000001000000000000000000000000000000000000
        88999999999999999999000002
        >>>

        '''
        if not self.__fromFile:
            self.close_file()
        return _FileIter(self)

    def __bytes__(self):
        ''':rtype: representation of this object as `CSB43` records \
        (using `\\\\n` as separator)

        >>> import csb43.csb43 as csb
        >>> f = csb.File()
        >>> f.add_account(csb.Account())
        >>> f.add_transaction(csb.Transaction())
        >>> print f
        11                  000000000000000000000000000000
        22    0000000000000000000001000000000000000000000000000000000000
        88999999999999999999000002
        '''
        return b'\n'.join([x for x in self])

    def showInfo(self, fd=sys.stderr):
        '''
        :param fd: file descriptor where to write to
        :type fd: :class:`file`
        '''

        header = (
            _("{naccounts:d}\taccount(s) read"),
            _("File properly closed:\t{file_is_closed}"),
            _("{total_records:d}\trecord(s) read"),
        )

        txt = "\n".join("* %s" % x for x in header).format(
            naccounts=len(self.accounts),
            file_is_closed=self.is_closed(),
            total_records=self.abstract.totalRecords,
        )

        item_ac = (
            _("+ Account:\t{account_number}\t{short_name}"),
            _("   From:\t{date_from}"),
            _("   To:  \t{date_to}"),
            "",
            _("{ntransactions:d} transaction(s) read"),
            _("Account properly closed:\t{ac_is_closed}"),
            _("Information mode:\t{information_mode}"),
            _("Previous amount:\t{ib_amount:14.2f}\t{ib_currency}"),
            _(" Income:        \t{inc_amount:14.2f}\t{inc_currency}"),
            _(" Expense:       \t{exp_amount:14.2f}\t{exp_currency}"),
            _("Balance:        \t{bal_amount:14.2f}\t{bal_currency}"),
        )

        template = "\n".join("* %s" % x for x in item_ac)

        print(m3_enc(txt, fd), file=fd)

        enc = self.str_decode

        for ac in self.accounts:
            txt = template.format(
                account_number=enc(ac.accountNumber),
                short_name=enc(ac.shortName),
                date_from=ac.initialDate.strftime("%Y-%m-%d"),
                date_to=ac.finalDate.strftime("%Y-%m-%d"),
                ntransactions=len(ac.transactions),
                ac_is_closed=ac.is_closed(),
                information_mode=enc(ac.informationMode),
                ib_amount=ac.initialBalance,
                ib_currency=ac.currency.letter,
                inc_amount=ac.abstract.income,
                inc_currency=ac.abstract.currency.letter,
                exp_amount=ac.abstract.expense,
                exp_currency=ac.abstract.currency.letter,
                bal_amount=ac.abstract.balance,
                bal_currency=ac.abstract.currency.letter,
            )
            print("*" * 60, file=fd)
            print(txt, file=fd)
            print("*" * 60, file=fd)


class _FileIter(NextMixin):

    def __init__(self, f):
        self.__output = []
        self.__output.extend(f.accounts)
        if f.abstract:
            self.__output.append(f.abstract)

        self.__iter = iter(self.__output)
        self.__acc = None

    def __next__(self):
        if self.__acc:
            try:
                return m3_next(self.__acc)
            except StopIteration:
                self.__acc = None
        now = m3_next(self.__iter)

        if isinstance(now, Account):
            self.__acc = iter(now)
            return self.__next__()
        else:
            return m3_bytes(now)


class ClosingFile(RecordSequence):
    '''
    A File abstract, given by a termination record

    Create a :class:`ClosingFile` object from a `CSB43` string record::

        >>> from csb43.csb43 import ClosingFile
        >>> c = ClosingFile(record)

    From an empty object to a `CSB43` string record::

        >>> c = ClosingFile()
        >>> c.totalRecords = 123
        >>> str(c)
        '8899999999999999999900012\
3                                                      '

    '''

    def __init__(self, record=None,
                 **record_settings):
        '''
        :param record: csb record
        :type record: :class:`basestring` or `None`

        :param strict: treat warnings as exceptions when `True`
        :type strict: :class:`bool`

        :raises: :class:`csb43.utils.Csb43Exception`
        '''
        super(ClosingFile, self).__init__(**record_settings)

        self.__totalRecords = None
        self.__padding = None

        if record is not None:
            chk_args = self._get_check_args()

            record = self.str_encode(record)
            if not ClosingFile.is_valid(record):
                raiseCsb43Exception(msg.BAD_RECORD(record), **chk_args)

            self._check_nines(record[2:20], **chk_args)
            self._set_total_records(record[20:26], **chk_args)
            self._set_padding(record[26:80], **chk_args)

    @staticmethod
    def is_valid(record):
        return m3_is_string(record)\
            and (27 <= len(record) <= 80) and (record[0:2] == b'88')

    # padding
    #
    # repr: bytes
    # user in: text
    # user out: bytes

    @check_strict(br'^.{0,54}$')
    def _set_padding(self, value, **chk_args):
        self.__padding = value.rstrip(b" ")

    @property
    def padding(self):
        """padding"""
        return self.__padding

    @padding.setter
    def padding(self, value):
        value = self.str_encode(value)
        self._set_padding(value)

    # total records
    #
    # repr: bytes
    # user in: text, number
    # user out: int

    @check_strict(br'^\d{6}$')
    def _set_total_records(self, value, **chk_args):
        self.__totalRecords = value

    def _get_total_records(self):
        return self.__totalRecords

    @property
    def totalRecords(self):
        """total number of entries

>>> c.totalRecords = 34
>>> c.totalRecords
34
>>> c.totalRecords = '115'
>>> c.totalRecords
115"""
        if self.__totalRecords is None:
            return None
        return int(self.__totalRecords)

    @totalRecords.setter
    def totalRecords(self, value):
        field = self._enc_left_pad(value, n=6, fill=b"0")
        self._set_total_records(field)

    @check_strict(br'^9{18}$')
    def _check_nines(self, value, **chk_args):
        pass

    def __bytes__(self):
        ''':rtype: representation of this object as `CSB43` records \
        (using `\\\\n` as separator)'''
        return (b"88" +
                b"9" * 18 +
                b_left_pad(self._get_total_records() or b'', 6, b"0") +
                b_right_pad(self.padding or b'', 54))
