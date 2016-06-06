#!/usr/bin/env python

import unittest
from philutils.pagination import get_display_pages, validate_input


class DisplayPagesTest(unittest.TestCase):
    def test_situation_1(self):
        result = get_display_pages(13, 7, 2)
        expected_result = [
            dict(type="link", page=1, is_current=False),
            dict(type="link", page=2, is_current=False),
            dict(type="link", page=3, is_current=False),
            dict(type="ellipsis"),
            dict(type="link", page=5, is_current=False),
            dict(type="link", page=6, is_current=False),
            dict(type="link", page=7, is_current=True),
            dict(type="link", page=8, is_current=False),
            dict(type="link", page=9, is_current=False),
            dict(type="ellipsis"),
            dict(type="link", page=11, is_current=False),
            dict(type="link", page=12, is_current=False),
            dict(type="link", page=13, is_current=False)]
        self.assertEqual(result, expected_result)

    def test_situation_2(self):
        result = get_display_pages(13, 4, 2)
        expected_result = [
            dict(type="link", page=1, is_current=False),
            dict(type="link", page=2, is_current=False),
            dict(type="link", page=3, is_current=False),
            dict(type="link", page=4, is_current=True),
            dict(type="link", page=5, is_current=False),
            dict(type="link", page=6, is_current=False),
            dict(type="ellipsis"),
            dict(type="link", page=11, is_current=False),
            dict(type="link", page=12, is_current=False),
            dict(type="link", page=13, is_current=False)]
        self.assertEqual(result, expected_result)

    def test_situation_3(self):
        result = get_display_pages(13, 10, 2)
        expected_result = [
            dict(type="link", page=1, is_current=False),
            dict(type="link", page=2, is_current=False),
            dict(type="link", page=3, is_current=False),
            dict(type="ellipsis"),
            dict(type="link", page=8, is_current=False),
            dict(type="link", page=9, is_current=False),
            dict(type="link", page=10, is_current=True),
            dict(type="link", page=11, is_current=False),
            dict(type="link", page=12, is_current=False),
            dict(type="link", page=13, is_current=False)]
        self.assertEqual(result, expected_result)

    def test_situation_4(self):
        result = get_display_pages(13, 7, 1)
        expected_result = [
            dict(type="link", page=1, is_current=False),
            dict(type="link", page=2, is_current=False),
            dict(type="ellipsis"),
            dict(type="link", page=6, is_current=False),
            dict(type="link", page=7, is_current=True),
            dict(type="link", page=8, is_current=False),
            dict(type="ellipsis"),
            dict(type="link", page=12, is_current=False),
            dict(type="link", page=13, is_current=False)]
        self.assertEqual(result, expected_result)

    def test_situation_6(self):
        result = get_display_pages(5, 3, 3)
        expected_result = [
            dict(type="link", page=1, is_current=False),
            dict(type="link", page=2, is_current=False),
            dict(type="link", page=3, is_current=True),
            dict(type="link", page=4, is_current=False),
            dict(type="link", page=5, is_current=False)]
        self.assertEqual(result, expected_result)

    def test_situation_7(self):
        args = ['moose', 5, 3]
        self.assertRaises(TypeError, get_display_pages, *args)

    def test_situation_8(self):
        args = [3, 'orange', 2]
        self.assertRaises(TypeError, get_display_pages, *args)

    def test_situation_9(self):
        args = [3, 12, 'blue']
        self.assertRaises(TypeError, get_display_pages, *args)

    def test_situation_10(self):
        args = [-3, 12, 4]
        self.assertRaises(ValueError, get_display_pages, *args)

    def test_situation_11(self):
        args = [3, -2, 4]
        self.assertRaises(ValueError, get_display_pages, *args)

    def test_situation_12(self):
        args = [3, 2, -4]
        self.assertRaises(ValueError, get_display_pages, *args)

    def test_situation_13(self):
        args = [3, 12, 4]
        self.assertRaises(ValueError, get_display_pages, *args)

    def test_situation_14(self):
        result = get_display_pages(23, 12, 4)
        expected_result = [
            dict(type="link", page=1, is_current=False),
            dict(type="link", page=2, is_current=False),
            dict(type="link", page=3, is_current=False),
            dict(type="link", page=4, is_current=False),
            dict(type="link", page=5, is_current=False),
            dict(type="ellipsis"),
            dict(type="link", page=8, is_current=False),
            dict(type="link", page=9, is_current=False),
            dict(type="link", page=10, is_current=False),
            dict(type="link", page=11, is_current=False),
            dict(type="link", page=12, is_current=True),
            dict(type="link", page=13, is_current=False),
            dict(type="link", page=14, is_current=False),
            dict(type="link", page=15, is_current=False),
            dict(type="link", page=16, is_current=False),
            dict(type="ellipsis"),
            dict(type="link", page=19, is_current=False),
            dict(type="link", page=20, is_current=False),
            dict(type="link", page=21, is_current=False),
            dict(type="link", page=22, is_current=False),
            dict(type="link", page=23, is_current=False)]
        self.assertEqual(result, expected_result)

    def test_situation_15(self):
        result = get_display_pages(23, 12, 0)
        expected_result = [
            dict(type="link", page=1, is_current=False),
            dict(type="ellipsis"),
            dict(type="link", page=12, is_current=True),
            dict(type="ellipsis"),
            dict(type="link", page=23, is_current=False)]
        self.assertEqual(result, expected_result)

    def test_situation_16(self):
        result = get_display_pages(23, 1, 0)
        expected_result = [
            dict(type="link", page=1, is_current=True),
            dict(type="ellipsis"),
            dict(type="link", page=23, is_current=False)]
        self.assertEqual(result, expected_result)
