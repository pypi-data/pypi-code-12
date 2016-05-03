# -*- coding: utf-8 -*-
u"""
Created on 2015-12-17

@author: cheng.li
"""

import unittest
from DataAPI import api


class TestInstrumentInfo(unittest.TestCase):

    def test_get_future_info_with_specific_instrument_name(self):
        data = api.GetFutureInstrumentInfo('IF1506')
        self.assertTrue(len(data) == 1)

    def test_get_future_info_with_lower_case(self):
        data = api.GetFutureInstrumentInfo('if1506')
        self.assertTrue(len(data) == 1)

    def test_get_future_info_with_specific_columns(self):
        data = api.GetFutureInstrumentInfo('IF1606', ['market', 'windCode'])
        self.assertTrue('windCode' in data)
        self.assertTrue('market' in data)
        self.assertTrue('cnName' not in data)

    def test_get_future_info_with_wildcard_rule(self):
        data = api.GetFutureInstrumentInfo('if*')
        # spot check several contract
        self.assertTrue('IFM0906' in data.instrumentID.values)
        self.assertTrue('IF1201' in data.instrumentID.values)
        self.assertTrue('IF1512' in data.instrumentID.values)
        self.assertFalse('AF1501' in data.instrumentID.values)

    def test_get_future_info_with_wildcard_rule_2(self):
        data = api.GetFutureInstrumentInfo('*15*')
        # spot check several contract
        self.assertTrue('IF1512' in data.instrumentID.values)
        self.assertTrue('AF1503-S' in data.instrumentID.values)
        self.assertTrue('AG1506' in data.instrumentID.values)
        self.assertFalse('IF1401' in data.instrumentID.values)

    def test_get_future_info_with_wokring_day(self):
        data = api.GetFutureInstrumentInfo(refdate='2015-12-18')
        self.assertEqual(len(data), 494)

    def test_get_future_info_with_holiday(self):
        data = api.GetFutureInstrumentInfo(refdate='2015-12-19')
        self.assertEqual(len(data), 0)

    def test_get_equity_info_with_specific_instrument_name(self):
        data = api.GetEquityInstrumentInfo('600000')
        self.assertEqual(len(data), 1)
        self.assertEqual(data['instrumentID'][0], '600000')

    def test_get_equity_info_with_wrong_instrument_name(self):
        data = api.GetEquityInstrumentInfo('oops')
        self.assertEqual(len(data), 0)

    def test_get_euqity_info_with_board_name(self):
        data = api.GetEquityInstrumentInfo(boardName=u'主板')
        listboards = data.listBoardName
        for board in listboards:
            self.assertEqual(board, u'主板')

    def test_get_equity_info_with_specific_columns(self):
        data = api.GetEquityInstrumentInfo(field=['exchange'])
        self.assertTrue('exchange' in data)
        self.assertTrue('instrumentID' not in data)

    def test_get_equity_info_with_specific_reference_date(self):
        refDate = "20121231"
        data = api.GetEquityInstrumentInfo(refDate=refDate[:4] + "-" + refDate[4:6] + "-" + refDate[6:8])
        listdates = data.listDate
        for date in listdates:
            self.assertTrue(date <= refDate)

        delistdates = data.delistDate
        for date in delistdates:
            self.assertTrue(not date or date >= refDate)

    def test_get_equity_info_with_several_conditions(self):
        codes = ['600000', '300357']
        boardname = u'创业板'

        data = api.GetEquityInstrumentInfo(instrumentIDList=codes,
                                           boardName=boardname)

        self.assertEqual(len(data), 1)
        output_codes = data.instrumentID.values
        self.assertTrue('300357' in output_codes)
        self.assertTrue('600000' not in output_codes)

