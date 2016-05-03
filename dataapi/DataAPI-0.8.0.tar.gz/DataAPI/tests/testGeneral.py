# -*- coding: utf-8 -*-
u"""
Created on 2015-12-11

@author: cheng.li, weijun.shen
"""

import unittest
import pandas as pd
import numpy as np
from DataAPI import api


class TestGeneral(unittest.TestCase):
    def test_general_bar(self):
        symbols = ['600000.xshg', 'if1512.CFFEX', '000300.zicn']
        allData = api.GetGeneralBarData(symbols,
                                        '2015-01-01',
                                        '2015-12-12',
                                        api.BAR_TYPE.EOD)

        self.assertTrue(isinstance(allData, pd.DataFrame))
        self.assertTrue(len(allData) > 0)

        groups = allData.groupby('instrumentID')

        self.assertEqual(len(groups), 3)

        for _, data in groups:
            self.assertTrue(len(data) > 0)

    def test_general_bar_in_chunk(self):
        symbols = ['600000.xshg', 'if1512.CFFEX', '000300.zicn']
        allData = api.GetGeneralBarData(symbols,
                                        '2015-01-01',
                                        '2015-12-12',
                                        api.BAR_TYPE.EOD,
                                        "*",
                                        10)

        testSymbols = [s[:6] for s in symbols]
        for data in allData:
            s = data.instrumentID.unique()[0]
            s = s.lower()
            if s in testSymbols:
                testSymbols.remove(s)
            self.assertTrue(len(data) > 0)

        self.assertFalse(testSymbols)

    def test_general_with_no_data_symbol(self):

        # IF1512 is not traded during Jan 2015
        symbols = ['600000.xshg', 'if1512.CFFEX', '000300.zicn']
        allData = api.GetGeneralBarData(symbols,
                                        '2015-01-01',
                                        '2015-01-31',
                                        api.BAR_TYPE.EOD)

        self.assertTrue(isinstance(allData, pd.DataFrame))
        self.assertTrue(len(allData) > 0)

        groups = allData.groupby('instrumentID')

        self.assertEqual(len(groups), 2)

        for _, data in groups:
            self.assertTrue(len(data) > 0)

    def test_general_with_instrumentIDasClo_as_true(self):
        symbols = ['600000.xshg', 'if1512.CFFEX', '000300.zicn']
        allData = api.GetGeneralBarData(symbols,
                                        '2015-01-01',
                                        '2015-12-12',
                                        api.BAR_TYPE.EOD,
                                        field=['closePrice'],
                                        instrumentIDasCol=True)

        plainAllData = api.GetGeneralBarData(symbols,
                                             '2015-01-01',
                                             '2015-12-12',
                                             api.BAR_TYPE.EOD,
                                             field=['closePrice'])

        instruments = allData.columns.get_level_values(level=1)
        groups = plainAllData.groupby('instrumentID')

        for s in instruments:
            series = allData['closePrice'][s].dropna()
            series2 = groups.get_group(s)['closePrice']
            self.assertTrue(sum(np.abs(series - series2)) < 1e-12)

    def test_general_with_incompleted_instrument_ids(self):
        symbols = ['600000.xshg', 'if1512', '000300.zicn']
        with self.assertRaises(ValueError):
            _ = api.GetGeneralBarData(symbols,
                                      '2015-01-01',
                                      '2015-12-12',
                                      api.BAR_TYPE.EOD,
                                      field=['closePrice'],
                                      instrumentIDasCol=True)