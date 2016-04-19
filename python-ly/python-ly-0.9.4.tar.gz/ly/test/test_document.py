#!/usr/bin/env python

import unittest

import ly.document


class TestDocument(unittest.TestCase):
    def setUp(self):
        self.d = ly.document.Document("abcde")


class TestEditStart(TestDocument):
    def runTest(self):
        with self.d as d:
            d[0] = "A"
        self.assertEqual(d.plaintext(), "Abcde")


class TestEditEnd(TestDocument):
    def runTest(self):
        with self.d as d:
            d[-1] = "E"
        self.assertEqual(d.plaintext(), "abcdE")


