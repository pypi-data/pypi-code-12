# -*- coding: utf-8 -*-
u"""
Created on 2016-1-14

@author: cheng.li, weijun.shen, yuchen.lai
"""

import unittest
from DataAPI import api


@unittest.skip("Skip all the snapshot related tests since we have no access to this api")
class TestSnapshots(unittest.TestCase):

    def test_get_industry_net_cashflow_all(self):
        data = api.GetIndustryNetCashSnapshot()
        self.assertEqual(len(data), 75)

    def test_get_industry_net_cashflow_by_industry_id(self):
        data = api.GetIndustryNetCashSnapshot(industryID='j68')
        self.assertEqual(len(data), 1)

    def test_get_industry_net_cashflow_by_multi_industry_id(self):
        data = api.GetIndustryNetCashSnapshot(industryID=['j68', 'j66'])
        self.assertEqual(len(data), 2)

    def test_get_industry_net_cashflow_by_industry_name(self):
        data = api.GetIndustryNetCashSnapshot(industryName='保险业')
        self.assertEqual(len(data), 1)
