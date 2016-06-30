# -*- coding: utf-8 -*-
'''
.. note::

    license: GNU Lesser General Public License v3.0 (see LICENSE)
'''

from __future__ import unicode_literals
from __future__ import absolute_import

from ..utils.compat import (m3_is_string,
                            m3_bytes)
from ..utils import (check_strict,
                     raiseCsb43Exception)
from ..utils import (messages as msg,
                     b_left_pad,
                     b_right_pad)
#from csb43.i18n import tr as _

from .record import RecordSequence


class Item(RecordSequence):
    '''
    Complementary item / (es) Concepto adicional (registro 23)

    - Create an :class:`Item` object from a `CSB43` string record::

        >>> from csb43.csb43 import Item
        >>> record = '2301primer concepto adicional             segundo \
concepto adicional            '
        >>> i = Item(record)
        >>> i.item1
        'primer concepto adicional'
        >>> i.item2
        'segundo concepto adicional'
        >>> i.recordCode
        1

    - From an empty object to a `CSB43` string record::

        >>> i = Item()
        >>> i.item1 = 'primer concepto adicional'
        >>> i.item2 = 'segundo concepto adicional'
        >>> i.recordCode = 1
        >>> str(i)
        '2301primer concepto adicional             segundo concepto \
adicional            '
    '''

    def __init__(self, record=None,
                 **record_settings):
        '''
        :param record: csb record
        :type record: :class:`basestring` or `None`

        :param \*\*record_settings: see :class:`csb43.csb43.RecordSequence`

        :raises: :class:`csb43.utils.Csb43Exception`

        '''
        super(Item, self).__init__(**record_settings)

        self.__recordCode = None
        self.__item1 = None
        self.__item2 = None

        if record is not None:
            chk_args = self._get_check_args()

            record = self.str_encode(record)
            if not self.is_valid(record):
                raiseCsb43Exception(msg.BAD_RECORD(record), **chk_args)

            self._set_record_code(record[2:4], **chk_args)
            self._set_item_1(record[4:42], **chk_args)
            self._set_item_2(record[42:80], **chk_args)

    def is_valid(self, record):
        return m3_is_string(record) and\
            (len(record) == 80) and (record[0:2] == b'23')

    # record_code
    #
    # repr: bytes
    # user in: text
    # user out: int

    @check_strict(br'^0[12345]$')
    def _set_record_code(self, value, **chk_args):
        self.__recordCode = value

    @property
    def recordCode(self):
        """code of record / (es) codigo de registro

Code can be assigned as a number or as a string::

    >>> i.recordCode = 1
    >>> i.recordCode
    1
    >>> i.recordCode = '2'
    >>> i.recordCode
    2
    >>> i.recordCode = '01'
    >>> i.recordCode
    1
    >>> try:
    ...     i.recordCode = 10
    ... except Exception, e:
    ...     print e
    ...
    mal formato: el contenido '10' no concuerda con el formato \
esperado r'^0[12345]$' para este campo"""
        if self.__recordCode is None:
            return None
        return int(self.__recordCode)

    @recordCode.setter
    def recordCode(self, value):
        value = self._text2field(value, valnone=None)
        field = b_left_pad(value, 2, b"0")
        self._set_record_code(field)

    # item1
    #
    # repr: bytes
    # user in: text
    # user out: bytes

    @check_strict(br'^[\x20-\xFF]{38}$')
    def _set_item_1(self, value, **chk_args):
        self.__item1 = value.rstrip(b' ')

    @property
    def item1(self):
        "first additional item / (es) primer concepto adicional"
        return self.__item1

    @item1.setter
    def item1(self, value):
        value = self._text2field(value)
        field = b_right_pad(value, 38)
        self._set_item_1(field)

    # item2
    #
    # repr: bytes
    # user in: text
    # user out: bytes

    @check_strict(br'^[\x20-\xFF]{38}$')
    def _set_item_2(self, value, **chk_args):
        self.__item2 = value.rstrip(b' ')

    @property
    def item2(self):
        "second additional item / (es) segundo concepto adicional"
        return self.__item2

    @item2.setter
    def item2(self, value):
        value = self._text2field(value)
        field = b_right_pad(value, 38)
        self._set_item_2(field)

    def __bytes__(self):
        ':rtype: representation of this object as a `CSB43` record'
        record = (b"23" +
                  b_left_pad(self.__recordCode or b'', 2, b"0") +
                  b_right_pad(self.__item1 or b'', 38) +
                  b_right_pad(self.__item2 or b'', 38))

        return record

    def __iter__(self):
        return iter([m3_bytes(self)])

    def as_dict(self):
        '''
        :rtype: a representation of this object as a :class:`dict`. The keys \
        will be localised

        >>> i.as_dict()
        {u'concepto1': 'primer concepto adicional', u'concepto2': 'segundo \
        concepto adicional', u'codigo_de_registro': 1}

        '''
        return {
            msg.T_RECORD_CODE: self.recordCode,
            msg.T_ITEM_1: self.str_decode(self.item1),
            msg.T_ITEM_2: self.str_decode(self.item2),
        }
