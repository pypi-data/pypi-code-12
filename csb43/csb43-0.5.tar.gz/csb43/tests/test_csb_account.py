# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import unittest

from ..csb43 import (Account,
                     ClosingAccount,
                     Exchange,
                     Item,
                     Transaction)
from .. import utils
from ..utils.compat import (m3_bytes,
                            m3_is_string)
from ..csb43 import record
import pycountry
from datetime import datetime


class TestCsbAccount(unittest.TestCase):

    def setUp(self):
        self.t = Account()

    def test_strict_default(self):
        self.assertTrue(self.t.strict_mode)

    def test_strict_true(self):
        t = Account(strict=True)

        self.assertTrue(t.strict_mode)

    def test_strict_false(self):
        t = Account(strict=False)

        self.assertFalse(t.strict_mode)

    def test_empty_as_dict(self):
        self.t.as_dict()

    def test_init_bad_code(self):
        record = b'12' + (b'1' * 78)

        self.assertEqual(80, len(record))

        with self.assertRaises(utils.Csb43Exception):
            Account(record)

    def test_init_bad_length(self):
        record = b'1112380118008'

        with self.assertRaises(utils.Csb43Exception):
            Account(record)

    def test_init_bytes(self):
        record = b'11' + (b'1' * 78)

        self.assertEqual(80, len(record))

        Account(record)

    def test_init_str(self):
        record = '11' + ('1' * 78)

        self.assertEqual(80, len(record))

        Account(record)

    def test_transactions(self):
        self.assertIsNotNone(self.t.transactions)
        self.assertIsInstance(self.t.transactions, list)
        self.assertEqual(len(self.t.transactions), 0)

    def test_initial_date_none(self):
        self.assertIsNone(self.t.initialDate)

    def test_initial_date_set_bytes(self):

        value = b'230434'

        with self.assertRaises(utils.Csb43Exception):
            self.t.initialDate = value

    def test_initial_date_set_datetime(self):

        value = datetime(year=2004, month=3, day=1).date()

        self.t.initialDate = value

        self.assertEqual(2004, self.t.initialDate.year)
        self.assertEqual(3, self.t.initialDate.month)
        self.assertEqual(1, self.t.initialDate.day)

    def test_final_date_none(self):
        self.assertIsNone(self.t.finalDate)

    def test_final_date_set_bytes(self):

        value = b'230434'

        with self.assertRaises(utils.Csb43Exception):
            self.t.finalDate = value

    def test_final_date_set_datetime(self):

        value = datetime(year=2004, month=3, day=1).date()

        self.t.finalDate = value

        self.assertEqual(2004, self.t.finalDate.year)
        self.assertEqual(3, self.t.finalDate.month)
        self.assertEqual(1, self.t.finalDate.day)

    def test_initial_balance_none(self):
        self.assertIsNone(self.t.initialBalance)

    def test_initial_balance_set_bytes_long(self):

        value = b'12345' * 4

        with self.assertRaises(utils.Csb43Exception):
            self.t.initialBalance = value

    def test_initial_balance_set_str_long(self):

        value = '12345' * 4

        with self.assertRaises(utils.Csb43Exception):
            self.t.initialBalance = value

    def test_initial_balance_set_bytes_int(self):

        value = b'12345'

        self.t.initialBalance = value
        self.assertEqual(12345, self.t.initialBalance)

    def test_initial_balance_set_str_int(self):

        value = '12345'

        self.t.initialBalance = value
        self.assertEqual(12345, self.t.initialBalance)

    def test_initial_balance_set_str_int_negative(self):

        value = '-12345'

        self.t.initialBalance = value
        self.assertEqual(-12345, self.t.initialBalance)

    def test_initial_balance_set_int_negative(self):

        value = -12345

        self.t.initialBalance = value
        self.assertEqual(-12345, self.t.initialBalance)

    def test_initial_balance_set_int(self):

        value = 123456

        self.t.initialBalance = value
        self.assertEqual(123456, self.t.initialBalance)

    def test_initial_balance_set_float_decimal_truncate(self):

        value = 123456.876

        self.t.initialBalance = value
        self.assertEqual(123456.87, self.t.initialBalance)

    def test_initial_balance_set_bytes_invalid(self):

        value = b'asdagsa'

        with self.assertRaises(ValueError):
            self.t.initialBalance = value

    def test_initial_balance_set_str_invalid(self):

        value = 'asdagsa'

        with self.assertRaises(ValueError):
            self.t.initialBalance = value

    def test_currency_none(self):
        self.assertIsNone(self.t.currency)

    def test_currency_set_int_invalid(self):

        with self.assertRaises(utils.Csb43Exception):
            self.t.currency = 3

    def test_currency_set_bytes_invalid(self):

        with self.assertRaises(utils.Csb43Exception):
            self.t.currency = b'asdfalsjk'

    def test_currency_set_str_invalid(self):

        with self.assertRaises(utils.Csb43Exception):
            self.t.currency = 'asdfalsjk'

    def test_currency_set_int_euro(self):

        self.t.currency = 978

        self.assertIsNotNone(self.t.currency)
        self.assertEqual('EUR', self.t.currency.letter)

    def test_currency_set_alpha_dollar(self):

        self.t.currency = 'usd'  # 840

        self.assertIsNotNone(self.t.currency)
        self.assertEqual('840', self.t.currency.numeric)

    def test_currency_set_bytes_int_euro(self):

        self.t.currency = b'978'

        self.assertIsNotNone(self.t.currency)
        self.assertEqual('EUR', self.t.currency.letter)

    def test_currency_set_pycountry_dollar(self):

        self.t.currency = pycountry.currencies.get(numeric='840')

        self.assertIsNotNone(self.t.currency)
        self.assertEqual('USD', self.t.currency.letter)

    def test_short_name_none(self):
        self.assertIsNone(self.t.shortName)

    def test_short_name_set_bytes(self):
        value = b'John Smith'

        self.t.shortName = value

        self.assertEqual(value, self.t.shortName)

    def test_short_name_set_str(self):
        uvalue = 'John Smith'
        bvalue = b'John Smith'

        self.t.shortName = uvalue

        self.assertEqual(bvalue, self.t.shortName)

    def test_short_name_set_bytes_long(self):

        value = b'John Smith' * 10

        with self.assertRaises(utils.Csb43Exception):
            self.t.shortName = value

    def test_short_name_set_str_unicode(self):
        uvalue = "José Müller Muñiz Avinyò"
        bvalue = uvalue.encode(record.RecordSequence.ENCODING)

        self.t.shortName = uvalue

        self.assertEqual(bvalue, self.t.shortName)

    def test_short_name_set_bytes_latin1(self):
        uvalue = "José Müller Muñiz Avinyò"
        bvalue = uvalue.encode(record.RecordSequence.ENCODING)

        self.t.shortName = bvalue

        self.assertEqual(bvalue, self.t.shortName)

    def test_short_name_set_none(self):
        self.t.shortName = None

        self.assertEqual(b'', self.t.shortName)

    def test_account_number_none(self):
        self.assertIsNone(self.t.accountNumber)

    def test_account_number_set_bytes_int(self):
        value = b'0123456789'

        self.t.accountNumber = value
        self.assertEqual(value, self.t.accountNumber)

    def test_account_number_set_str_int(self):
        uvalue = '0123456789'
        bvalue = b'0123456789'

        self.t.accountNumber = uvalue
        self.assertEqual(bvalue, self.t.accountNumber)

    def test_account_number_set_bytes_alphanum(self):

        value = b'a123456789'

        with self.assertRaises(utils.Csb43Exception):
            self.t.accountNumber = value

    def test_account_number_set_str_alphanum(self):

        value = 'a123456789'

        with self.assertRaises(utils.Csb43Exception):
            self.t.accountNumber = value

    def test_account_number_set_bytes_short(self):

        value = b'0123467'

        with self.assertRaises(utils.Csb43Exception):
            self.t.accountNumber = value

    def test_bank_code_none(self):
        self.assertIsNone(self.t.bankCode)

    def test_bank_code_set_bytes_int(self):

        value = b'0123'

        self.t.bankCode = value
        self.assertEqual(value, self.t.bankCode)

    def test_bank_code_set_str_int(self):

        uvalue = '0123'
        bvalue = b'0123'

        self.t.bankCode = uvalue
        self.assertEqual(bvalue, self.t.bankCode)

    def test_bank_code_set_bytes_alphanum(self):

        value = b'a123'

        with self.assertRaises(utils.Csb43Exception):
            self.t.bankCode = value

    def test_bank_code_set_bytes_int_long(self):

        value = b'0123467'

        with self.assertRaises(utils.Csb43Exception):
            self.t.bankCode = value

    def test_branch_code_none(self):
        self.assertIsNone(self.t.branchCode)

    def test_branch_code_set_bytes_int(self):
        value = b'1234'

        self.t.branchCode = value
        self.assertEqual(value, self.t.branchCode)

    def test_branch_code_set_str_int(self):
        bvalue = b'1234'
        uvalue = '1234'

        self.t.branchCode = uvalue
        self.assertEqual(bvalue, self.t.branchCode)

    def test_branch_code_set_bytes_alphanum(self):

        value = b'123b'

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

    def test_information_mode_none(self):
        self.assertIsNone(self.t.informationMode)

    def test_information_mode_set_bytes(self):

        value = b'3'

        self.t.informationMode = value
        self.assertEqual(b'3', self.t.informationMode)

    def test_information_mode_set_str(self):

        value = '3'

        self.t.informationMode = value
        self.assertEqual(b'3', self.t.informationMode)

    def test_information_mode_set_bytes_blank(self):

        value = b' '

        self.t.informationMode = value
        self.assertEqual(b' ', self.t.informationMode)

    def test_information_mode_set_int(self):

        value = 3

        self.t.informationMode = value
        self.assertEqual(b'3', self.t.informationMode)

    def test_information_mode_set_bytes_alpha_short(self):

        value = b'a'

        with self.assertRaises(utils.Csb43Exception):
            self.t.informationMode = value

    def test_information_mode_set_bytes_int_long(self):

        value = b'12'

        with self.assertRaises(utils.Csb43Exception):
            self.t.informationMode = value

    def test_padding_none(self):
        self.assertIsNone(self.t.padding)

    def test_padding_set_bytes_long(self):

        value = b'sadl jasdf la'

        with self.assertRaises(utils.Csb43Exception):
            self.t.padding = value

    def test_padding_set_bytes(self):

        value = b' a '

        self.t.padding = value

        self.assertEqual(b' a', self.t.padding)

    def test_padding_set_str(self):

        value = ' a '

        self.t.padding = value

        self.assertEqual(b' a', self.t.padding)

    def test_bytes(self):

        self.test_iter()

        s = m3_bytes(self.t).split(b'\n')

        Account(s[0])
        Transaction(s[1])
        ClosingAccount(s[2])

    def test_iter(self):

        self.t.currency = 'EUR'
        self.t.bankCode = '0' * 4
        self.t.branchCode = '0' * 4
        self.t.accountNumber = '0' * 10
        self.t.initialBalance = 0

        self.test_add_transaction_bytes()

        l = [x for x in self.t]

        self.assertEqual(2, len(l))
        self.assertEqual(b'11', l[0][0:2])

        for x in l:
            self.assertEqual(80, len(x))

        Transaction(l[1])

        self.t.close_account()

        l = [x for x in self.t]

        self.assertEqual(3, len(l))
        self.assertEqual(b'11', l[0][0:2])

        for x in l:
            self.assertEqual(80, len(x))

        ClosingAccount(l[2])

    def test_add_item_bytes(self):

        self.test_add_transaction_bytes()

        i = Item()
        i.recordCode = 1
        i.item1 = 'a'
        i.item2 = 'b'

        record = m3_bytes(i)

        self.t.add_item(record)

        self.assertEqual(
            record,
            m3_bytes(self.t.get_last_transaction().optionalItems[-1])
        )

    def test_add_item_object(self):

        self.test_add_transaction_bytes()

        i = Item()
        i.recordCode = 1
        i.item1 = 'a'
        i.item2 = 'b'

        self.t.add_item(i)

        self.assertEqual(
            m3_bytes(i),
            m3_bytes(self.t.get_last_transaction().optionalItems[-1]))

    def test_add_exchange_bytes(self):

        self.test_add_transaction_bytes()

        e = Exchange()
        e.amount = 12345.5
        e.sourceCurrency = 'EUR'

        record = m3_bytes(e)

        self.t.add_exchange(record)

        exchange = self.t.get_last_transaction().exchange

        self.assertIsInstance(exchange, Exchange)

        self.assertEqual(record, m3_bytes(exchange))

    def test_add_exchange_object(self):

        self.test_add_transaction_object()

        e = Exchange()
        e.amount = 12345.5
        e.sourceCurrency = 'EUR'

        self.t.add_exchange(e)

        exchange = self.t.get_last_transaction().exchange

        self.assertIsInstance(exchange, Exchange)

        self.assertEqual(m3_bytes(e), m3_bytes(exchange))

    @staticmethod
    def _create_valid_transaction(strict=True):
        t = Transaction(strict=strict)
        t.branchCode = '0' * 4
        t.transactionDate = datetime.now()
        t.valueDate = datetime.now()
        t.commonItem = '00'
        t.ownItem = '000'
        t.amount = 123.00
        t.documentNumber = '0' * 10

        return t

    def test_add_transaction_bytes(self, ac=None, t=None):

        if not ac:
            ac = self.t
        if not t:
            t = self._create_valid_transaction()

        record = m3_bytes(t)

        ac.add_transaction(record)

        self.assertEqual(record, m3_bytes(ac.get_last_transaction()))

    def test_add_transaction_strict_false(self):
        ac = Account(strict=False)

        self.test_add_transaction_bytes(ac=ac)

        tr = ac.get_last_transaction()

        self.assertEqual(ac.strict_mode, tr.strict_mode)
        self.assertFalse(tr.strict_mode)

    def test_add_transaction_strict_true(self):
        ac = Account(strict=True)

        self.test_add_transaction_bytes(ac=ac)

        tr = ac.get_last_transaction()

        self.assertEqual(ac.strict_mode, tr.strict_mode)
        self.assertTrue(tr.strict_mode)

    def test_add_transaction_object(self):
        t = self._create_valid_transaction()

        self.t.add_transaction(t)

        self.assertEqual(m3_bytes(t), m3_bytes(self.t.get_last_transaction()))

    def test_transaction_information_mode_bytes(self):
        self.t.informationMode = 1

        self.test_add_transaction_bytes()

        record = self.t.get_last_transaction()

        self.assertEqual(record.informationMode, self.t.informationMode)

    def test_transaction_information_mode_object(self):
        self.t.informationMode = 1

        self.test_add_transaction_object()

        record = self.t.get_last_transaction()

        self.assertEqual(record.informationMode, self.t.informationMode)

    def test_account_key(self):
        values = [
            ('1234', '5678', '1234567890', b'06'),
            ('4321', '8755', '1234567891', b'50'),
            ('0001', '0000', '1000000000', b'11'),
            ('0000', '0000', '1000000000', b'01'),
            ('0000', '0000', '0000000000', b'00'),
            ('9972', '0347', '9674748288', b'45'),
            ('1274', '1866', '1455455527', b'68'),
        ]

        for bank, branch, number, key in values:
            self.t.bankCode = bank
            self.t.branchCode = branch
            self.t.accountNumber = number

            self.assertEqual(key, self.t.get_account_key())


