
from __future__ import unicode_literals
from __future__ import absolute_import

import unittest

from ..csb43 import ClosingFile, File, Account, Transaction, Item, Exchange
from .. import utils
from ..utils.compat import (m3_bytes,
                            m3_is_string)


class TestFile(unittest.TestCase):

    def setUp(self):
        self.t = File()

    def test_strict_default(self):
        self.assertTrue(self.t.strict_mode)

    def test_strict_true(self):
        t = File(strict=True)

        self.assertTrue(t.strict_mode)

    def test_strict_false(self):
        t = File(strict=False)

        self.assertFalse(t.strict_mode)

    def test_empty_as_dict(self):
        self.t.as_dict()

    def test_init(self):
        self.assertEqual([], self.t.accounts)

    def test_get_last_account(self):

        with self.assertRaises(IndexError):
            self.t.get_last_account()

        self.test_add_account_bytes()

        self.assertIsInstance(self.t.get_last_account(), Account)

    def test_add_account_bytes(self, f=None):

        if not f:
            f = self.t

        a = Account()
        a.bankCode = b'0' * 4
        a.branchCode = b'0' * 4
        a.accountNumber = b'0' * 10
        a.initialBalance = 0

        record = m3_bytes(a)

        f.add_account(record)

        self.assertEqual(record, m3_bytes(f.get_last_account()))

    def test_add_account_bytes_strict_false(self):
        f = File(strict=False)

        self.test_add_account_bytes(f=f)

        ac = f.get_last_account()

        self.assertEqual(f.strict_mode, ac.strict_mode)
        self.assertFalse(ac.strict_mode)

    def test_add_account_bytes_strict_true(self):
        f = File(strict=True)

        self.test_add_account_bytes(f=f)

        ac = f.get_last_account()

        self.assertEqual(f.strict_mode, ac.strict_mode)
        self.assertTrue(ac.strict_mode)

    def test_add_account_object(self):

        a = Account()
        a.bankCode = b'0' * 4
        a.branchCode = b'0' * 4
        a.accountNumber = b'0' * 10
        a.initialBalance = 0

        self.t.add_account(a)

        self.assertEqual(m3_bytes(a), m3_bytes(self.t.get_last_account()))

    def test_add_transaction(self):

        t = Transaction()
        t.amount = 3

        with self.assertRaises(IndexError):
            self.t.add_transaction(t)

        self.test_add_account_bytes()

        self.t.add_transaction(t)

        self.assertIsInstance(self.t.get_last_account().get_last_transaction(),
                              Transaction)

        self.t.add_transaction(m3_bytes(t))

        self.assertIsInstance(self.t.get_last_account().get_last_transaction(),
                              Transaction)

    def test_add_item(self):

        i = Item()
        i.recordCode = 1

        with self.assertRaises(IndexError):
            self.t.add_item(i)

        self.test_add_transaction()

        self.t.add_item(i)

        t = self.t.get_last_account().get_last_transaction()

        self.assertIsInstance(t.optionalItems[-1], Item)

        self.t.add_item(m3_bytes(i))

        self.assertIsInstance(t.optionalItems[-1], Item)

    def test_add_exchange_object(self):

        e = Exchange()

        with self.assertRaises(IndexError):
            self.t.add_exchange(e)

        self.test_add_transaction()

        self.t.add_exchange(e)

        t = self.t.get_last_account().get_last_transaction()

        self.assertIsInstance(t.exchange, Exchange)

        with self.assertRaises(utils.Csb43Exception):
            self.t.add_exchange(e)

    def test_add_exchange2(self):

        e = Exchange()

        record = m3_bytes(e)

        with self.assertRaises(IndexError):
            self.t.add_exchange(record)

        self.test_add_transaction()

        self.t.add_exchange(record)

        t = self.t.get_last_account().get_last_transaction()

        self.assertIsInstance(t.exchange, Exchange)

        with self.assertRaises(utils.Csb43Exception):
            self.t.add_exchange(e)

    def test_close_file0(self):

        self.t.close_file()

    def test_close_file1(self):

        c = ClosingFile()
        c.totalRecords = 0

        self.t.close_file(m3_bytes(c))

        self.assertEqual(0, self.t.abstract.totalRecords)

        self.t.close_file(c)

        self.assertEqual(0, self.t.abstract.totalRecords)

        self.t.close_file()

        self.assertEqual(0, self.t.abstract.totalRecords)

    def test_close_file2(self):

        c = ClosingFile()
        c.totalRecords = 3  # 1ac + 2 trans

        self.test_add_transaction()

        self.t.close_file(m3_bytes(c))

        self.assertEqual(3, self.t.abstract.totalRecords)

    def test_close_file3(self):

        self.t.close_file()
        self.assertEqual(0, self.t.abstract.totalRecords)

        # +1 acc, +2 trans
        self.test_add_transaction()

        self.t.close_file()

        self.assertEqual(3, self.t.abstract.totalRecords)

    def test_close_file4(self):

        c = ClosingFile()
        c.totalRecords = 3

        self.test_add_transaction()

        self.t.close_file(m3_bytes(c))

    def test_iter(self):

        l = [x for x in self.t]

        self.assertEqual(1, len(l))

        ClosingFile(m3_bytes(l[0]))

        self.test_add_transaction()

        l = [x for x in self.t]

        self.assertEqual(4, len(l))

        Account(m3_bytes(l[0]))

        Transaction(m3_bytes(l[1]))

        Transaction(m3_bytes(l[2]))

        ClosingFile(m3_bytes(l[3]))

    def test_bytes(self):

        s = m3_bytes(self.t).split(b'\n')

        ClosingFile(s[0])

        self.test_add_transaction()

        s = m3_bytes(self.t).split(b'\n')

        for r in s:
            self.assertEqual(80, len(r))

        Account(s[0])

        Transaction(s[1])

        Transaction(s[2])

        ClosingFile(s[3])


