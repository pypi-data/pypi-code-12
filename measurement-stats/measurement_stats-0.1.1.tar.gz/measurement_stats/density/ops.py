from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import random
from operator import itemgetter

import numpy as np

from measurement_stats import value


def percentile(distribution, target=0.5, tolerance=1e-6):
    """
    Computes the position along the measurement axis where the distribution
    reaches the given target percentile. The computation is carried out
    using a numerical integrator, which requires a tolerance where it can
    determine success and return

    :param distribution: The distribution for which the percentile should be
        calculated.
    :type: refined_stats.density.Distribution

    :param target: The percentile to find within the distribution.
    :type: float

    :param tolerance: The threshold below which the function will declare
        success and return
    :type: float

    :return: A dictionary with the keys:
        * x: Position along the measurement (x) axis where the cumulative
             probability of the distribution reaches the target percentile
        * y: Value of the probability function at that point
        * target: Percentile value that was achieved by integration, which
            will be within the tolerance threshold of the target value unless
            the integration convergence took too long and was aborted early.
    :rtype: dict
    """

    x_values = uniform_range(distribution, max_sigma=10.0, num_points=2048)

    area = 0.0
    x = x_values[0]
    dx = 0

    for i in range(len(x_values) - 1):
        x = x_values[i]
        xn = x_values[i + 1]
        dx = xn - x
        y = distribution.probability_at(x)
        yn = distribution.probability_at(xn)
        new_area = area + dx * (y + 0.5 * abs(yn - y))

        if value.equivalent(new_area, target, tolerance):
            return dict(
                x=xn,
                y=yn,
                target=new_area
            )

        elif new_area > target:
            break
        else:
            area = new_area

    ratio = 0.5
    ratio_min = 0.0
    ratio_max = 1.0

    for i in range(10000):
        dx_piece = ratio * dx
        xn = x + dx_piece
        yn = distribution.probability_at(xn)
        area_extension = dx_piece * (y + 0.5 * abs(yn - y))
        test = area + area_extension

        if value.equivalent(test, target, tolerance):
            return dict(
                x=xn,
                y=yn,
                target=test
            )

        if test < target:
            ratio_min = max(ratio_min, ratio)
        elif test > target:
            ratio_max = min(ratio_max, ratio)

        ratio *= (target - area) / area_extension
        if ratio_max <= ratio <= ratio_min:
            ratio = ratio_min + 0.5*(ratio_max - ratio_min)

    raise ValueError('Unable to find percentile value')


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
