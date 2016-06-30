
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import unittest
import pycountry

from ..csb43 import Exchange
from .. import utils
from ..utils.compat import (m3_bytes,
                            m3_unicode)


class TestCsbExchange(unittest.TestCase):

    def setUp(self):
        self.exch = Exchange()

    def test_init(self):

        Exchange()

    def test_strict_default(self):
        self.assertTrue(self.exch.strict_mode)

    def test_strict_true(self):
        exch = Exchange(strict=True)

        self.assertTrue(exch.strict_mode)

    def test_strict_false(self):
        exch = Exchange(strict=False)

        self.assertFalse(exch.strict_mode)

    def test_empty_as_dict(self):
        self.exch.as_dict()

    def test_init_bad_length(self):
        record = '24011023402150'

        with self.assertRaises(utils.Csb43Exception):
            Exchange(record)

    def test_init_bad_code_str(self):
        record = '2501' + ('1' * 76)

        with self.assertRaises(utils.Csb43Exception):
            Exchange(record)

    def test_init_bad_code_bytes(self):
        record = b'2501' + (b'1' * 76)

        with self.assertRaises(utils.Csb43Exception):
            Exchange(record)

    def test_init_record_str(self):
        record = '2401'
        record += '840'  # currency code
        record += '14' * 7  # amount
        record += '1' * 59

        try:
            e = Exchange(record)

            self.assertEqual('USD', e.sourceCurrency.letter)
            self.assertEqual(141414141414.14, e.amount)

        except utils.Csb43Exception:
            self.fail("exception not expected")

    def test_init_record_bytes(self):
        record = b'2401'
        record += b'840'  # currency code
        record += b'14' * 7  # amount
        record += b'1' * 59

        try:
            e = Exchange(record)

            self.assertEqual('USD', e.sourceCurrency.letter)
            self.assertEqual(141414141414.14, e.amount)

        except utils.Csb43Exception:
            self.fail("exception not expected")

    def test_source_currency_none(self):

        self.assertIsNone(self.exch.sourceCurrency)

    def test_source_currency_set_int_invalid(self):

        with self.assertRaises(utils.Csb43Exception):
            self.exch.sourceCurrency = 3

    def test_source_currency_set_bytes_invalid(self):

        with self.assertRaises(utils.Csb43Exception):
            self.exch.sourceCurrency = b'asdfalsjk'

    def test_source_currency_set_str_invalid(self):

        with self.assertRaises(utils.Csb43Exception):
            self.exch.sourceCurrency = 'asdfalsjk'

    def test_source_currency_set_int_euro(self):

        self.exch.sourceCurrency = 978

        self.assertIsNotNone(self.exch.sourceCurrency)
        self.assertEqual('EUR', self.exch.sourceCurrency.letter)

    def test_source_currency_set_bytes_dollar(self):

        self.exch.sourceCurrency = b'usd'  # 840

        self.assertIsNotNone(self.exch.sourceCurrency)
        self.assertEqual('840', self.exch.sourceCurrency.numeric)

    def test_source_currency_set_str_dollar(self):

        self.exch.sourceCurrency = 'usd'  # 840

        self.assertIsNotNone(self.exch.sourceCurrency)
        self.assertEqual('840', self.exch.sourceCurrency.numeric)

    def test_source_currency_set_bytes_euro(self):

        self.exch.sourceCurrency = b'978'

        self.assertIsNotNone(self.exch.sourceCurrency)
        self.assertEqual('EUR', self.exch.sourceCurrency.letter)

    def test_source_currency_set_str_euro(self):

        self.exch.sourceCurrency = '978'

        self.assertIsNotNone(self.exch.sourceCurrency)
        self.assertEqual('EUR', self.exch.sourceCurrency.letter)

    #def test_source_currency_set_pycountry_bytes(self):

        #self.exch.sourceCurrency = pycountry.currencies.get(numeric=b'840')

        #self.assertIsNotNone(self.exch.sourceCurrency)
        #self.assertEqual('USD', self.exch.sourceCurrency.letter)

    def test_source_currency_set_pycountry_str(self):

        self.exch.sourceCurrency = pycountry.currencies.get(numeric='840')

        self.assertIsNotNone(self.exch.sourceCurrency)
        self.assertEqual('USD', self.exch.sourceCurrency.letter)

    def test_amount_none(self):

        self.assertIsNone(self.exch.amount)

    def test_amount_set_none(self):

        with self.assertRaises(TypeError):
            self.exch.amount = None

    def test_amount_set_bytes_long(self):

        value = b'12345' * 4

        with self.assertRaises(utils.Csb43Exception):
            self.exch.amount = value

    def test_amount_set_str_long(self):

        value = '12345' * 4

        with self.assertRaises(utils.Csb43Exception):
            self.exch.amount = value

    def test_amount_set_bytes(self):

        value = b'12345'

        self.exch.amount = value
        self.assertEqual(12345, self.exch.amount)

    def test_amount_set_str(self):

        value = b'12345'

        self.exch.amount = value
        self.assertEqual(12345, self.exch.amount)

    def test_amount_int(self):

        value = 123456

        self.exch.amount = value
        self.assertEqual(123456, self.exch.amount)

    def test_amount_set_float_decimal_truncate(self):

        value = 123456.876

        self.exch.amount = value
        self.assertEqual(123456.87, self.exch.amount)

    def test_amount_set_bytes_decimal_truncate(self):

        value = b'123456.876'

        self.exch.amount = value
        self.assertEqual(123456.87, self.exch.amount)

    def test_amount_set_str_decimal_truncate(self):

        value = '123456.876'

        self.exch.amount = value
        self.assertEqual(123456.87, self.exch.amount)

    def test_amount_set_bytes_invalid_text(self):

        value = b'asdagsa'

        with self.assertRaises(ValueError):
            self.exch.amount = value

    def test_padding_none(self):

        self.assertIsNone(self.exch.padding)

    def test_padding_set_str(self):

        bvalue = b"asdga shfadsas"
        svalue = "asdga shfadsas"

        self.exch.padding = svalue

        self.assertEqual(bvalue, self.exch.padding)

    def test_padding_set_bytes_full(self):

        value = b"1" * 59

        self.exch.padding = value

        self.assertEqual(value, self.exch.padding)

    def test_padding_set_bytes_strip(self):

        value = b"0" * 9 + (b" a c " * 10)

        self.exch.padding = value

        self.assertEqual(value.rstrip(b" "), self.exch.padding)

    def test_bytes1(self):
        s = m3_bytes(self.exch)

        self.assertEqual(80, len(s))

        self.assertEqual(b'2401', s[0:4])

    def test_str1(self):
        s = m3_unicode(self.exch)

        self.assertEqual(80, len(s))

        self.assertEqual('2401', s[0:4])

    def test_bytes2(self, exch=None):

        exch = exch or self.exch

        exch.amount = 12345.678

        exch.sourceCurrency = 'EUR'

        s = m3_bytes(exch)

        e = Exchange(s, strict=True, decimal=2)

        self.assertEqual('EUR', e.sourceCurrency.letter)
        self.assertEqual(12345.67, e.amount)

        self.assertEqual(m3_bytes(e), s)

    def test_iter(self):

        self.test_bytes2()

        r = [x for x in self.exch]

        self.assertEqual(1, len(r))

        self.assertEqual(m3_bytes(self.exch), r[0])
