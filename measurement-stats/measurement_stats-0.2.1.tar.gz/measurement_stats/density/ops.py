from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import random
from operator import itemgetter

import numpy as np

from measurement_stats import value
from measurement_stats.density.distribution import Distribution


def uniform_range(distribution, max_sigma, num_points=0, delta=0):
    """
    Creates a uniform range of values along the measurement (x) axis for
    the distribution within the boundaries created by the maximum sigma
    argument.

    :param distribution: The distribution for which the range should be created
    :type: refined_stats.density.Distribution

    :param max_sigma: Threshold sigma deviations that defines the range
        boundaries. The range will begin where all measurements are at least
        max_sigma above the value and end where all measurements are at
        least max_sigma below the value.
    :type: float

    :param num_points: (optional) The number of points to include in the range.
        If not specified the number of points will be assigned based either on
        the specified delta argument, or a default value of 1024.
    :type: int

    :param delta: (optional) Spacing between points within the range. If the
        number of points argument is specified (i.e. non-zero), this argument
        is ignored. If no number of points or delta are specified (both are 0)
        then a default delta will be assigned.
    :type: float

    :return: A list of uniformly spaced values that cover the distribution
        within the tolerance boundaries set by the max_sigma argument.
    :rtype: list
    """

    min_val = distribution.minimum_boundary(max_sigma)
    max_val = distribution.maximum_boundary(max_sigma)

    if not num_points:
        if delta:
            num_points = round((max_val - min_val) / delta)
        else:
            num_points = 1024

    return np.linspace(min_val, max_val, int(num_points))


def adaptive_range(distribution, max_sigma, max_delta=None):
    """
    Creates a dynamically assigned range of values along the measurement
    (x) axis for the distribution within the boundaries created by the
    maximum sigma argument.

    The values returned are not spaced equally. Instead they are spaced
    based on the gradient of the distribution, where larger gradients
    receive a higher density of values and smaller gradients less.

    :param distribution: The distribution for which the range should be created
    :type: refined_stats.density.Distribution

    :param max_sigma: Threshold sigma deviations that defines the range
        boundaries. The range will begin where all measurements are at least
        max_sigma above the value and end where all measurements are at
        least max_sigma below the value.
    :type: float

    :param max_delta: (optional) Maximum spacing between points within the
        range. If no maximum delta is assigned, one will be calculated
        automatically based on the structure of the distribution to prevent
        missing features.
    :type: float

    :return: A list of adaptively-spaced values that cover the distribution
        within the tolerance boundaries set by the max_sigma argument.
    :rtype: list
    """

    min_val = distribution.minimum_boundary(max_sigma)
    max_val = distribution.maximum_boundary(max_sigma)

    if max_delta is None:
        max_delta = 0.01 * abs(max_val - min_val)

    measurements = []
    for m in distribution.measurements:
        measurements.append({
            'min': m.value - 6.0*m.uncertainty,
            'max': m.value + 6.0*m.uncertainty,
            'value': m
        })

    measurements.sort(key=itemgetter('min'))

    out = [min_val]
    while out[-1] < max_val:
        delta = min(max_delta, max_val - out[-1])
        x_next = out[-1] + delta

        index = 0
        while len(measurements) and index < len(measurements):
            m = measurements[index]
            x = out[-1]
            x_next = x + delta

            if x_next <= m['min']:
                # BEFORE KERNEL: If the new x value is less than the lower
                # bound of the kernel value, use that delta value.
                break

            if m['max'] <= x:
                # AFTER KERNEL: If x is higher than the kernel upper
                # bound then skip to the next by removing this kernel from
                # the list so that it won't appear in future iterations.
                measurements.pop(0)
                continue

            if m['min'] <= x <= m['max']:
                # INSIDE KERNEL: If x is inside a kernel, use that kernel's
                # delta if it is smaller than the delta already set.
                delta = min(delta, 0.25*m['value'].uncertainty)

            elif x <= m['min'] and m['max'] <= x_next:
                # OVER KERNEL: If x and x+dx wrap around the kernel, use
                # a delta that puts the new x value at the lower edge of
                # the kernel.
                delta = min(delta, m['min'] - x)

            index += 1
            x_next = x + delta

        out.append(x_next)

    return out


