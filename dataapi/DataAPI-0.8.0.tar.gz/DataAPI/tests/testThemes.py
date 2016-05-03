# -*- coding: utf-8 -*-
u"""
Created on 2016-1-7

@author: cheng.li, weijun.shen, yuchen.lai
"""

import unittest
from DataAPI import api


class TestThemes(unittest.TestCase):

    def setUp(self):
        api.Settings.set_token()

    def test_get_theme_info(self):
        data = api.GetThemeInfo(themeName=u'火箭军')
        self.assertTrue(len(data) > 0)

    def test_get_empty_theme(self):
        data = api.GetThemeInfo(themeName=u'不存在的主题')
        self.assertTrue(len(data) == 0)

    def test_theme_hotness(self):
        data = api.GetThemeHotness(u'银行', '2015-01-01', '2016-01-01')
        self.assertEqual(len(data), 7686)

    def test_theme_hotness_with_wrong_field(self):
        with self.assertRaises(ValueError):
            _ = api.GetThemeHotness(u'银行', '2015-01-01', '2016-01-01', field='closePrice')

    def test_theme_hotness_with_specific_field(self):
        data = api.GetThemeHotness(u'银行', '2015-01-01', '2016-01-01', field=['newsNum', 'themeID'])
        self.assertTrue('newsNum' in data)
        self.assertTrue('themeID' in data)
        self.assertTrue('themeName' not in data)

    def test_theme_related_stocks(self):
        data = api.GetStocksByTheme(u'机器人', refDate='2016-01-05')
        self.assertTrue(len(data) > 0)

    def test_theme_related_stocks_with_wrong_field(self):
        with self.assertRaises(ValueError):
            _ = api.GetStocksByTheme(u'机器人', refDate='2015-01-05', field=['closePrice', 'date'])

    def test_theme_related_stocks_with_specific_field(self):
        data = api.GetStocksByTheme(u'机器人', refDate='2016-01-05', field='score')
        self.assertTrue('score' in data)
        self.assertTrue('themeID' not in data)

    def test_theme_active_themes_related_stocks(self):
        data = api.GetActiveThemesRelatedStocks(refDate='2016-01-04')
        self.assertTrue(len(data) > 300)