class TestCsbClosingAccount(unittest.TestCase):
    '''ClosingAccount'''

    def setUp(self):
        self.t = ClosingAccount()

    def test_strict_default(self):
        self.assertTrue(self.t.strict_mode)

    def test_strict_true(self):
        t = ClosingAccount(strict=True)

        self.assertTrue(t.strict_mode)

    def test_strict_false(self):
        t = ClosingAccount(strict=False)

        self.assertFalse(t.strict_mode)

    def test_empty_as_dict(self):
        self.t.as_dict()

    def test_init_bad_length(self):
        record = b'33012380118008'

        with self.assertRaises(utils.Csb43Exception):
            ClosingAccount(record)

    def test_init_bad_code(self):
        record = b'34' + (b'1' * 55)
        record += b'0' * 23

        self.assertEqual(80, len(record))

        with self.assertRaises(utils.Csb43Exception):
            ClosingAccount(record)

    def test_init(self):
        record = b'33' + (b'1' * 78)

        ClosingAccount(record)

    def test_balance_none(self):

        self.assertIsNone(self.t.balance)

    def test_balance_set_bytes_int_long(self):

        value = b'12345' * 4

        with self.assertRaises(utils.Csb43Exception):
            self.t.balance = value

    def test_balance_set_bytes_int(self):

        value = b'12345'

        self.t.balance = value
        self.assertEqual(12345, self.t.balance)

    def test_balance_set_str_int(self):

        value = '12345'

        self.t.balance = value
        self.assertEqual(12345, self.t.balance)

    def test_balance_set_bytes_int_negative(self):

        value = b'-12345'

        self.t.balance = value
        self.assertEqual(-12345, self.t.balance)

    def test_balance_set_int(self):

        value = 123456

        self.t.balance = value
        self.assertEqual(123456, self.t.balance)

    def test_balance_set_int_negative(self):

        value = -123456

        self.t.balance = value
        self.assertEqual(-123456, self.t.balance)

    def test_balance_set_float_decimal_truncate(self):

        value = 123456.876

        self.t.balance = value
        self.assertEqual(123456.87, self.t.balance)

    def test_balance_set_bytes_invalid(self):

        value = b'asdagsa'

        with self.assertRaises(ValueError):
            self.t.balance = value

    def test_account_number_none(self):
        self.assertIsNone(self.t.accountNumber)

    def test_account_number_set_bytes_int(self):

        value = b'0123456789'

        self.t.accountNumber = value
        self.assertEqual(value, self.t.accountNumber)

    def test_account_number_set_str_int(self):

        bvalue = b'0123456789'
        uvalue = '0123456789'

        self.t.accountNumber = uvalue
        self.assertEqual(bvalue, self.t.accountNumber)

    def test_account_number_set_bytes_alphanum(self):

        value = 'a123456789'

        with self.assertRaises(utils.Csb43Exception):
            self.t.accountNumber = value

    def test_account_number_set_bytes_int_short(self):

        value = '0123467'

        with self.assertRaises(utils.Csb43Exception):
            self.t.accountNumber = value

    def test_bank_code_none(self):
        self.assertIsNone(self.t.bankCode)

    def test_bank_code_set_bytes_int(self):

        value = b'0123'

        self.t.bankCode = value
        self.assertEqual(value, self.t.bankCode)

    def test_bank_code_set_str_int(self):

        uvalue = '0123'
        bvalue = b'0123'

        self.t.bankCode = uvalue
        self.assertEqual(bvalue, self.t.bankCode)

    def test_bank_code_set_bytes_alphanum(self):

        value = b'a123'

        with self.assertRaises(utils.Csb43Exception):
            self.t.bankCode = value

    def test_bank_code_set_bytes_int_long(self):

        value = b'0123467'

        with self.assertRaises(utils.Csb43Exception):
            self.t.bankCode = value

    def test_branch_code_none(self):
        self.assertIsNone(self.t.branchCode)

    def test_branch_code_set_bytes_int(self):

        value = b'1234'

        self.t.branchCode = value
        self.assertEqual(value, self.t.branchCode)

    def test_branch_code_set_str_int(self):

        uvalue = '1234'
        bvalue = b'1234'

        self.t.branchCode = uvalue
        self.assertEqual(bvalue, self.t.branchCode)

    def test_branch_code_set_bytes_alphanum(self):

        value = b'123b'

        with self.assertRaises(utils.Csb43Exception):
            self.t.branchCode = value

    def test_branch_code_set_int(self):

        value = 1234

        self.t.branchCode = value

        self.assertEqual(b'1234', self.t.branchCode)

    def test_branch_code_set_bytes_int_short(self):

        value = b'123'

        with self.assertRaises(utils.Csb43Exception):
            self.t.branchCode = value

    def test_expense_entries_none(self):

        self.assertIsNone(self.t.expenseEntries)

    def test_expense_entries_set_bytes_int_long(self):

        value = b'12345' * 4

        with self.assertRaises(utils.Csb43Exception):
            self.t.expenseEntries = value

    def test_expense_entries_set_bytes_int(self):

        value = b'12345'

        self.t.expenseEntries = value
        self.assertEqual(12345, self.t.expenseEntries)

    def test_expense_entries_set_int(self):

        value = 1234

        self.t.expenseEntries = value
        self.assertEqual(1234, self.t.expenseEntries)

    def test_expense_entries_set_float(self):

        value = 123456.876

        with self.assertRaises(utils.Csb43Exception):
            self.t.expenseEntries = value

    def test_expense_entries_set_bytes_invalid(self):

        value = b'asdagsa'

        with self.assertRaises(utils.Csb43Exception):
            self.t.expenseEntries = value

    def test_expense_none(self):
        self.assertIsNone(self.t.expense)

    def test_expense_set_bytes_int_long(self):
        value = b'12345' * 4

        with self.assertRaises(utils.Csb43Exception):
            self.t.expense = value

    def test_expense_set_bytes_int(self):
        value = b'12345'

        self.t.expense = value
        self.assertEqual(12345, self.t.expense)

    def test_expense_set_bytes_int2(self):

        value = 123456

        self.t.expense = value
        self.assertEqual(123456, self.t.expense)

    def test_expense_set_float(self):

        value = 123456.876

        self.t.expense = value
        self.assertEqual(123456.87, self.t.expense)

    def test_expense_set_bytes_invalid(self):

        value = b'asdagsa'

        with self.assertRaises(ValueError):
            self.t.expense = value

    def test_income_entries_none(self):

        self.assertIsNone(self.t.incomeEntries)

        self.assertIsNone(self.t.incomeEntries)

    def test_income_entries_set_bytes_int_long(self):

        value = b'12345' * 4

        with self.assertRaises(utils.Csb43Exception):
            self.t.incomeEntries = value

    def test_income_entries_set_bytes_int(self):

        value = '12345'

        self.t.incomeEntries = value
        self.assertEqual(12345, self.t.incomeEntries)

    def test_income_entries_set_int(self):

        value = 1234

        self.t.incomeEntries = value
        self.assertEqual(1234, self.t.incomeEntries)

    def test_income_entries_set_float(self):
        value = 123456.876

        with self.assertRaises(utils.Csb43Exception):
            self.t.incomeEntries = value

    def test_income_entries_set_bytes_invalid(self):

        value = b'asdagsa'

        with self.assertRaises(utils.Csb43Exception):
            self.t.incomeEntries = value

    def test_income_none(self):
        self.assertIsNone(self.t.income)

    def test_income_set_bytes_int_long(self):

        value = b'12345' * 4

        with self.assertRaises(utils.Csb43Exception):
            self.t.income = value

    def test_income_set_bytes_int(self):

        value = b'12345'

        self.t.income = value
        self.assertEqual(12345, self.t.income)

    def test_income_set_bytes_int_char_size(self):

        value = b'1'

        self.t.income = value
        self.assertEqual(1, self.t.income)

    def test_income_set_int(self):

        value = 123456

        self.t.income = value
        self.assertEqual(123456, self.t.income)

    def test_income_set_float_decimal_truncate(self):

        value = 123456.876

        self.t.income = value
        self.assertEqual(123456.87, self.t.income)

    def test_income_set_bytes_invalid(self):

        value = 'asdagsa'

        with self.assertRaises(ValueError):
            self.t.income = value

    def test_currency_none(self):

        self.assertIsNone(self.t.currency)

    def test_currency_set_int_invalid(self):
        with self.assertRaises(utils.Csb43Exception):
            self.t.currency = 3

    def test_currency_set_bytes_invalid(self):
        with self.assertRaises(utils.Csb43Exception):
            self.t.currency = b'asdfalsjk'

    def test_currency_set_int_euro(self):
        self.t.currency = 978

        self.assertIsNotNone(self.t.currency)
        self.assertEqual('EUR', self.t.currency.letter)

    def test_currency_set_str_dollar(self):

        self.t.currency = 'usd'  # 840

        self.assertIsNotNone(self.t.currency)
        self.assertEqual('840', self.t.currency.numeric)

    def test_currency_set_int_str_euro(self):

        self.t.currency = '978'

        self.assertIsNotNone(self.t.currency)
        self.assertEqual('EUR', self.t.currency.letter)

    def test_currency_set_pycountry_dollar(self):

        self.t.currency = pycountry.currencies.get(numeric='840')

        self.assertIsNotNone(self.t.currency)
        self.assertEqual('USD', self.t.currency.letter)

    def test_padding_none(self):

        self.assertIsNone(self.t.padding)

    def test_padding_set_bytes_long(self):

        value = "asdga shfadsas"

        with self.assertRaises(utils.Csb43Exception):
            self.t.padding = value

    def test_padding_set_bytes(self):

        value = b" a c"

        self.t.padding = value

        self.assertEqual(value, self.t.padding)

    def test_padding_set_str(self):

        uvalue = " a c"
        bvalue = b" a c"

        self.t.padding = uvalue

        self.assertEqual(bvalue, self.t.padding)

    def test_padding_str_bytes_short(self):

        value = b"a "

        self.t.padding = value

        self.assertEqual(b"a", self.t.padding)

    def test_bytes(self):

        s = m3_bytes(self.t)

        #self.assertIsInstance(s, basestring)
        self.assertTrue(m3_is_string(s))
        self.assertEqual(len(s), 80)

        self.assertEqual(b'33', s[0:2])
