from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np

from measurement_stats.density import ops


def unweighted_boundaries(distribution):
    """
    Returns the unweighted Tukey box-whisker boundaries for the given
    distribution, including the mean. As the returned boundaries are
    unweighted, they ignore uncertainties in the measurements.

    :param distribution: The distribution for which to calculate the boundaries
    :return: A tuple containing 5 values:
        * minimum (whisker boundary)
        * lower quartile (box boundary)
        * percentile
        * upper quartile (box boundary)
        * maximum (whisker boundary)
    :rtype: tuple
    """

    measurements = [m.value for m in distribution.measurements]

    lower_quartile = np.percentile(measurements, 25)
    upper_quartile = np.percentile(measurements, 75)
    inter_quartile_range = upper_quartile - lower_quartile

    return (
        lower_quartile - inter_quartile_range,
        lower_quartile,
        np.percentile(measurements, 50),
        upper_quartile,
        upper_quartile + inter_quartile_range
    )


def weighted_boundaries(distribution, tolerance=1e-6):
    """
    Returns the weighted Tukey box-whisker boundaries for the given
    distribution, including the mean. These boundaries are based on the
    weighted density distribution and take into account the uncertainties
    in the measurements.

    :param distribution:
        The distribution for which to calculate the boundaries
    :param tolerance:
        The acceptable convergence tolerance when numerically integrating the
        distribution to find the region boundaries. A smaller value will
        produce more precise results but will take longer to compute.
    :return:
        A tuple containing 5 values:
        * minimum (whisker boundary)
        * lower quartile (box boundary)
        * percentile
        * upper quartile (box boundary)
        * maximum (whisker boundary)
    :rtype: tuple
    """

    lower_quartile = ops.percentile(distribution, 0.25)['x']
    upper_quartile = ops.percentile(distribution, 0.75)['x']
    inter_quartile_range = upper_quartile - lower_quartile

    return (
        lower_quartile - inter_quartile_range,
        lower_quartile,
        ops.percentile(distribution, 0.5)['x'],
        upper_quartile,
        upper_quartile + inter_quartile_range
    )
