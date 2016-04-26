#!/usr/bin/env python
# encoding: utf-8

def pricing(fv, cp, maturity, ytm, interval):
    period = int(maturity / interval)
    sum = 0
    for i in xrange(0, period):
        sum += (fv * cp * interval) / ((1 + ytm * interval) ** (i + 1))
    sum += fv / ((1 + ytm * interval) ** period)
    return sum

