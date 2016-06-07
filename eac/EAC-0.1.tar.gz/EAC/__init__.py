#!/usr/bin/env python
#coding:utf-8
"""
  Author: Yeison Cardona  --<yeisoneng@gmail.com>
  Purpose: Implement EAC algorithm in Python because I can.
  Created: 06/06/16
"""

import numpy as np
from scipy.signal import hanning
from scipy.fftpack import fft

#----------------------------------------------------------------------
def eac(data, windowsize=2**11):
    """
    A Computationally Efficient Multipitch Analysis Model
    IEEE TRANSACTIONS ON SPEECH AND AUDIO PROCESSING, VOL. 8, NO. 6, NOVEMBER 2000
    Tero Tolonen, Student Member, IEEE, and Matti Karjalainen, Member, IEEE

    Audacity: A Digital Audio Editor
    FreqWindow.cpp
    Dominic Mazzoni
    """

    half = int(windowsize / 2)
    mProcessed = np.zeros(half)

    win = hanning(windowsize)
    start = 0
    windows = 0
    while start + windowsize <= len(data):

        in_ = [win[i] * data[start + i] for i in range(windowsize)]

        out = fft(in_)
        in_ = [((v.real ** 2) + (v.imag ** 2)) ** (1 / 3) for v in out]

        out = fft(in_)
        mProcessed += np.array([v.real for v in out][:half])

        start += half
        windows += 1

    mProcessed = mProcessed / windows
    mProcessed = np.array([v if v > 0 else 0 for v in mProcessed])
    out = mProcessed.copy()

    for i in range(half):
        if (i % 2) == 0:
            mProcessed[i] -= out[int(i / 2)]
        else:
            mProcessed[i] -= ((out[int(i / 2)] + out[int(i / 2 + 1)]) / 2)

    mProcessed = np.array([v if v > 0 else 0 for v in mProcessed])

    return mProcessed[1:]
