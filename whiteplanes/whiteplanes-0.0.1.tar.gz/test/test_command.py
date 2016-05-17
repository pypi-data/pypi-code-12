#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Tests for whiteplanes command. """
import unittest
from whiteplanes import Whiteplanes
from .context import Context

class TestCommand(unittest.TestCase):
    def setUp(self):
        self.context = Context()

    def process(self, *, code, expected):
        interpreter = Whiteplanes(code)
        interpreter.run(context=self.context)
        self.assertEqual(expected, self.context.stack.pop())

    def test_add(self):
        self.process(code="S S T\tT\tT\tT\tT\tN\nS S T\tT\tT\tT\tN\nT\tS S S ", expected=46)

    def test_sub(self):
        self.process(code="S S T\tT\tT\tT\tN\nS S T\tT\tT\tT\tT\tN\nT\tS S T\t", expected=16)

    def test_mul(self):
        self.process(code="S S T\tT\tT\tT\tT\tN\nS S T\tT\tT\tT\tN\nT\tS S N\n", expected=465)

    def test_div(self):
        self.process(code="S S T\tS N\nS S T\tT\tT\tS N\nT\tS T\tS ", expected=7)

    def test_mod(self):
        self.process(code="S S T\tT\tN\nS S T\tT\tT\tS N\nT\tS T\tT\t", expected=2)