from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np

from measurement_stats.distributions.boxes import support


def unweighted_tukey(distribution_or_values):
    """
    Returns the unweighted Tukey box-whisker boundaries for the given
    distribution, including the median. As the returned boundaries are
    unweighted, they ignore uncertainties in the measurements.

    :param distribution_or_values:
        The distribution for which to calculate the boundaries
    :return:
        A tuple containing 5 values:
            * minimum (whisker boundary)
            * lower quartile (box boundary)
            * median
            * upper quartile (box boundary)
            * maximum (whisker boundary)
    :rtype: tuple
    """

    values = support.to_unweighted_population(distribution_or_values)

    median = np.percentile(values, 50)
    lower_quartile = np.percentile(values, 25)
    upper_quartile = np.percentile(values, 75)

    inter_quartile_range = upper_quartile - lower_quartile
    tukey_range = 1.5 * inter_quartile_range

    values.sort()
    bottom = None
    top = None
    for index in range(len(values)):
        v = values[index]
        if bottom is None and v >= (median - tukey_range):
            bottom = v

        v = values[len(values) - index - 1]
        if top is None and v <= (median + tukey_range):
            top = v

        if top is not None and bottom is not None:
            break

    return bottom, lower_quartile, median, upper_quartile, top


def weighted_tukey(distribution_or_population, count=None):
    """
    Returns the weighted Tukey box-whisker boundaries for the given
    distribution, including the mean. These boundaries are based on the
    weighted distributions distribution and take into account the uncertainties
    in the measurements.

    :param distribution_or_population:
        The distribution for which to calculate the boundaries
    :param count:
        The number of values to use when creating the weighted probability
        population used to define the whiskers
    :return:
        A tuple containing 5 values:
        * minimum (whisker boundary)
        * lower quartile (box boundary)
        * median
        * upper quartile (box boundary)
        * maximum (whisker boundary)
    :rtype: tuple
    """

    return unweighted_tukey(support.to_weighted_population(
        distribution_or_population, count
    ))


def unweighted_nine(distribution_or_values):
    """
    Returns the unweighted "Nines" box-whisker boundaries for the given
    distribution, including the median, where the whiskers are defined by the
    9% and 91% percentiles.

    :param distribution_or_values:
        The distribution for which to calculate the boundaries
    :return:
        A tuple containing 5 values:
            * minimum (whisker boundary)
            * lower quartile (box boundary)
            * median
            * upper quartile (box boundary)
            * maximum (whisker boundary)
    :rtype: tuple
    """

    values = support.to_unweighted_population(distribution_or_values)

    return (
        np.percentile(values, 9),
        np.percentile(values, 25),
        np.percentile(values, 50),
        np.percentile(values, 75),
        np.percentile(values, 91)
    )


def weighted_nine(distribution_or_population, count=None):
    """
    Returns the weighted "Nines" box-whisker boundaries for the given
    distribution, including the median, where the whiskers are defined by the
    9% and 91% percentiles.

    :param distribution_or_population:
        The distribution for which to calculate the boundaries
    :param count:
        The number of values to use when creating the weighted probability
        population
    :return:
        A tuple containing 5 values:
            * minimum (whisker boundary)
            * lower quartile (box boundary)
            * median
            * upper quartile (box boundary)
            * maximum (whisker boundary)
    :rtype: tuple
    """

    return unweighted_nine(
        support.to_weighted_population(distribution_or_population, count)
    )


def unweighted_two(distribution_or_values):
    """
    Returns the unweighted "Twos" box-whisker boundaries for the given
    distribution, including the median, where the whiskers are defined by the
    2% and 98% percentiles.

    :param distribution_or_values:
        The distribution for which to calculate the boundaries
    :return:
        A tuple containing 5 values:
            * minimum (whisker boundary)
            * lower quartile (box boundary)
            * median
            * upper quartile (box boundary)
            * maximum (whisker boundary)
    :rtype: tuple
    """

    values = support.to_unweighted_population(distribution_or_values)

    return (
        np.percentile(values, 2),
        np.percentile(values, 25),
        np.percentile(values, 50),
        np.percentile(values, 75),
        np.percentile(values, 98)
    )


def weighted_two(distribution_or_population, count=None):
    """
    Returns the weighted "Twos" box-whisker boundaries for the given
    distribution, including the median, where the whiskers are defined by the
    2% and 98% percentiles.

    :param distribution_or_population:
        The distribution for which to calculate the boundaries
    :param count:
        The number of values to use when creating the weighted probability
        population
    :return:
        A tuple containing 5 values:
            * minimum (whisker boundary)
            * lower quartile (box boundary)
            * median
            * upper quartile (box boundary)
            * maximum (whisker boundary)
    :rtype: tuple
    """

    return unweighted_two(
        support.to_weighted_population(distribution_or_population, count)
    )
