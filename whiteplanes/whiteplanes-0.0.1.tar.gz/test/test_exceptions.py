#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Tests for whiteplanes exceptions. """
import unittest
from whiteplanes import Whiteplanes
from exceptions import SyntaxError


########################################################################
# Execute Test
########################################################################
class ExceptionsTest(unittest.TestCase):

    def test_exception(self):
        for code in ["S ", "T\t", "S S T\tT\t", "S T\tT\t", "T\tS T\tN\n",
            "T\tS N\n", "T\tT\tN\n", "N\nN\nS ", "N\nN\nT\t", "T\tN\nS N\n", 
            "T\tN\nT\tN\n", "T\tN\nN\n"]:
            with self.assertRaises(SyntaxError):
                interpreter = Whiteplanes(code)