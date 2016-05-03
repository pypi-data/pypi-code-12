# -*- coding: utf-8 -*-
u"""
Created on 2015-11-12

@author: cheng.li, weijun.shen
"""

# enum type
from DataAPI.MarketDataLoader import BAR_TYPE
from DataAPI.MarketDataLoader import ASSET_TYPE

# Equity
from DataAPI.Equity import GetEquityBarMin1
from DataAPI.Equity import GetEquityBarMin5
from DataAPI.Equity import GetEquityBarEOD

# Index
from DataAPI.Index import GetIndexBarMin1
from DataAPI.Index import GetIndexBarMin5
from DataAPI.Index import GetIndexBarEOD
from DataAPI.Index import GetIndexConstitutionInfo

# Index future
from DataAPI.Future import GetFutureBarMin1
from DataAPI.Future import GetFutureBarMin5
from DataAPI.Future import GetFutureBarMin5Continuing
from DataAPI.Future import GetFutureBarEOD
from DataAPI.Future import GetFutureBarEODContinuing

# Commodity
from DataAPI.Commodity import GetCommodityStocksInfo

# Hedge fund
from DataAPI.HedgeFund import GetHedgeFundInfo
from DataAPI.HedgeFund import GetHedgeFundPool
from DataAPI.HedgeFund import GetHedgeFundBarWeek
from DataAPI.HedgeFund import GetHedgeFundBarMonth
from DataAPI.HedgeFund import GetHedgeFundStylePerf
from DataAPI.HedgeFund import GetHedgeFundPerfComparison
from DataAPI.HedgeFund import GetHedgeFundStyleAnalysis
from DataAPI.HedgeFund import GetHedgePortfolioPerf
from DataAPI.HedgeFund import GetHedgeFundOptimizedPortfolio

# Mutual fund
from DataAPI.MutualFund import GetMutualFundBarMin5

# General
from DataAPI.General import GetGeneralBarData

# Security master data
from DataAPI.InstrumentInfo import GetFutureInstrumentInfo
from DataAPI.InstrumentInfo import GetEquityInstrumentInfo

# Themes analysis
from DataAPI.Themes import GetThemeInfo
from DataAPI.Themes import GetThemeHotness
from DataAPI.Themes import GetStocksByTheme
from DataAPI.Themes import GetActiveThemesRelatedStocks

# Snapshot
from DataAPI.Snapshots import GetIndustryNetCashSnapshot

# Settings
from DataAPI.Utilities import Settings


__all__ = ['BAR_TYPE',
           'ASSET_TYPE',
           'GetEquityBarMin1',
           'GetEquityBarMin5',
           'GetEquityBarEOD',
           'GetIndexBarMin1',
           'GetIndexBarMin5',
           'GetIndexBarEOD',
           'GetIndexConstitutionInfo',
           'GetFutureBarMin1',
           'GetFutureBarMin5',
           'GetFutureBarMin5Continuing',
           'GetFutureBarEOD',
           'GetFutureBarEODContinuing',
           'GetCommodityStocksInfo',
           'GetHedgeFundInfo',
           'GetHedgeFundPool',
           'GetHedgeFundBarWeek',
           'GetHedgeFundBarMonth',
           'GetHedgeFundStylePerf',
           'GetHedgeFundPerfComparison',
           'GetHedgeFundStyleAnalysis',
           'GetHedgePortfolioPerf',
           'GetHedgeFundOptimizedPortfolio',
           'GetMutualFundBarMin5',
           'GetGeneralBarData',
           'GetFutureInstrumentInfo',
           'GetEquityInstrumentInfo',
           'Settings',
           'GetThemeInfo',
           'GetThemeHotness',
           'GetStocksByTheme',
           'GetActiveThemesRelatedStocks',
           'GetIndustryNetCashSnapshot']

