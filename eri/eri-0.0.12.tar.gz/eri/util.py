#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module: util.py
Author: zlamberty
Created: 2016-02-25

Description:
    simple utility functions I feel should have been included elsewhere

Usage:
    <usage>

"""

import numpy as _np

import eri.logging as logging


# ----------------------------- #
#   Module Constants            #
# ----------------------------- #

logger = logging.getLogger(__name__)


# ----------------------------- #
#   utilities                   #
# ----------------------------- #

def norm(l):
    """given an iterable of numbers, return the vector norm"""
    return _np.sqrt(_np.square(l).sum())
