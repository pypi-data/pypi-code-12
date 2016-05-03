# -*- coding: utf-8 -*-
u"""
Created on 2016-1-5

@author: cheng.li
"""

import unittest
from DataAPI.SqlExpressions import Condition


class TestSqlExpressions(unittest.TestCase):

    def test_single_condition(self):
        condition = Condition('A', 1, '=')
        self.assertEqual(str(condition), '(A = 1)')

    def test_and_statement(self):
        condition1 = Condition('A', 1, '=')
        condition2 = Condition('B', "'s', 'b'", 'in')

        all_condtion = condition1 & condition2
        self.assertEqual(str(all_condtion), "((A = 1) and (B in ('s', 'b')))")

    def test_or_statement(self):
        condition1 = Condition('A', 1, '=')
        condition2 = Condition('B', "'s', 'b'", 'in')

        all_condtion = condition1 | condition2
        self.assertEqual(str(all_condtion), "((A = 1) or (B in ('s', 'b')))")
