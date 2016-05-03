# -*- coding: utf-8 -*-
u"""
Created on 2015-11-10

@author: cheng.li, weijun.shen
"""

import unittest
import pandas as pd
import DataAPI.api as api


class TestEquity(unittest.TestCase):

    def test_equity_bar_1_min(self):
        data = api.GetEquityBarMin1('600000', '2016-01-01', '2016-01-31', forceUpdate=True)
        self.assertTrue(isinstance(data, pd.DataFrame))
        self.assertTrue(len(data) > 0)

    def test_equity_bar_1_min_in_chunk(self):
        datas = api.GetEquityBarMin1('600000', '2016-01-01', '2016-01-31', chunksize=10, forceUpdate=True)
        for data in datas:
            self.assertTrue(isinstance(data, pd.DataFrame))
            self.assertTrue(len(data) > 0)

    def test_equity_bar_5_min(self):
        data = api.GetEquityBarMin5(['600000'], '2015-01-01', '2015-01-31', forceUpdate=True)
        self.assertTrue(isinstance(data, pd.DataFrame))
        self.assertTrue(len(data) > 0)

    def test_equity_bar_5_min_in_chunk(self):
        datas = api.GetEquityBarMin5(['600000'], '2015-01-01', '2015-01-31', chunksize=10, forceUpdate=True)
        for data in datas:
            self.assertTrue(isinstance(data, pd.DataFrame))
            self.assertTrue(len(data) > 0)

    def test_equity_bar_eod(self):
        data = api.GetEquityBarEOD(['600000'], '2015-01-01', '2015-01-31', field=['closePrice'], forceUpdate=True)
        self.assertTrue(isinstance(data, pd.DataFrame))
        self.assertTrue(len(data) > 0)

    def test_equity_bar_eod_in_chunk(self):
        datas = api.GetEquityBarEOD(['600000'], '2015-01-01', '2015-01-31', field=['closePrice'],  chunksize=10, forceUpdate=True)
        for data in datas:
            self.assertTrue(isinstance(data, pd.DataFrame))
            self.assertTrue(len(data) > 0)

    def _test_base_date_template(self, api_for_test, base_date):

        datas = api_for_test('600000',
                             '2016-01-04',
                             '2016-01-29',
                             field=['closePrice'],
                             baseDate=base_date,
                             forceUpdate=True)
        chunkDatas = api_for_test('600000',
                                  '2016-01-04',
                                  '2016-01-29',
                                  field=['closePrice'],
                                  chunksize=100,
                                  baseDate=base_date,
                                  forceUpdate=True)

        lineCount = 0

        for chunk in chunkDatas:
            for row in chunk.iterrows():
                try:
                    self.assertAlmostEqual(datas['closePrice'][lineCount], row[1]['closePrice'], 12)
                except:
                    print(datas.ix[lineCount], row[1])
                lineCount += 1

    def test_equity_bar_eod_with_base_date_end(self):
        api_for_test = api.GetEquityBarEOD
        base_date = 'end'
        self._test_base_date_template(api_for_test, base_date)

    def test_equity_bar_min5_with_base_date_end(self):
        api_for_test = api.GetEquityBarMin5
        base_date = 'end'
        self._test_base_date_template(api_for_test, base_date)

    def test_equity_bar_min1_with_base_date_end(self):
        api_for_test = api.GetEquityBarMin1
        base_date = 'end'
        self._test_base_date_template(api_for_test, base_date)

    def test_equity_bar_eod_with_base_date_start(self):
        api_for_test = api.GetEquityBarEOD
        base_date = 'start'
        self._test_base_date_template(api_for_test, base_date)

    def test_equity_bar_min5_with_base_date_start(self):
        api_for_test = api.GetEquityBarMin5
        base_date = 'start'
        self._test_base_date_template(api_for_test, base_date)

    def test_equity_bar_min1_with_base_date_start(self):
        api_for_test = api.GetEquityBarMin1
        base_date = 'start'
        self._test_base_date_template(api_for_test, base_date)

    @unittest.skip("currently EQUITY_5MIN_PATCH is not completed")
    def test_equity_bar_eod_comparing_with_min5_with_base_data_none(self):
        instruments = ['600000', '000001']
        eod_prices = api.GetEquityBarEOD(instruments,
                                         '2013-01-01',
                                         '2015-10-01',
                                         field=['closePrice'],
                                         baseDate=None,
                                         forceUpdate=True)
        min5_prices = api.GetEquityBarMin5(instruments,
                                           '2013-01-01',
                                           '2015-10-01',
                                           field=['closePrice'],
                                           baseDate=None,
                                           forceUpdate=True)

        eod_from_min5_prices = min5_prices[min5_prices.tradingTime == '14:55:00.0000000']
        for ins in instruments:
            specific_eod_from_min5 = eod_from_min5_prices[eod_from_min5_prices.instrumentID == ins]
            sepcific_eod = eod_prices[eod_prices.instrumentID == ins]
            self.assertEqual(len(specific_eod_from_min5), len(sepcific_eod))

            for prices1, prices2 in zip(specific_eod_from_min5.closePrices.values, sepcific_eod.closePrice.values):
                self.assertAlmostEqual(prices1, prices2, 12)

    @unittest.skip("currently EQUITY_1MIN_PATCH is not completed")
    def test_equity_bar_eod_comparing_with_min1_with_base_data_none(self):
        instruments = ['600000', '000001']
        eod_prices = api.GetEquityBarEOD(instruments,
                                         '2012-12-01',
                                         '2015-10-01',
                                         field=['closePrice'],
                                         baseDate=None,
                                         forceUpdate=True)
        min5_prices = api.GetEquityBarMin1(instruments,
                                           '2012-12-01',
                                           '2015-10-01',
                                           field=['closePrice'],
                                           baseDate=None,
                                           forceUpdate=True)

        eod_from_min5_prices = min5_prices[min5_prices.tradingTime == '14:59:00.0000000']
        for ins in instruments:
            specific_eod_from_min5 = eod_from_min5_prices[eod_from_min5_prices.instrumentID == ins]
            sepcific_eod = eod_prices[eod_prices.instrumentID == ins]
            self.assertEqual(len(specific_eod_from_min5), len(sepcific_eod))

            for prices1, prices2 in zip(specific_eod_from_min5.closePrices.values, sepcific_eod.closePrice.values):
                self.assertAlmostEqual(prices1, prices2, 12)
