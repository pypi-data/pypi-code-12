#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_urler
----------------------------------

Tests for `urler` module.
"""

import urler
import unittest
import mock


class TestUrler(unittest.TestCase):

    @mock.patch('__builtin__.open', create=True)
    def test_load_csv_file(self, mock_open):
        mock_open.side_effect = [
            mock.mock_open(read_data='localhost,8080,test1').return_value,
            mock.mock_open(read_data='localhost,8080,test2').return_value,
            mock.mock_open(read_data='localhost,8080,test2').return_value,
        ]
        self.assertEqual('localhost,8080,test1', urler.load_csv_file("file1.csv")[0])
        mock_open.assert_called_once_with('file1.csv', 'r')
        mock_open.reset_mock()

        self.assertEqual('localhost,8080,test2', urler.load_csv_file("file2.csv")[0])
        mock_open.assert_called_once_with('file2.csv', 'r')
        mock_open.reset_mock()

        with self.assertRaises(IndexError):
            urler.load_csv_file('file3.csv')[1]

        # could be done with a `with` statement
        self.assertRaises(SystemExit, lambda: urler.load_csv_file('file4.csv')[0])

    def test_create_target(self):
        csv = 'localhost,8080,test'
        target = 'localhost:8080/test'
        self.assertEqual(target, urler.create_target(csv))

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
