# -*- coding: utf-8 -*-
u"""
Created on 2016-2-16

@author: cheng.li
"""

import unittest
import numpy as np
from DataAPI.api import GetCommodityStocksInfo


class TestCommodity(unittest.TestCase):

    def test_commodity_stocks_by_specific_product_id(self):
        data = GetCommodityStocksInfo('CU', '2015-01-01', '2016-01-01', forceUpdate=True)
        self.assertTrue(len(data) > 0)
        self.assertTrue(np.all(data.productID == u'CU'))

    def test_commodity_stock_by_several_product_ids(self):
        data = GetCommodityStocksInfo(['CU', 'A'], '2015-01-01', '2016-01-01', forceUpdate=True)
        self.assertTrue(len(data) > 0)
        grouped = data.groupby('productID')
        for _, group in grouped:
            self.assertTrue(len(group) > 0)

    def test_commodity_stock_by_specific_ware_house(self):
        data = GetCommodityStocksInfo('CU', '2015-01-01', '2016-01-01', wareHouse=u'江苏:中储无锡', forceUpdate=True)
        self.assertTrue(len(data) > 0)
        self.assertTrue(np.all(data.wareHouse == u'江苏:中储无锡'))
