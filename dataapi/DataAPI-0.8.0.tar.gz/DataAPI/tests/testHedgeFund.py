# -*- coding: utf-8 -*-
u"""
Created on 2016-1-5

@author: cheng.li
"""

import unittest
import numpy as np
import pandas as pd
from DataAPI import api
from DataAPI.HedgeFund import perf_combine
from PyFin.POpt.Optimizer import portfolio_returns
from PyFin.POpt.Optimizer import utility_calculator
from PyFin.POpt.Optimizer import portfolio_optimization
from PyFin.POpt.Optimizer import OptTarget


class TestHedgeFund(unittest.TestCase):
    def test_hedge_fund_info(self):
        data = api.GetHedgeFundInfo()
        self.assertTrue(len(data) > 1)

    def test_hedge_fund_info_with_specific_first_invest(self):
        data = api.GetHedgeFundInfo(firstInvestType=u'股票型')
        first_invest_types = data.firstInvestType.values
        for ftype in first_invest_types:
            self.assertEqual(ftype, u'股票型')

    def test_hedge_fund_info_with_wrong_field(self):
        with self.assertRaises(ValueError):
            _ = api.GetHedgeFundInfo(field='listDate')

    def test_hedge_fund_info_with_specific_field(self):
        data = api.GetHedgeFundInfo(field='fullName')
        self.assertTrue('fullName' in data)
        self.assertTrue('instrumentID' not in data)

    def test_hedge_fund_bar_week_with_specific_instrument(self):
        data = api.GetHedgeFundBarWeek('XT125853.XT')
        instruments = data.instrumentID.unique()
        self.assertEqual(len(instruments), 1)
        self.assertEqual(instruments[0], u'XT125853.XT')

    def test_hedge_fund_bar_week_with_wrong_field(self):
        with self.assertRaises(ValueError):
            _ = api.GetHedgeFundBarWeek(field='listDate')

    def test_hedge_fund_bar_week_with_specific_field(self):
        data = api.GetHedgeFundBarWeek(field='navUnit')
        self.assertTrue('navUnit' in data)
        self.assertTrue('navAcc' not in data)

    def test_hedge_fund_style_ret(self):
        data = api.GetHedgeFundStylePerf(styleName=u'债券型', startDate='2014-01-01', endDate='2016-02-01')
        self.assertEqual(len(data), 26)

    def test_hedge_fund_style_analysis(self):
        styles = [u'债券型', u'多空仓型', u'宏观策略', u'市场中性', u'管理期货', u'股票型', u'货币型']
        for style in styles:
            data = api.GetHedgeFundStylePerf(styleName=style, startDate='2014-01-01', endDate='2016-02-01')
            data['nav'] = np.exp((data['median_ret'] / 100.).cumsum())
            specific_data = data[['nav']]
            res = api.GetHedgeFundStyleAnalysis(navTable=specific_data)
            self.assertAlmostEqual(res[style][0], 1.0)

    def test_hedge_fund_portfolio_perf_db(self):
        instruments = ['XT125045.XT', 'XT130295.XT']

        return_data = perf_combine(instruments, navTable=pd.DataFrame(), startDate='2013-01-01',
                                   endDate='2016-03-22')
        return_data.dropna(inplace=True)
        nav_data = np.exp(return_data.cumsum())

        sample_weights = {'XT125045.XT': 1.0, 'XT130295.XT': 0.0}
        data = api.GetHedgePortfolioPerf(instruments=instruments,
                                         weights=sample_weights,
                                         startDate='2013-01-01',
                                         endDate='2016-03-22')

        for pvalue, fvalue in zip(data['portfolio'], nav_data['XT125045.XT']):
            self.assertAlmostEqual(pvalue, fvalue)

        sample_weights = {'XT125045.XT': 0.0, 'XT130295.XT': 1.0}
        data = api.GetHedgePortfolioPerf(instruments=instruments,
                                         weights=sample_weights,
                                         startDate='2013-01-01',
                                         endDate='2016-03-22')

        for pvalue, fvalue in zip(data['portfolio'], nav_data['XT130295.XT']):
            self.assertAlmostEqual(pvalue, fvalue)

    def test_hedge_fund_utility_calculator(self):
        instruments = ['XT125045.XT', 'XT130295.XT']
        return_data = perf_combine(instruments, navTable=pd.DataFrame(), startDate='2013-01-01',
                                   endDate='2016-03-04')
        return_data.dropna(inplace=True)
        nav_data = np.exp(return_data.cumsum())

        sample_weights = {'XT125045.XT': 0.8, 'XT130295.XT': 0.2}

        nav_data2 = api.GetHedgePortfolioPerf(instruments=instruments,
                                              weights=sample_weights,
                                              startDate='2013-01-01',
                                              endDate='2016-03-04')

        score_data = api.GetHedgeFundPerfComparison(navTable=nav_data2, startDate='2013-01-01',  endDate='2016-03-04')

        sample_weights = np.array([sample_weights[col] for col in nav_data.columns])

        for _, field in enumerate(OptTarget):
            returns = portfolio_returns(sample_weights, nav_table=np.array(nav_data.values), rebalance=False)
            score = utility_calculator(returns, opt_type=field)
            if field == OptTarget.RETURN:
                self.assertAlmostEqual(score_data[u'年化收益'][0], np.exp(score) - 1.0)
            elif field == OptTarget.VOL:
                self.assertAlmostEqual(-score_data[u'波动率'][0], score)
            elif field == OptTarget.MAX_DRAWDOWN:
                self.assertAlmostEqual(score_data[u'最大回撤'][0], 1.0 - np.exp(score))
            elif field == OptTarget.SHARP:
                self.assertAlmostEqual(score_data[u'sharp'][0], score)
            elif field == OptTarget.SORTINO:
                self.assertAlmostEqual(score_data[u'sortino'][0], score)
            elif field == OptTarget.RETURN_D_MAX_DRAWDOWN:
                self.assertAlmostEqual(score_data[u'收益回撤比'][0], score_data[u'年化收益'][0] / score_data[u'最大回撤'][0])

    def _create_value_dict(self, names, values):
        return {name: value for name, value in zip(names, values)}

    def test_hedge_fund_portfolio_optimizer_without_reblance(self):
        instruments = sorted(['XT125045.XT',
                              'XT130295.XT',
                              'XT090981.XT',
                              'XT113779.XT',
                              'XT091121.XT',
                              'XT121986.XT',
                              'XT1205941.XT',
                              'XT101310.XT',
                              'XT113932.XT',
                              'XT090776.XT',
                              'XT112098.XT',
                              'XT110161.XT',
                              'XT113453.XT',
                              'XT125853.XT'])

        return_data = perf_combine(instruments,
                                   navTable=pd.DataFrame(),
                                   startDate='2013-01-01',
                                   endDate='2016-03-04')
        return_data.dropna(inplace=True)
        nav_data = np.exp(return_data.cumsum())

        nav_data.to_csv('d:/funds_data.csv')

        guess = [0.1 / len(instruments)] * len(instruments)

        # all the results are tested against Matlab with fmincon function

        # target with maximum return
        matlab_res = self._create_value_dict(instruments, [4.75393550839560e-19,
                                                           0,
                                                           3.43546906184303e-19,
                                                           0,
                                                           0,
                                                           8.36677837797548e-20,
                                                           0,
                                                           5.76673494924112e-19,
                                                           4.05923081267658e-19,
                                                           0,
                                                           3.12250225675825e-17,
                                                           2.41998887084620e-20,
                                                           0,
                                                           1])

        out, fx, its, imode, smode = portfolio_optimization(guess, nav_data, OptTarget.RETURN)
        for name in matlab_res:
            self.assertAlmostEqual(matlab_res[name], out[name]['weight'], 4)

        # target with minimum volatilty
        matlab_res = self._create_value_dict(instruments, [0,
                                                           0,
                                                           0,
                                                           6.99175721467524e-39,
                                                           1.87467007228981e-38,
                                                           0.00376413514611989,
                                                           0,
                                                           7.75214182640125e-38,
                                                           0.000712597692602067,
                                                           0,
                                                           0,
                                                           0.994237264821637,
                                                           0.00128600233964123,
                                                           7.05296610493373e-38])

        out, fx, its, imode, smode = portfolio_optimization(guess, nav_data, OptTarget.VOL)
        for name in matlab_res:
            self.assertAlmostEqual(matlab_res[name], out[name]['weight'], 4)

        # target with maximum sharp
        matlab_res = self._create_value_dict(instruments, [3.72414607721023e-39,
                                                           5.58329252509498e-40,
                                                           8.50903300813402e-40,
                                                           9.42738796971393e-40,
                                                           4.83561316181437e-40,
                                                           0.00102720032914267,
                                                           4.40810381558358e-39,
                                                           0.000145735792353755,
                                                           0.000756493258973369,
                                                           3.91725820023446e-40,
                                                           0,
                                                           0.996553125979859,
                                                           0.00117153574239032,
                                                           0.000345908897280735])

        out, fx, its, imode, smode = portfolio_optimization(guess, nav_data, OptTarget.SHARP)
        for name in matlab_res:
            self.assertAlmostEqual(matlab_res[name], out[name]['weight'], 4)

    def test_hedge_fund_portfolio_optimizer_with_rebalance(self):
        instruments = sorted(['XT125045.XT',
                              'XT130295.XT',
                              'XT090981.XT',
                              'XT113779.XT',
                              'XT091121.XT',
                              'XT121986.XT',
                              'XT1205941.XT',
                              'XT101310.XT',
                              'XT113932.XT',
                              'XT090776.XT',
                              'XT112098.XT',
                              'XT110161.XT',
                              'XT113453.XT',
                              'XT125853.XT'])

        return_data = perf_combine(instruments,
                                   navTable=pd.DataFrame(),
                                   startDate='2013-01-01',
                                   endDate='2016-03-04')
        return_data.dropna(inplace=True)
        nav_data = np.exp(return_data.cumsum())

        guess = [1.0 / len(instruments)] * len(instruments)

        # all the results are tested against Matlab with fmincon function

        # target with maximum return
        matlab_res = self._create_value_dict(instruments, [1.59234884538490e-17,
                                                           1.64287856671892e-18,
                                                           2.31111593326468e-33,
                                                           5.02151358940695e-17,
                                                           0,
                                                           9.41672950270667e-18,
                                                           1.64287856671892e-18,
                                                           2.82144347121750e-17,
                                                           0,
                                                           2.24595602784406e-17,
                                                           2.44504165203472e-16,
                                                           -1.68518870133883e-34,
                                                           0,
                                                           1.00000000000000])

        out, fx, its, imode, smode = portfolio_optimization(guess, nav_data, OptTarget.RETURN, True)
        for name in matlab_res:
            self.assertAlmostEqual(matlab_res[name], out[name]['weight'], 4)

        # target with minimum volatilty
        matlab_res = self._create_value_dict(instruments, [1.17549435082229e-38,
                                                           0,
                                                           0,
                                                           1.68242628961440e-37,
                                                           0,
                                                           0.00209693665998001,
                                                           0,
                                                           1.53548949576161e-37,
                                                           0.00135190283349081,
                                                           0,
                                                           6.31828213566980e-38,
                                                           0.994988759101536,
                                                           0.00156240140499358,
                                                           0])

        out, fx, its, imode, smode = portfolio_optimization(guess, nav_data, OptTarget.VOL, True)
        for name in matlab_res:
            self.assertAlmostEqual(matlab_res[name], out[name]['weight'], 4)

        # target with maximum sharp
        matlab_res = self._create_value_dict(instruments, [2.76471048953164e-22,
                                                           7.19170303955622e-21,
                                                           2.52983701805491e-21,
                                                           1.94636169061746e-22,
                                                           0,
                                                           0,
                                                           0,
                                                           0.000165267959303058,
                                                           0.00137258304784842,
                                                           0,
                                                           2.06247008802505e-22,
                                                           0.995739327032537,
                                                           0.00134638898667400,
                                                           0.00137643297363735])

        out, fx, its, imode, smode = portfolio_optimization(guess, nav_data, OptTarget.SHARP, True)
        for name in matlab_res:
            self.assertAlmostEqual(matlab_res[name], out[name]['weight'], 4)

        # target with minimum mean draw down.
        matlab_res = self._create_value_dict(instruments, [5.37474182227176e-22,
                                                           2.82896031188845e-22,
                                                           1.20698075433964e-23,
                                                           0.00274348787708052,
                                                           1.22120906871005e-22,
                                                           7.87524500196388e-23,
                                                           1.57188355733056e-22,
                                                           0.00725661407447253,
                                                           0.00379580611331051,
                                                           2.87596094074308e-22,
                                                           2.14643185237454e-22,
                                                           0.980793787184098,
                                                           0.00541030475103811,
                                                           8.32465103109039e-23])

        out, fx, its, imode, smode = portfolio_optimization(guess, nav_data, OptTarget.MEAN_DRAWDOWN, True)
        for name in matlab_res:
            self.assertAlmostEqual(matlab_res[name], out[name]['weight'], 4)

        # target with minimum max draw down.
        matlab_res = 0.001718164500123

        out, fx, its, imode, smode = portfolio_optimization(guess, nav_data, OptTarget.MAX_DRAWDOWN, True)
        self.assertAlmostEqual(matlab_res, fx, 4)

        # target with maximum return to max draw down
        matlab_res = -24.368711910217957

        out, fx, its, imode, smode = portfolio_optimization(guess, nav_data, OptTarget.RETURN_D_MAX_DRAWDOWN, True)
        self.assertLess(fx, 0.98 * matlab_res)
