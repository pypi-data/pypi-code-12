
from __future__ import unicode_literals
from __future__ import absolute_import

import unittest
import datetime

from ..csb43 import Transaction, Item, Exchange
from .. import utils
from ..utils.compat import m3_bytes


class TestCsbTransaction(unittest.TestCase):

    def setUp(self):
        self.t = Transaction()

    def test_strict_default(self):
        self.assertTrue(self.t.strict_mode)

    def test_strict_true(self):
        t = Transaction(strict=True)

        self.assertTrue(t.strict_mode)

    def test_strict_false(self):
        t = Transaction(strict=False)

        self.assertFalse(t.strict_mode)

    def test_empty_as_dict(self):
        self.t.as_dict()

    def test_information_mode_default(self):

        self.assertEqual(b'3', self.t.informationMode)

    def test_information_mode_set_int_1(self):

        value = 1

        t = Transaction(informationMode=value)

        self.assertEqual(b'1', t.informationMode)

    def test_information_mode_set_int_2(self):

        value = 2

        t = Transaction(informationMode=value)

        self.assertEqual(b'2', t.informationMode)

    def test_information_mode_set_str_2(self):

        value = "2"

        t = Transaction(informationMode=value)

        self.assertEqual(b'2', t.informationMode)

    def test_init_bad_length(self):
        record = '22011023402150'

        with self.assertRaises(utils.Csb43Exception):
            Transaction(record)

    def test_init_bad_code(self):
        record = '25' + ('1' * 78)

        with self.assertRaises(utils.Csb43Exception):
            Transaction(record)

    def test_init(self):
        record = '22' + ('0' * 25)
        record += '1'
        record += ('0' * 52)

        Transaction(record)

    def test_amount_none(self):

        self.assertIsNone(self.t.amount)

    def test_amount_set_bytes_long(self):
        value = b'12345' * 4

        with self.assertRaises(utils.Csb43Exception):
            self.t.amount = value

    def test_amount_set_str_long(self):
        value = b'12345' * 4

        with self.assertRaises(utils.Csb43Exception):
            self.t.amount = value

    def test_amount_set_bytes_positive(self):
        value = b'12345'

        self.t.amount = value
        self.assertEqual(12345, self.t.amount)

    def test_amount_set_str_positive(self):
        value = '12345'

        self.t.amount = value
        self.assertEqual(12345, self.t.amount)

    def test_amount_set_bytes_negative(self):
        value = b'-12345'

        self.t.amount = value
        self.assertEqual(-12345, self.t.amount)

    def test_amount_set_str_negative(self):
        value = '-12345'

        self.t.amount = value
        self.assertEqual(-12345, self.t.amount)

    def test_amount_set_int_positive(self):

        value = 123456

        self.t.amount = value
        self.assertEqual(123456, self.t.amount)

    def test_amount_set_int_negative(self):

        value = -123456

        self.t.amount = value
        self.assertEqual(-123456, self.t.amount)

    def test_amount_set_float_decimal_truncate_positive(self):

        value = 123456.876

        self.t.amount = value
        self.assertEqual(123456.87, self.t.amount)

    def test_amount_set_float_decimal_truncate_negative(self):

        value = -123456.876

        self.t.amount = value
        self.assertEqual(-123456.87, self.t.amount)

    def test_amount_set_bytes_invalid(self):

        value = b'asdagsa'

        with self.assertRaises(ValueError):
            self.t.amount = value

    def test_amount_set_str_invalid(self):

        value = 'asdagsa'

        with self.assertRaises(ValueError):
            self.t.amount = value

    def test_branch_code_none(self):
        self.assertIsNone(self.t.branchCode)

    def test_branch_code_set_bytes_number(self):

        value = b'1234'

        self.t.branchCode = value
        self.assertEqual(value, self.t.branchCode)

    def test_branch_code_set_str_number(self):

        uvalue = '1234'
        bvalue = b'1234'

        self.t.branchCode = uvalue
        self.assertEqual(bvalue, self.t.branchCode)

    def test_branch_code_set_bytes_alphanum(self):

        value = b'123b'

        with self.assertRaises(utils.Csb43Exception):
            self.t.branchCode = value

    def test_branch_code_set_str_alphanum(self):

        value = '123b'

        with self.assertRaises(utils.Csb43Exception):
            self.t.branchCode = value

    def test_branch_code_set_int(self):

        value = 1234

        self.t.branchCode = value

        self.assertEqual(b'1234', self.t.branchCode)

    def test_branch_code_set_bytes_short(self):

        value = b'123'

        with self.assertRaises(utils.Csb43Exception):
            self.t.branchCode = value

    def test_branch_code_set_str_short(self):

        value = '123'

        with self.assertRaises(utils.Csb43Exception):
            self.t.branchCode = value

    def test_document_number_none(self):
        self.assertIsNone(self.t.documentNumber)

    def test_document_number_set_bytes(self):

        value = b'0123456789'

        self.t.documentNumber = value
        self.assertEqual(int(value), self.t.documentNumber)

    def test_document_number_set_str(self):

        value = '0123456789'

        self.t.documentNumber = value
        self.assertEqual(int(value), self.t.documentNumber)

    def test_document_number_set_bytes_invalid(self):

        value = b'a123456789'

        with self.assertRaises(utils.Csb43Exception):
            self.t.documentNumber = value

    def test_document_number_set_str_invalid(self):

        value = 'a123456789'

        with self.assertRaises(utils.Csb43Exception):
            self.t.documentNumber = value

    def test_document_number_set_bytes_short(self):

        value = b'0123467'

        #self.t.documentNumber = value
        #self.assertEqual(int(value), self.t.documentNumber)
        with self.assertRaises(utils.Csb43Exception):
            self.t.documentNumber = value

    def test_document_number_set_str_short(self):

        value = '0123467'

        #self.t.documentNumber = value
        #self.assertEqual(int(value), self.t.documentNumber)
        with self.assertRaises(utils.Csb43Exception):
            self.t.documentNumber = value

    def test_exchange_none(self):
        self.assertIsNone(self.t.exchange)

    def test_exchange_add_bytes(self):

        value = b'2401978' + b'0' * (14 + 59)
        self.t.add_exchange(value)

        self.assertIsInstance(self.t.exchange, Exchange)
        self.assertEqual('EUR', self.t.exchange.sourceCurrency.letter)

    def test_exchange_add_str(self):

        value = '2401978' + '0' * (14 + 59)
        self.t.add_exchange(value)

        self.assertIsInstance(self.t.exchange, Exchange)
        self.assertEqual('EUR', self.t.exchange.sourceCurrency.letter)

    def test_optional_items_empty(self):
        self.assertListEqual([], self.t.optionalItems)

    def test_add_optional_items(self, t=None):

        if not t:
            t = self.t

        value = Item()
        t.add_item(value)

        self.assertListEqual([value], t.optionalItems)

        value = b'2305' + b' ' * 76
        t.add_item(value)

        self.assertEqual(2, len(t.optionalItems))
        self.assertEqual(value, m3_bytes(t.optionalItems[-1]))

        for n in range(3):
            t.add_item(Item())

        self.assertEqual(5, len(t.optionalItems))

        with self.assertRaises(utils.Csb43Exception):
            self.t.add_item(Item())

    def test_add_optional_bytes_strict_false(self):

        t = Transaction(strict=False)

        value = b'2305' + b' ' * 76
        t.add_item(value)

        item = t.optionalItems[-1]

        self.assertEqual(item.strict_mode, t.strict_mode)
        self.assertFalse(item.strict_mode)

    def test_add_optional_bytes_strict_true(self):

        t = Transaction(strict=True)

        value = b'2305' + b' ' * 76
        t.add_item(value)

        item = t.optionalItems[-1]

        self.assertEqual(item.strict_mode, t.strict_mode)
        self.assertTrue(item.strict_mode)

    def test_own_item_none(self):

        self.assertIsNone(self.t.ownItem)

    def test_own_item_set_bytes_alpha(self):

        value = b'asd'

        with self.assertRaises(utils.Csb43Exception):
            self.t.sharedItem = value

    def test_own_item_set_str_alpha(self):

        value = 'asd'

        with self.assertRaises(utils.Csb43Exception):
            self.t.sharedItem = value

    def test_own_item_set_int(self):

        value = 123

        self.t.ownItem = value

        self.assertEqual(b'123', self.t.ownItem)

    def test_own_item_set_bytes_int(self):

        value = b'025'

        self.t.ownItem = value

        self.assertEqual(b'025', self.t.ownItem)

    def test_own_item_set_str_int(self):

        value = '025'

        self.t.ownItem = value

        self.assertEqual(b'025', self.t.ownItem)

    def test_own_item_set_int_short(self):

        value = 3

        self.t.ownItem = value

        self.assertEqual(b'003', self.t.ownItem)

    def test_own_item_set_int_long(self):

        value = 1234

        with self.assertRaises(utils.Csb43Exception):
            self.t.ownItem = value

    def test_own_item_set_bytes_int_long(self):

        value = b'1256'

        with self.assertRaises(utils.Csb43Exception):
            self.t.ownItem = value

    def test_own_item_set_str_int_long(self):

        value = '1256'

        with self.assertRaises(utils.Csb43Exception):
            self.t.ownItem = value

    def test_reference1_mode1(self):

        t = Transaction(informationMode=1)

        self._test_reference1_mode12(t)

    def test_reference1_mode2(self):

        t = Transaction(informationMode=2)

        self._test_reference1_mode12(t)

    def _test_reference1_mode12(self, t):
        self.assertIsNone(t.reference1)

        values = ('0123456789ab',
                  ' 1234       ',
                  '012345678900',
                  b'0123456789ab',
                  b' 1234       ',
                  b'012345678900')

        for value in values:
            t.reference1 = value

            self.assertEqual(self.t.str_encode(value).rstrip(), t.reference1)

        # invalid

        values = ('0123456789abc',
                  b'0123456789abc')

        for value in values:
            with self.assertRaises(utils.Csb43Exception):
                t.reference1 = value

    def test_reference1_mode3_none(self):

        t = Transaction(informationMode=3)

        self.assertIsNone(t.reference1)

    def test_reference1_mode3_set_bytes_alphanum_short(self):

        t = Transaction(informationMode=3)

        value = b'0123456789ab'

        with self.assertRaises(utils.Csb43Exception):
            t.reference1 = value

    def test_reference1_mode3_set_str_alphanum_short(self):

        t = Transaction(informationMode=3)

        value = '0123456789ab'

        with self.assertRaises(utils.Csb43Exception):
            t.reference1 = value

    def test_reference1_mode3_set_bytes_alphanum_invalid(self):

        t = Transaction(informationMode=3)

        value = b' 1234       '

        with self.assertRaises(utils.Csb43Exception):
            t.reference1 = value

    def test_reference1_mode3_set_str_alphanum_invalid(self):

        t = Transaction(informationMode=3)

        value = ' 1234       '

        with self.assertRaises(utils.Csb43Exception):
            t.reference1 = value

    def test_reference1_mode3_set_bytes_alphanum_invalid2(self):

        t = Transaction(informationMode=3)

        value = b'0123456789abc'

        with self.assertRaises(utils.Csb43Exception):
            t.reference1 = value

    def test_reference1_mode3_set_bytes_number_good_checksum(self):

        t = Transaction(informationMode=3)

        value = b'012345678900'
        t.reference1 = value

        self.assertEqual(value, t.reference1)

    def test_reference1_mode3_set_str_number_good_checksum(self):

        t = Transaction(informationMode=3)

        bvalue = b'012345678900'
        svalue = '012345678900'
        t.reference1 = svalue

        self.assertEqual(bvalue, t.reference1)

    def test_reference2_none(self):

        self.assertIsNone(self.t.reference2)

    def test_reference2_set_bytes(self):

        value = b'0123456789ab0123'
        self.t.reference2 = value

        self.assertEqual(value, self.t.reference2)

    def test_reference2_set_str(self):

        bvalue = b'0123456789ab0123'
        svalue = '0123456789ab0123'
        self.t.reference2 = svalue

        self.assertEqual(bvalue, self.t.reference2)

    def test_reference2_set_bytes_padded(self):

        value = b' 12341234       '
        self.t.reference2 = value

        self.assertEqual(b' 12341234', self.t.reference2)

    def test_reference2_set_str_padded(self):

        value = ' 12341234       '
        self.t.reference2 = value

        self.assertEqual(b' 12341234', self.t.reference2)

    def test_reference2_set_bytes_long(self):

        value = b'0123456789abc'

        with self.assertRaises(utils.Csb43Exception):
            self.t.reference2 = value

    def test_reference2_set_bytes_dot(self):
        value = b'PayPal Europe S.'
        self.t.reference2 = value

        self.assertEqual(value, self.t.reference2)

    def test_reference2_set_str_dot(self):
        bvalue = b'PayPal Europe S.'
        svalue = 'PayPal Europe S.'
        self.t.reference2 = svalue

        self.assertEqual(bvalue, self.t.reference2)

    def test_shared_item_none(self):

        self.assertIsNone(self.t.sharedItem)

    def test_shared_item_set_bytes_alpha_long(self):

        value = b'asd'

        with self.assertRaises(utils.Csb43Exception):
            self.t.sharedItem = value

    def test_shared_item_set_str_alpha_long(self):

        value = 'asd'

        with self.assertRaises(utils.Csb43Exception):
            self.t.sharedItem = value

    def test_shared_item_set_int(self):
        value = 23

        self.t.sharedItem = value

        self.assertEqual(b'23', self.t.sharedItem)

    def test_shared_item_set_bytes_int(self):

        value = b'25'

        self.t.sharedItem = value

        self.assertEqual(b'25', self.t.sharedItem)

    def test_shared_item_set_str_int(self):

        value = '25'

        self.t.sharedItem = value

        self.assertEqual(b'25', self.t.sharedItem)

    def test_shared_item_set_int_short(self):

        value = 3

        self.t.sharedItem = value

        self.assertEqual(b'03', self.t.sharedItem)

    def test_shared_item_set_int_long(self):

        value = 123

        with self.assertRaises(utils.Csb43Exception):
            self.t.sharedItem = value

    def test_shared_item_set_bytes_int_long(self):

        value = b'125'

        with self.assertRaises(utils.Csb43Exception):
            self.t.sharedItem = value

    def test_transaction_date_none(self):

        self.assertIsNone(self.t.transactionDate)

    def test_transaction_date_set_datetime(self):

        d = datetime.date(2002, 3, 4)

        self.t.transactionDate = d

        self.assertEqual(2002, self.t.transactionDate.year)
        self.assertEqual(3, self.t.transactionDate.month)
        self.assertEqual(4, self.t.transactionDate.day)

    def test_value_date_none(self):

        self.assertIsNone(self.t.valueDate)

    def test_value_date_set_datetime(self):

        d = datetime.date(2002, 3, 4)

        self.t.valueDate = d

        self.assertEqual(2002, self.t.valueDate.year)
        self.assertEqual(3, self.t.valueDate.month)
        self.assertEqual(4, self.t.valueDate.day)

    def test_add_exchange_record(self, t=None):

        if not t:
            t = self.t

        e = Exchange()
        e.amount = 12345.5
        e.sourceCurrency = 'EUR'

        record = m3_bytes(e)

        t.add_exchange(record)

        self.assertIsInstance(t.exchange, Exchange)

        self.assertEqual(e.amount, t.exchange.amount)
        self.assertEqual(e.sourceCurrency.letter,
                         t.exchange.sourceCurrency.letter)

    def test_add_exchange_record_strict_false(self):

        t = Transaction(strict=False)

        self.test_add_exchange_record(t=t)

        ex = t.exchange

        self.assertEqual(t.strict_mode, ex.strict_mode)
        self.assertFalse(ex.strict_mode)

    def test_add_exchange_record_strict_true(self):

        t = Transaction(strict=True)

        self.test_add_exchange_record(t=t)

        ex = t.exchange

        self.assertEqual(t.strict_mode, ex.strict_mode)
        self.assertTrue(ex.strict_mode)

    def test_add_exchange_object(self):

        e = Exchange()
        e.amount = 12345.5
        e.sourceCurrency = 'EUR'

        self.t.add_exchange(e)

        self.assertIsInstance(self.t.exchange, Exchange)

        self.assertEqual(e.amount, self.t.exchange.amount)
        self.assertEqual(e.sourceCurrency.letter,
                         self.t.exchange.sourceCurrency.letter)

    def test_iter(self):

        l = [x for x in self.t]

        self.assertEqual(1, len(l))
        self.assertEqual(b'22', l[0][0:2])
        for x in l:
            self.assertEqual(80, len(x))

        self.test_add_exchange_object()

        l = [x for x in self.t]
        self.assertEqual(2, len(l))
        self.assertEqual(b'22', l[0][0:2])
        for x in l:
            self.assertEqual(80, len(x))

        self.assertEqual(l[1], m3_bytes(self.t.exchange))

    def test_bytes(self):

        self.test_iter()

        l = m3_bytes(self.t).split(b'\n')

        li = [x for x in self.t]

        self.assertEqual(l[0], li[0])
        self.assertEqual(l[1], li[1])
