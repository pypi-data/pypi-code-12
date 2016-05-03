# -*- coding: utf-8 -*-
u"""
Created on 2015-11-12

@author: cheng.li, weijun.shen
"""

import unittest
import pandas as pd
from DataAPI import api


class TestFuture(unittest.TestCase):

    @unittest.skip("currently FUTURE 1min bar data is not available")
    def test_future_bar_1_min(self):
        data = api.GetFutureBarMin1('ZN1501', '2015-01-01', '2015-01-31', forceUpdate=True)
        self.assertTrue(isinstance(data, pd.DataFrame))
        self.assertTrue(len(data) > 0)

    @unittest.skip("currently FUTURE 1min bar data is not available")
    def test_future_bar_1_min_in_chunk(self):
        datas = api.GetFutureBarMin1('ZN1501', '2015-01-01', '2015-01-31', chunksize=10, forceUpdate=True)
        for data in datas:
            self.assertTrue(isinstance(data, pd.DataFrame))
            self.assertTrue(len(data) > 0)

    def test_future_bar_5_min(self):
        data = api.GetFutureBarMin5(['IF1502'], '2010-10-01', '2015-10-01', forceUpdate=True)
        self.assertTrue(isinstance(data, pd.DataFrame))
        self.assertTrue(len(data) > 0)

    def test_future_bar_5_min_in_chunk(self):
        datas = api.GetFutureBarMin5(['IF1502'], '2010-10-01', '2015-10-01', chunksize=10, forceUpdate=True)
        for data in datas:
            self.assertTrue(isinstance(data, pd.DataFrame))
            self.assertTrue(len(data) > 0)

    def test_future_bar_eod(self):
        data = api.GetFutureBarEOD(['IF1502'], '2015-01-01', '2015-01-31', field=['closePrice'], forceUpdate=True)
        self.assertTrue(isinstance(data, pd.DataFrame))
        self.assertTrue(len(data) > 0)

    def test_future_bar_eod_in_chunk(self):
        datas = api.GetFutureBarEOD(['IF1502'], '2015-01-01', '2015-01-31', field=['closePrice'], chunksize=10, forceUpdate=True)
        for data in datas:
            self.assertTrue(isinstance(data, pd.DataFrame))
            self.assertTrue(len(data) > 0)

    def test_future_bar_eod_continuing(self):
        data = api.GetFutureBarEODContinuing(['IF'], '2015-01-01', '2015-01-31', field=['closePrice'], forceUpdate=True)
        self.assertTrue(isinstance(data, pd.DataFrame))
        self.assertTrue(len(data) > 0)

    def test_future_bar_eod_continuing_in_chunk(self):
        datas = api.GetFutureBarEODContinuing(['IF'], '2015-01-01', '2015-01-31', field=['closePrice'], chunksize=10, forceUpdate=True)
        for data in datas:
            self.assertTrue(isinstance(data, pd.DataFrame))
            self.assertTrue(len(data) > 0)

    def test_future_bar_5_min_continuing(self):
        data = api.GetFutureBarMin5Continuing(['IF'], '2010-10-01', '2015-10-01', forceUpdate=True)
        self.assertTrue(isinstance(data, pd.DataFrame))
        self.assertTrue(len(data) > 0)

    def test_future_bar_5_min_continuing_in_chunk(self):
        datas = api.GetFutureBarMin5Continuing(['IF'], '2010-10-01', '2015-10-01', chunksize=10, forceUpdate=True)
        for data in datas:
            self.assertTrue(isinstance(data, pd.DataFrame))
            self.assertTrue(len(data) > 0)


