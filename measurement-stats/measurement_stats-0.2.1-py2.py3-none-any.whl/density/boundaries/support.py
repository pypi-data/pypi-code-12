from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from measurement_stats.density import ops


def to_weighted_population(distribution_or_population, count=None):
    """

    :param distribution_or_population:
    :param count:
    :return:
    """

    if count is None:
        count = 4096

    if hasattr(distribution_or_population, 'measurements'):
        return ops.population(distribution_or_population, count)

    return distribution_or_population


def to_unweighted_population(distribution_or_values):
    """

    :param distribution_or_values:
    :return:
    """

    if hasattr(distribution_or_values, 'measurements'):
        return [x.value for x in distribution_or_values.measurements]

    return distribution_or_values
