from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
import numpy as np

from measurement_stats import value


def unweighted(*values):
    """

    :param values:
    :return:
    """

    if not values:
        return value.ValueUncertainty()

    if isinstance(values[0], (list, tuple)):
        values = values[0]
        if not values:
            return value.ValueUncertainty()

    values = [v.value for v in values]
    return value.ValueUncertainty(
            value=float(np.mean(values)),
            uncertainty=float(np.std(values))
    )


def weighted(*values):
    """
    Calculates the uncertainty weighted average of the provided values,
    where each value is a ValueUncertainty instance. For mathematical
    formulation of the weighted average see "An Introduction to Error
    Analysis, 2nd Edition" by John R. Taylor, Chapter 7.2.

    :param values:
    :return:
    """

    if not values:
        return value.ValueUncertainty()

    if isinstance(values[0], (list, tuple)):
        values = values[0]
        if not values:
            return value.ValueUncertainty()

    wxs = 0.0
    ws  = 0.0
    for v in values:
        w = 1.0/(v.uncertainty*v.uncertainty)
        wxs += w*v.value
        ws  += w

    ave = wxs/ws
    unc =  1.0/math.sqrt(ws)

    return value.ValueUncertainty(value=ave, uncertainty=unc)


def weighted_mean_and_deviation(*values):
    """
    Returns the mean and standard deviation of a weighted set of values.
    For further info see:
        http://stats.stackexchange.com/questions/6534/
            how-do-i-calculate-a-weighted-standard-deviation-in-excel

    :param values:
    :return:
    """

    if not values:
        return value.ValueUncertainty()

    if isinstance(values[0], (list, tuple)):
        values = values[0]
        if not values:
            return value.ValueUncertainty()

    if len(values) == 1:
        return values[0].clone()

    wxs = 0.0
    ws  = 0.0
    weights = []

    for v in values:
        w = 1.0/(v.uncertainty*v.uncertainty)
        weights.append(w)
        wxs += w*v.value
        ws  += w

    ave = wxs/ws
    dev = 0.0
    N = len(values)
    for i in range(N):
        dev += weights[i]*(values[i].value - ave)**2

    denom = ws*(N - 1.0)/N
    dev = math.sqrt(dev/denom)

    return value.ValueUncertainty(value=ave, uncertainty=dev)
