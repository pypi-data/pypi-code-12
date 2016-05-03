#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
from .testcase import TestCase

from pdml2flow.utils import *

class TestUtils(TestCase):

    def test_boolify(self):
        self.assertEqual(True, boolify('True'))
        self.assertEqual(False, boolify('False'))
        self.assertRaises(ValueError, boolify, 'Something but not a bool')

    def test_autoconvert(self):
        self.assertEqual(True, autoconvert('True'))
        self.assertEqual(False, autoconvert('False'))
        self.assertEqual(0, autoconvert('0'))
        self.assertEqual(123, autoconvert('123'))
        self.assertEqual(-123, autoconvert('-123'))
        self.assertEqual(0.5, autoconvert('0.5'))
        self.assertEqual(-0.5, autoconvert('-0.5'))
        self.assertEqual('Can not convert', autoconvert('Can not convert'))

if __name__ == '__main__':
    unittest.main()
