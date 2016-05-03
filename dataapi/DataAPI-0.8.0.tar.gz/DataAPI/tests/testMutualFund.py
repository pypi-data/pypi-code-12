# -*- coding: utf-8 -*-
u"""
Created on 2016-1-21

@author: cheng.li, weijun.shen
"""

import unittest
from DataAPI import api


class TestMutualFund(unittest.TestCase):

    def test_get_mutual_fund_min5_bar(self):
        data = api.GetMutualFundBarMin5('150019', '2012-01-01', '2016-01-01')
        self.assertTrue(len(data) > 1)

    def test_get_mutual_fund_min5_bar_with_several_symbols(self):
        data = api.GetMutualFundBarMin5(['150019', '518880'], '2012-01-01', '2016-01-01')
        self.assertTrue(len(data.instrumentID.unique()) == 2)

    def test_get_mutual_fund_min5_bar_with_field(self):
        data = api.GetMutualFundBarMin5('150019', '2012-01-01', '2016-01-01', field=['openPrice'])
        self.assertTrue('openPrice' in data)
        self.assertTrue('highPrice' not in data)