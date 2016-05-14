# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from unittest import TestCase

from rattail import config


class TestParseList(TestCase):

    def test_none(self):
        value = config.parse_list(None)
        self.assertEqual(len(value), 0)

    def test_single_value(self):
        value = config.parse_list(u'foo')
        self.assertEqual(len(value), 1)
        self.assertEqual(value[0], u'foo')

    def test_single_value_padded_by_spaces(self):
        value = config.parse_list(u'   foo   ')
        self.assertEqual(len(value), 1)
        self.assertEqual(value[0], u'foo')

    def test_slash_is_not_a_separator(self):
        value = config.parse_list(u'/dev/null')
        self.assertEqual(len(value), 1)
        self.assertEqual(value[0], u'/dev/null')

    def test_multiple_values_separated_by_whitespace(self):
        value = config.parse_list(u'foo bar baz')
        self.assertEqual(len(value), 3)
        self.assertEqual(value[0], u'foo')
        self.assertEqual(value[1], u'bar')
        self.assertEqual(value[2], u'baz')

    def test_multiple_values_separated_by_commas(self):
        value = config.parse_list(u'foo,bar,baz')
        self.assertEqual(len(value), 3)
        self.assertEqual(value[0], u'foo')
        self.assertEqual(value[1], u'bar')
        self.assertEqual(value[2], u'baz')

    def test_multiple_values_separated_by_whitespace_and_commas(self):
        value = config.parse_list(u'  foo,   bar   baz')
        self.assertEqual(len(value), 3)
        self.assertEqual(value[0], u'foo')
        self.assertEqual(value[1], u'bar')
        self.assertEqual(value[2], u'baz')

    def test_multiple_values_separated_by_whitespace_and_commas_with_some_quoting(self):
        value = config.parse_list(u"""
        foo
        "C:\\some path\\with spaces\\and, a comma",
        baz
""")
        self.assertEqual(len(value), 3)
        self.assertEqual(value[0], u'foo')
        self.assertEqual(value[1], u'C:\\some path\\with spaces\\and, a comma')
        self.assertEqual(value[2], u'baz')
