'''
@license: GNU Lesser General Public License v3.0 (see LICENSE)
'''
from __future__ import absolute_import
from .. import utils
from ..utils import compat

import numbers
import re
from ..utils import (messages as msg,
                     currencyISOByLetter,
                     currencyISO,
                     isCurrency,
                     b_left_pad,
                     raiseCsb43Exception)
from ..utils.compat import (m3_unicode,
                            m3_is_string)


class BytesMixin(object):

    if compat.IS_PY2:
        def __str__(self):
            return self.__bytes__()
    else:
        def __str__(self):
            return self.__unicode__()

    def __bytes__(self):
        raise NotImplementedError("__bytes__")

    def __unicode__(self):
        raise NotImplementedError("__unicode__")


class NextMixin(object):

    if compat.IS_PY2:
        def next(self):
            return self.__next__()


class RecordSequence(BytesMixin):
    '''
    Generic record in a CSB43 file
    '''

    ENCODING = "latin1"
    DECIMAL = utils.DECIMAL

    CUR_NUM = re.compile(r'^\d{3}$')
    CUR_LET = re.compile(r'^[a-zA-Z]{3}$')

    def __init__(self,
                 strict=True,
                 decimal=utils.DECIMAL,
                 yearFirst=True,
                 encoding=ENCODING,
                 silent=False):
        '''
        Constructor
        '''
        self._s_decimal = decimal
        self._s_year_first = yearFirst
        self._s_encoding = encoding
        self.__strict = strict
        self.__silent = silent

    def _settings(self):
        d = {
            "decimal": self._s_decimal,
            "yearFirst": self._s_year_first,
            "encoding": self._s_encoding,
        }
        d.update(self._get_check_args())
        return d

    @property
    def str_encoding(self):
        return self._s_encoding

    def set_decimal_precision(self, decimal):
        self._s_decimal = decimal

    def set_year_first(self, yearFirst=True):
        self._s_year_first = yearFirst

    @property
    def strict_mode(self):
        return self.__strict

    @property
    def silent_mode(self):
        return not self.__strict and self.__silent

    def _get_check_args(self):
        return {
            "strict": self.strict_mode,
            "silent": self.silent_mode,
        }

    def _format_date(self, value):
        '''
        Args:
            value (str) -- CSB date
        Return:
            (datetime)  -- date object
        '''
        return utils.raw2date(value, self._s_year_first)

    def _unformat_date(self, value):
        '''
        Args:
            value (datetime) -- date object
        Return:
            (str)            -- CSB date
        '''
        return utils.date2raw(value, self._s_year_first)

    def _format_currency(self, value, debit=b'2'):
        '''
        Args:
            value (str)     -- CSB raw amount
            debit (r'[12]') -- flag to indicate credit or debit
        Return:
            (int)           -- formatted numeric amount
        '''
        return utils.raw2currency(value, self._s_decimal, debit)

    def _unformat_currency(self, value):
        '''
        Args:
            value (int) -- amount
        Return:
            pair (raw amount), (debit [2] or credit [1])
        '''
        return utils.currency2raw(value, self._s_decimal)

    def str_encode(self, value, valnone=b'', **kwargs):
        if value is None:
            return valnone
        if isinstance(value, compat.m3_unicode):
            value = value.encode(self._s_encoding)
        elif not isinstance(value, compat.m3_bytes):
            value = compat.m3_bytes(value)
        return value

    def str_decode(self, value):
        if value is None:
            return None
        return value.decode(self._s_encoding)

    def _text2field(self, value, **kwargs):
        if value and not m3_is_string(value):
            value = m3_unicode(value)

        return self.str_encode(value, **kwargs)

    def _enc_left_pad(self, value, **kwargs):
        out = self._text2field(value, **kwargs)
        if isinstance(value, numbers.Number):
            return b_left_pad(out, **kwargs)
        return out

    def __unicode__(self):
        return self.str_decode(self.__bytes__())

    def _parse_currency_code(self, value):
        out = None
        try:
            if isCurrency(value):
                out = value.numeric
            else:
                if isinstance(value, numbers.Number):
                    val = "%03d" % value
                else:
                    val = self.str_decode(self.str_encode(value))
                obj = None
                if self.CUR_NUM.match(val):
                    obj = currencyISO(val)
                elif self.CUR_LET.match(val):
                    obj = currencyISOByLetter(val.upper())
                else:
                    raiseCsb43Exception(
                        msg.CURRENCY_EXPECTED(val),
                        strict=True
                    )
                if obj:
                    out = obj.numeric
        except KeyError:
            raiseCsb43Exception(msg.CURRENCY_EXPECTED(value), strict=True)

        if out is not None:
            return self.str_encode(out)
        return out