class TestClosingFile(unittest.TestCase):

    def setUp(self):
        self.t = ClosingFile()

    def test_init(self):
        record = b'88' + b'9' * 18 + b'1' * 60

        ClosingFile(record)

    def test_init_bad_length(self):
        record = b'88' + b'9' * 18 + b'1' * 4

        with self.assertRaises(utils.Csb43Exception):
            ClosingFile(record)

    def test_init_bad_code(self):
        record = b'89' + b'9' * 18 + b'1' * 60

        with self.assertRaises(utils.Csb43Exception):
            ClosingFile(record)

    def test_total_records_none(self):
        self.assertIsNone(self.t.totalRecords)

    def test_total_records_set_int(self):

        value = 1234

        self.t.totalRecords = value
        self.assertEqual(1234, self.t.totalRecords)

    def test_total_records_set_bytes_int(self):

        value = b'1234'

        #self.t.totalRecords = value
        #self.assertEqual(1234, self.t.totalRecords)
        with self.assertRaises(utils.Csb43Exception):
            self.t.totalRecords = value

    def test_total_records_set_str_int(self):

        value = '1234'

        #self.t.totalRecords = value
        #self.assertEqual(1234, self.t.totalRecords)
        with self.assertRaises(utils.Csb43Exception):
            self.t.totalRecords = value

    def test_total_records_set_bytes_alphanum(self):

        value = b'a123'

        with self.assertRaises(utils.Csb43Exception):
            self.t.totalRecords = value

    def test_total_records_set_bytes_int_long(self):

        value = b'12345678'

        with self.assertRaises(utils.Csb43Exception):
            self.t.totalRecords = value

    def test_padding_none(self):
        self.assertIsNone(self.t.padding)

    def test_padding_set_bytes1(self):

        value = b' b '

        self.t.padding = value

        self.assertEqual(value.rstrip(b' '), self.t.padding)

    def test_padding_set_str1(self):

        value = ' b '

        self.t.padding = value

        self.assertEqual(b' b', self.t.padding)

    def test_padding_set_bytes_long(self):

        value = b' b ' * 18

        self.t.padding = value

        self.assertEqual(value.rstrip(b' '), self.t.padding)

    def test_padding_set_bytes_longer(self):

        value = b' b ' * 18 + b'c'

        with self.assertRaises(utils.Csb43Exception):
            self.t.padding = value

    def test_bytes(self):
        res = m3_bytes(self.t)

        #self.assertIsInstance(res, basestring)
        self.assertTrue(m3_is_string(res))

        self.assertEqual(80, len(res))
        self.assertEqual(b'88', res[0:2])
