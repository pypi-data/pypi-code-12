# -*- coding: utf-8 -*-
u"""
Created on 2015-11-13

@author: cheng.li, weijun.shen
"""

import os
import sys

thisFilePath = os.path.abspath(__file__)
sys.path.append(os.path.sep.join(thisFilePath.split(os.path.sep)[:-3]))

import unittest
from DataAPI.tests.testEquity import TestEquity
from DataAPI.tests.testIndex import TestIndex
from DataAPI.tests.testFuture import TestFuture
from DataAPI.tests.testCommodity import TestCommodity
from DataAPI.tests.testGeneral import TestGeneral
from DataAPI.tests.testInstrumentInfo import TestInstrumentInfo
from DataAPI.tests.testSqlExpressions import TestSqlExpressions
from DataAPI.tests.testHedgeFund import TestHedgeFund
from DataAPI.tests.testThemes import TestThemes
from DataAPI.tests.testSnapshots import TestSnapshots
from DataAPI.tests.testMutualFund import TestMutualFund


def test():
    print("Python " + sys.version)
    suite = unittest.TestSuite()

    tests = unittest.TestLoader().loadTestsFromTestCase(TestEquity)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(TestIndex)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(TestFuture)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(TestCommodity)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(TestGeneral)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(TestInstrumentInfo)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(TestSqlExpressions)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(TestHedgeFund)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(TestThemes)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(TestSnapshots)
    suite.addTests(tests)
    tests = unittest.TestLoader().loadTestsFromTestCase(TestMutualFund)
    suite.addTests(tests)

    res = unittest.TextTestRunner(verbosity=3).run(suite)
    if len(res.errors) >= 1 or len(res.failures) >= 1:
        sys.exit(-1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    test()
