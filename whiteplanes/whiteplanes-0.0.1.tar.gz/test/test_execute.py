#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Tests for whiteplanes executed. """
import io
import sys
import unittest
from whiteplanes import Whiteplanes
from .context import Context


########################################################################
# Execute Test
########################################################################
class ExecuteTest(unittest.TestCase):

    def setUp(self):
        self.capture = io.StringIO()
        sys.stdout = self.capture

    def process(self, *, filename, expected):
        filepath = './test/etc/' + filename + '.ws'
        with open(filepath) as f:
            code = f.read()
        interpreter = Whiteplanes(code)
        interpreter.run(context=Context())
        self.assertEqual(expected, self.capture.getvalue())

    def test_hello(self):
        self.process(filename='hello_world', expected='Hello World\n')

    def test_heapcontrol(self):
        self.process(filename='heap_control', expected='Hello World\n')

    def test_flow(self):
        self.process(filename='flow_control', expected='52')

    def test_count(self):
        self.process(filename='count', expected='1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n')

    def test_input(self):
        self.process(filename='input', expected='H72')
