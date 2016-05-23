#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module: transform.py
Author: zlamberty
Created: 2016-02-23

Description:
    transormations, mostly of pandas dataframes

Usage:
    <usage>

"""

import os
import pandas as pd

import eri.logging as logging


# ----------------------------- #
#   Module Constants            #
# ----------------------------- #

logger = logging.getLogger(__name__)


# ----------------------------- #
#   Main routine                #
# ----------------------------- #

def tenure(series, start=0):
    """given a df of exactly one 'stints' for which tenure is meaningful,
    calcualte tenure. This function is passed to the
        df.groupby().columnname.transform()
    function

    args:
        series: (pd series) a pandas series, often a chunk of one as given by
            the groupby function
        start: (int) base value of tenure (assume tenure associate to first year
            is `start`)

    returns:
        pd data frame of tenure values

    """
    yrdiffs = series.sort_values().diff().fillna(0)
    ten = yrdiffs.cumsum()

    # larger-than-1 gaps indicate they left and came back; subtract off that gap
    # time from all remaining values
    gaps = yrdiffs[yrdiffs > 1]
    for i in gaps.index:
        ten.loc[i:] -= ten.loc[i]

    ten += start

    return ten
