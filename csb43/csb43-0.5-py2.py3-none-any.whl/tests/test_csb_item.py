# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

import unittest

from ..csb43 import (item,
                     record)
from .. import utils
from ..utils.compat import (m3_bytes,
                            m3_unicode)


class TestCsbItem(unittest.TestCase):

    def setUp(self):
        self.item = item.Item()

    def test_init(self):

        item.Item()

    def test_strict_default(self):
        self.assertTrue(self.item.strict_mode)

    def test_strict_true(self):
        it = item.Item(strict=True)

        self.assertTrue(it.strict_mode)

    def test_strict_false(self):
        it = item.Item(strict=False)

        self.assertFalse(it.strict_mode)

    def test_empty_as_dict(self):
        self.item.as_dict()

    def test_init_bad_length(self):

        record = '230001230405'

        with self.assertRaises(utils.Csb43Exception):
            item.Item(record)

    def test_init_bad_code(self):

        record = '22' + '0' * 78

        with self.assertRaises(utils.Csb43Exception):
            item.Item(record)

    def test_init_bad_record_code_int1(self):

        record = '2306' + '0' * 76

        with self.assertRaises(utils.Csb43Exception):
            item.Item(record)

    def test_init_bad_record_code_int2(self):

        record = '2315' + '0' * 76

        with self.assertRaises(utils.Csb43Exception):
            item.Item(record)

    def test_init_good_record_code(self):

        record = '2305' + '0' * 76

        it = item.Item(record)

        self.assertEqual(it.recordCode, 5)

    def test_record_code_none(self):

        self.assertIsNone(self.item.recordCode)

    def test_record_code_set_none(self):

        with self.assertRaises(TypeError):
            self.item.recordCode = None

    def test_record_code_set_high_int(self):

        with self.assertRaises(utils.Csb43Exception):
            self.item.recordCode = 23

    def test_record_code_set_high_bytes(self):

        with self.assertRaises(utils.Csb43Exception):
            self.item.recordCode = b'23'

    def test_record_code_set_high_str(self):

        with self.assertRaises(utils.Csb43Exception):
            self.item.recordCode = '23'

    def test_record_code_set_int(self):

        self.item.recordCode = 5

        self.assertEqual(5, self.item.recordCode)

    def test_record_code_set_bytes(self):

        self.item.recordCode = b'05'

        self.assertEqual(5, self.item.recordCode)

    def test_record_code_set_str(self):

        self.item.recordCode = '05'

        self.assertEqual(5, self.item.recordCode)

    def test_item1_none(self):

        self.assertIsNone(self.item.item1)

    def test_item1_set_none(self):

        self.item.item1 = None

        self.assertEqual(b'', self.item.item1)

    def test_item1_set_num(self):
        value = 15
        self.item.item1 = value

        self.assertEqual(b"15", self.item.item1)

    def test_item1_set_bytes_num(self):
        value = b'1235677744'
        self.item.item1 = value

        self.assertEqual(value, self.item.item1)

    def test_item1_set_str_num(self):
        bvalue = b'1235677744'
        svalue = '1235677744'
        self.item.item1 = svalue

        self.assertEqual(bvalue, self.item.item1)

    def test_item1_set_bytes_alphnum(self):

        value = b'0123456789ABCDEF G ' * 2
        self.item.item1 = value

        self.assertEqual(value.rstrip(b' '), self.item.item1)

    def test_item1_set_str_alphnum(self):

        bvalue = b'0123456789ABCDEF G ' * 2
        svalue = '0123456789ABCDEF G ' * 2
        self.item.item1 = svalue

        self.assertEqual(bvalue.rstrip(b' '), self.item.item1)

    def test_item1_set_bytes_latin1(self):

        uvalue = 'áéóüñç'
        bvalue = uvalue.encode(record.RecordSequence.ENCODING)
        self.item.item1 = bvalue

        self.assertEqual(bvalue, self.item.item1)

    def test_item1_set_str_latin1(self):

        uvalue = 'áéóüñç'
        bvalue = uvalue.encode(record.RecordSequence.ENCODING)
        self.item.item1 = uvalue

        self.assertEqual(bvalue, self.item.item1)

    def test_item2_none(self):

        self.assertIsNone(self.item.item2)

    def test_item2_set_none(self):

        self.item.item2 = None

        self.assertEqual(b'', self.item.item2)

    def test_item2_set_num(self):
        bvalue = b"15"
        value = 15
        self.item.item2 = value

        self.assertEqual(bvalue, self.item.item2)

    def test_item2_set_bytes_num(self):
        value = b'1235677744'
        self.item.item2 = value

        self.assertEqual(value, self.item.item2)

    def test_item2_set_str_num(self):
        bvalue = b'1235677744'
        svalue = '1235677744'
        self.item.item2 = svalue

        self.assertEqual(bvalue, self.item.item2)

    def test_item2_set_bytes_alphnum(self):

        value = b'0123456789ABCDEF G ' * 2
        self.item.item2 = value

        self.assertEqual(value.rstrip(b' '), self.item.item2)

    def test_item2_set_str_alphnum(self):

        bvalue = b'0123456789ABCDEF G ' * 2
        svalue = '0123456789ABCDEF G ' * 2
        self.item.item2 = svalue

        self.assertEqual(bvalue.rstrip(b' '), self.item.item2)

    def test_item2_set_bytes_latin1(self):

        uvalue = 'áéóüñç'
        bvalue = uvalue.encode(record.RecordSequence.ENCODING)
        self.item.item2 = bvalue

        self.assertEqual(bvalue, self.item.item2)

    def test_item2_set_str_latin1(self):

        uvalue = 'áéóüñç'
        bvalue = uvalue.encode(record.RecordSequence.ENCODING)
        self.item.item2 = uvalue

        self.assertEqual(bvalue, self.item.item2)

    def test_bytes_empty(self):

        s = m3_bytes(self.item)

        self.assertEqual(s, b'2300' + b' ' * 76)

    def test_str_empty(self):

        s = m3_unicode(self.item)

        self.assertEqual(s, '2300' + ' ' * 76)

    def test_bytes1(self):

        s = m3_bytes(self.item)

        self.assertEqual(80, len(s))

        self.assertEqual(b'23', s[0:2])

    def test_bytes2(self):

        self.item.item1 = 'algo uno dos 1'
        self.item.item2 = 'dos 1 uno algo'
        self.item.recordCode = '05'

        s = m3_bytes(self.item)

        e = item.Item(s, strict=True)

        self.assertEqual(self.item.item1, e.item1)
        self.assertEqual(self.item.item2, e.item2)
        self.assertEqual(self.item.recordCode, e.recordCode)

        self.assertEqual(s, m3_bytes(e))

    def test_iter(self):

        self.test_bytes2()

        r = [x for x in self.item]

        self.assertEqual(1, len(r))

        self.assertEqual(m3_bytes(self.item), r[0])