def population(distribution, count=2048):
    """
    Creates a list of numerical values (no uncertainty) of the specified
    length that are representative of the distribution for use in less robust
    statistical operations.

    :param distribution:
        The distribution instance on which to create a population

    :param count: The number of numerical values to include in the returned
        population list.
    :type: int

    :return: A list of numerical values that approximate the the measurement
        probability density distribution
    :rtype: list
    """

    out = []
    x_min = distribution.minimum_boundary(10)
    x_max = distribution.maximum_boundary(10)

    x = x_min
    delta = (x_max - x_min) / 512.0
    total = float(len(distribution.measurements))

    while x <= x_max:
        n = int(round(count * delta * distribution.probability_at(x)))
        for i in range(n):
            out.append(random.uniform(
                x - 0.5 * delta,
                x + 0.5 * delta
            ))
        if x == x_max:
            break
        x = min(x_max, x + delta)
    return out


def overlap(distribution, comparison):
    """
    Returns the disparity in overlap between the two distributions.
    A value of 1.0 indicates that they overlap perfectly, while a value of
    0.0 indicates that there is no overlap between them. This approach can
    be useful in determining whether or not a distribution can be
    characterized by another one.

    :param distribution: A distribution for overlap comparison
    :type: refined_stats.density.Distribution

    :param comparison: A distribution for overlap comparison
    :type: refined_stats.density.Distribution

    :return: overlap on range [0, 1.0]
    :rtype: float
    """

    # Create a list of x values at critical points where the two distributions
    # should be evaluated
    x_values = list(set(
        adaptive_range(distribution, 10.0) +
        adaptive_range(comparison, 10.0)
    ))
    x_values.sort()

    out = 0.0
    my_value = distribution.probability_at(x_values[0])
    compare_value = comparison.probability_at(x_values[0])

    for i in range(len(x_values) - 1):
        x = x_values[i]
        x_next = x_values[i + 1]
        dx = x_next - x
        my_next_value = distribution.probability_at(x_next)
        compare_next_value = comparison.probability_at(x_next)

        my_area = dx * (
            min(my_value, my_next_value) +
            0.5 * abs(my_next_value - my_value)
        ) / float(len(distribution.measurements))

        compare_area = dx * (
            min(compare_value, compare_next_value) +
            0.5 * abs(compare_next_value - compare_value)
        )

        out += abs(my_area - compare_area)
        my_value = my_next_value
        compare_value = compare_next_value

    return 1.0 - 0.5*out


def weighted_median_average_deviation(distribution):
    """

    :param distribution:
    :return:
    """

    median = percentile(distribution, 0.5)

    # Create a list of the deviations, weighted by the uncertainty in the
    # measurement
    deviations = []
    for m in distribution.measurements:
        deviations.append(value.ValueUncertainty(
            abs(median - m.raw),
            m.raw_uncertainty
        ))

    dist = Distribution(
        measurements=deviations,
        kernel=distribution.kernel
    )

    return percentile(dist, 0.5)


def percentile(distribution_or_population, target=0.5, count=None):
    """
    Computes the position along the measurement axis where the distribution
    reaches the given target percentile_with_probability. The computation is
    carried out using a numerical integrator, which requires a tolerance where
    it can determine success and return

    :param distribution_or_population: The distribution for which the
        percentile should be calculated. Or a population list of values created
        by the distribution on which to calculate the percentile.

    :param target: The percentile_with_probability to find within the
        distribution.
    :type: float

    :param count: The number of points to use in populating the distribution
        for a standard percentile_with_probability calculation. Only matters if
        a distribution is specified, in which case the count is the size of the
        population create, which defaults to 4096. Ignored for populations as
        they already have  a count.
    :type: int
    """

    if count is None:
        count = 4096

    if hasattr(distribution_or_population, 'measurements'):
        pop = population(distribution_or_population, count=count)
    else:
        pop = distribution_or_population

    return np.percentile(pop, 100 * target)
