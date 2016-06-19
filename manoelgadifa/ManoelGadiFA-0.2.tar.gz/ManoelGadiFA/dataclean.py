# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 00:37:05 2016

@author: knnkv
"""
import pandas as pd
import numpy as np



def cleandata(data0):
    for x in range(0, len(data0.columns)-1):
        if len(data0[data0.columns[x]].round(0).value_counts()) == len(data0[data0.columns[x]]):
            data0= data0.set_index(data0.columns[x])
    data0=data0[(np.abs(stats.zscore(data0)) < 3).all(axis=1)]
    data0=data0.dropna()
    data0=data0.drop_duplicates()
    return data0