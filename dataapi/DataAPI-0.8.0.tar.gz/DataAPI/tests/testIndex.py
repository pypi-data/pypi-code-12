# -*- coding: utf-8 -*-
u"""
Created on 2015-11-10

@author: cheng.li, weijun.shen
"""

import unittest
import pandas as pd
from DataAPI import api


class TestIndex(unittest.TestCase):

    def test_index_bar_1_min(self):
        data = api.GetIndexBarMin1('000300.zicn', '2015-01-01', '2015-01-31', forceUpdate=True)
        self.assertTrue(isinstance(data, pd.DataFrame))
        self.assertTrue(len(data) > 0)

    def test_index_with_transformed_instrument_id(self):
        data1 = api.GetIndexBarMin5('000905', '2015-01-01', '2015-01-31', forceUpdate=True)
        data2 = api.GetIndexBarMin5('990905', '2015-01-01', '2015-01-31', forceUpdate=True)
        self.assertTrue(data1.equals(data2))

    def test_index_with_transformed_instrument_id_type2(self):
        data1 = api.GetIndexBarMin5('000001', '2015-01-01', '2015-01-31', forceUpdate=True)
        data2 = api.GetIndexBarMin5('999999', '2015-01-01', '2015-01-31', forceUpdate=True)
        self.assertTrue(data1.equals(data2))

    def test_index_bar_1_min_in_chunk(self):
        datas = api.GetIndexBarMin1('000300', '2015-01-01', '2015-01-31', chunksize=10, forceUpdate=True)
        for data in datas:
            self.assertTrue(isinstance(data, pd.DataFrame))
            self.assertTrue(len(data) > 0)

    def test_index_bar_5_min(self):
        data = api.GetIndexBarMin5(['000300'], '2015-01-01', '2015-01-31', forceUpdate=True)
        self.assertTrue(isinstance(data, pd.DataFrame))
        self.assertTrue(len(data) > 0)

    def test_index_bar_5_min_in_chunk(self):
        datas = api.GetIndexBarMin5(['000300'], '2015-01-01', '2015-01-31', chunksize=10, forceUpdate=True)
        for data in datas:
            self.assertTrue(isinstance(data, pd.DataFrame))
            self.assertTrue(len(data) > 0)

    def test_index_bar_eod(self):
        data = api.GetIndexBarEOD(['000300'], '2015-01-01', '2015-01-31', field=['closePrice'], forceUpdate=True)
        self.assertTrue(isinstance(data, pd.DataFrame))
        self.assertTrue(len(data) > 0)

    def test_index_bar_eod_in_chunk(self):
        datas = api.GetIndexBarEOD(['000300'], '2015-01-01', '2015-01-31', field=['closePrice'], chunksize=10, forceUpdate=True)
        for data in datas:
            self.assertTrue(isinstance(data, pd.DataFrame))
            self.assertTrue(len(data) > 0)

    def test_index_constitution(self):
        data = api.GetIndexConstitutionInfo('000300', refDate='2013-12-31')
        self.assertEqual(len(data), 300)
