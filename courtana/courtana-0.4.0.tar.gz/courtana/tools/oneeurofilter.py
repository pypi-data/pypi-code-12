# -*- coding: utf-8 -*-

"""
1€ Filter
=========

My implementation of the "1€ Filter"!

More info: http://www.lifl.fr/~casiez/1euro/

Paper: http://www.lifl.fr/~casiez/publications/CHI2012-casiez.pdf
"""

import math


class OneEuroFilter(object):

    def __init__(self, freq, mincutoff=1.0, beta=0.0, dcutoff=1.0):
        if freq <= 0:
            raise ValueError("freq should be >0")
        if mincutoff <= 0:
            raise ValueError("mincutoff should be >0")
        if dcutoff <= 0:
            raise ValueError("dcutoff should be >0")
        self._freq = float(freq)
        self._mincutoff = float(mincutoff)
        self._beta = float(beta)
        self._dcutoff = float(dcutoff)
        self._x = LowPassFilter(self._alpha(self._mincutoff))
        self._dx = LowPassFilter(self._alpha(self._dcutoff))
        self._lasttime = None

    def _alpha(self, cutoff):
        te = 1.0 / self._freq
        tau = 1.0 / (2*math.pi*cutoff)
        return 1.0 / (1.0 + tau/te)

    def __call__(self, x, timestamp=None):
        # NaN case
        if math.isnan(x):
            return float('NaN')
        # ---- update the sampling frequency based on timestamps
        if self._lasttime and timestamp:
            self._freq = 1.0 / (timestamp-self._lasttime)
        self._lasttime = timestamp
        # ---- estimate the current variation per second
        prev_x = self._x.lastValue()
        # FIXME: 0.0 or value?
        dx = 0.0 if prev_x is None else (x-prev_x)*self._freq
        edx = self._dx(dx, timestamp, alpha=self._alpha(self._dcutoff))
        # ---- use it to update the cutoff frequency
        cutoff = self._mincutoff + self._beta*math.fabs(edx)
        # ---- filter the given value
        return self._x(x, timestamp, alpha=self._alpha(cutoff))


class LowPassFilter(object):

    def __init__(self, alpha):
        self._setAlpha(alpha)
        self._y = self._s = None

    def _setAlpha(self, alpha):
        alpha = float(alpha)
        if alpha <= 0 or alpha > 1.0:
            raise ValueError("alpha (%s) should be in (0.0, 1.0]" % alpha)
        self._alpha = alpha

    def __call__(self, value, timestamp=None, alpha=None):
        if alpha is not None:
            self._setAlpha(alpha)
        if self._y is None:
            s = value
        else:
            s = self._alpha*value + (1.0-self._alpha)*self._s
        self._y = value
        self._s = s
        return s

    def lastValue(self):
        return self._y


if __name__ == '__main__':
    import random

    duration = 10.0  # seconds

    config = {
        'freq': 120,       # Hz
        'mincutoff': 1.0,  # FIXME
        'beta': 1.0,       # FIXME
        'dcutoff': 1.0     # this one should be ok
        }

    print("#SRC OneEuroFilter.py")
    print("#CFG {}".format(config))
    print("#LOG timestamp, signal, noisy, filtered")

    f = OneEuroFilter(**config)
    timestamp = 0.0  # seconds
    while timestamp < duration:
        signal = math.sin(timestamp)
        noisy = signal + (random.random()-0.5)/5.0
        filtered = f(noisy, timestamp)
        print("{0}, {1}, {2}, {3}".format(timestamp, signal, noisy, filtered))
        timestamp += 1.0/config["freq"]
