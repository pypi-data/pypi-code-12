"""
This module contains several functions to measure diversity and a few
related concepts. The diversity indicators all have different advantages and
disadvantages. An overview is given in [Wessing2015]_.

"""
import math

import numpy as np

from diversipy.distance import calc_euclidean_dist_matrix
from diversipy.distance import calc_dists_to_boundary



def solow_polasky_diversity(points, activity_param=1.0, dist_matrix_function=None):
    """Calculate the Solow-Polasky diversity for a set of points.

    This diversity indicator was introduced in [Solow1994]_ and is to be
    maximized. The algorithm has cubic run time, because the pseudoinverse
    of a correlation matrix has to be computed. The assumed correlation
    function is ``exp(-activity_param * dist)``.

    Parameters
    ----------
    points : array_like
        2-D data structure holding the points.
    activity_param : float, optional
        Parameter controlling the strength of correlation. It must hold
        ``0 < activity_param <= 2``. Default is 1.
    dist_matrix_function : callable, optional
        A metric distance function. Default is Euclidean distance.

    Returns
    -------
    diversity : float

    References
    ----------
    .. [Solow1994]  Solow, Andrew R.; Polasky, Stephen (1994). Measuring
        biological diversity. Environmental and Ecological Statistics,
        Vol. 1, No. 2, pp. 95-103. https://dx.doi.org/10.1007/BF02426650

    """
    if len(points) == 0:
        return 0.0
    if dist_matrix_function is None:
        dist_matrix_function = calc_euclidean_dist_matrix
    points = np.asarray(points)
    dist_matrix = dist_matrix_function(points, points)
    correlation_matrix = np.exp(-activity_param * dist_matrix)
    try:
        # compute pseudoinverse
        inverse_matrix = np.linalg.pinv(correlation_matrix)
    except np.linalg.linalg.LinAlgError:
        return 0.0
    return inverse_matrix.sum()



def weitzman_diversity(points, dist_matrix_function=None):
    """Calculate the Weitzman diversity for a set of points.

    This diversity indicator was introduced in [Weitzman1992]_. It is to be
    maximized.

    .. warning:: This implementation has exponential run time in the number
                 of points!

    Parameters
    ----------
    points : array_like
        2-D data structure holding the points.
    dist_matrix_function : callable, optional
        An arbitrary distance function. Default is Euclidean distance.

    Returns
    -------
    diversity : float

    References
    ----------
    .. [Weitzman1992] Weitzman, Martin L. (May 1992). On Diversity. The
        Quarterly Journal of Economics, Vol. 107, No. 2, pp. 363-405
        https://www.jstor.org/stable/2118476

    """
    def diversity_recursive(indices, dist_matrix):
        num_points = len(indices)
        if num_points == 1:
            # end of recursion
            return 1.0
        # find minimal distance
        min_dist = float("inf")
        min_dist_pair = None, None
        for i in range(num_points):
            index_i = indices[i]
            for j in range(i + 1, num_points):
                distance = dist_matrix[index_i, indices[j]]
                if distance < min_dist:
                    min_dist = distance
                    min_dist_pair = (i, j)
        a, b = min_dist_pair
        # prepare for recursive calls
        indices_without_a = indices[:]
        del indices_without_a[a]
        indices_without_b = indices[:]
        del indices_without_b[b]
        diversity_without_a = diversity_recursive(indices_without_a, dist_matrix)
        diversity_without_b = diversity_recursive(indices_without_b, dist_matrix)
        if diversity_without_a > diversity_without_b:
            return min_dist + diversity_without_a
        else:
            return min_dist + diversity_without_b

    num_points = len(points)
    if num_points == 0:
        return 0.0
    if dist_matrix_function is None:
        dist_matrix_function = calc_euclidean_dist_matrix
    points = np.asarray(points)
    dist_matrix = dist_matrix_function(points, points)
    return diversity_recursive(list(range(num_points)), dist_matrix)



def sum_of_dists(points, dist_matrix_function=None):
    """Calculate the square root of the sum of all pairwise distances.

    This indicator is to be maximized.

    .. warning:: This function is only included here for comparisons. It is
        actually not well suited as diversity indicator, as explained in
        [Solow1994]_.

    Parameters
    ----------
    points : array_like
        2-D data structure holding the points.
    dist_matrix_function : callable, optional
        An arbitrary distance function. Default is Euclidean distance.

    Returns
    -------
    spread : float

    """
    num_points = len(points)
    if num_points == 0:
        return 0.0
    if dist_matrix_function is None:
        dist_matrix_function = calc_euclidean_dist_matrix
    points = np.asarray(points)
    dist_matrix = dist_matrix_function(points, points)
    spread = math.sqrt(dist_matrix.sum() * 0.5)
    return spread



def average_inverse_dist(points, exponent=None, max_dist=1.0, dist_matrix_function=None):
    """Calculate the average inverse distance.

    For each pair of points, the value ``(max_dist / dist) ** exponent`` is
    computed. The average of all these values is the indicator value, which
    is to be minimized.

    Parameters
    ----------
    points : array_like
        2-D data structure holding the points.
    exponent : int or float, optional
        Exponent in the calculations explained above. Default is
        ``dimension + 1``.
    max_dist : float, optional
        Maximally possible distance or an arbitrary constant.
    dist_matrix_function : callable, optional
        An arbitrary distance function. Default is Euclidean distance.

    Returns
    -------
    diversity : float

    """
    num_points = len(points)
    if num_points < 2:
        return 0.0
    points = np.asarray(points)
    num_points, dimension = points.shape
    if exponent is None:
        exponent = dimension + 1
    if dist_matrix_function is None:
        dist_matrix_function = calc_euclidean_dist_matrix
    dist_matrix = dist_matrix_function(points, points)
    sum_of_inv_dists = 0.0
    num_zeros = 0
    for i in range(num_points):
        for j in range(i + 1, num_points):
            distance = dist_matrix[i, j]
            if distance == 0.0:
                num_zeros += 1
            else:
                sum_of_inv_dists += (max_dist / distance) ** exponent
    if num_zeros > 0:
        return float("inf")
    else:
        num_dists = num_points * (num_points - 1) / 2.0
        return sum_of_inv_dists ** (1.0 / exponent) / num_dists



def separation_dist(points, dist_matrix_function=None):
    """Calculate the minimal pairwise distance.

    This indicator is to be maximized.

    Parameters
    ----------
    points : array_like
        2-D data structure holding the points.
    dist_matrix_function : callable, optional
        An arbitrary distance function. Default is Euclidean distance.

    Returns
    -------
    min_dist : float

    """
    num_points = len(points)
    if num_points < 2:
        return 0.0
    points = np.asarray(points)
    if dist_matrix_function is None:
        dist_matrix_function = calc_euclidean_dist_matrix
    dist_matrix = dist_matrix_function(points, points)
    for i in range(num_points):
        dist_matrix[i, i] = np.inf
    min_dist = dist_matrix.min()
    return min_dist



def sum_of_nn_dists(points, dist_matrix_function=None):
    """Calculate the sum of nearest-neighbor distances

    This indicator is to be maximized.

    Parameters
    ----------
    points : array_like
        2-D data structure holding the points.
    dist_matrix_function : callable, optional
        An arbitrary distance function. Default is Euclidean distance.

    Returns
    -------
    sum_of_nn_dists : float

    """
    num_points = len(points)
    if num_points < 2:
        return 0.0
    points = np.asarray(points)
    if dist_matrix_function is None:
        dist_matrix_function = calc_euclidean_dist_matrix
    dist_matrix = dist_matrix_function(points, points)
    for i in range(num_points):
        dist_matrix[i, i] = np.inf
    nn_dists = dist_matrix.min(axis=0)
    return nn_dists.sum()







def unanchored_L2_discrepancy(points):
    """Calculate unanchored L2 discrepancy.

    Discrepancy is to be minimized. Note that the square root is already
    taken. Coordinates of points must be >=0 and <=1. Run time is quadratic.
    For details see [Morokoff1994]_.

    Parameters
    ----------
    points : array_like
        2-D data structure holding the points.

    Returns
    -------
    discrepancy : float

    References
    ----------
    .. [Morokoff1994] Morokoff, William J.; Caflisch, Russel E. (1994).
        Quasi-random sequences and their discrepancies. SIAM Journal on
        Scientific Computing, Vol. 15, No. 6, pp. 1251-1279.
        https://dx.doi.org/10.1137/0915077

    """
    if len(points) == 0:
        return 0.0
    points = np.asarray(points)
    assert np.all(points >= 0.0)
    assert np.all(points <= 1.0)
    num_points, dimension = points.shape
    num_batches = int(math.ceil(num_points / 1000.0))
    part1_sum = 0.0
    for j in range(num_batches):
        lo1 = j * 1000
        hi1 = (j + 1) * 1000
        for k in range(j, num_batches):
            lo2 = k * 1000
            hi2 = (k + 1) * 1000
            part1_matrix = (1.0 - np.maximum(points[lo1:hi1, 0, None], points[lo2:hi2, 0]))
            part1_matrix *= np.minimum(points[lo1:hi1, 0, None], points[lo2:hi2, 0])
            for i in range(1, dimension):
                part1_matrix *= (1.0 - np.maximum(points[lo1:hi1, i, None], points[lo2:hi2, i]))
                part1_matrix *= np.minimum(points[lo1:hi1, i, None], points[lo2:hi2, i])
            batch_sum = part1_matrix.sum()
            part1_sum += batch_sum
            if j != k:
                part1_sum += batch_sum
    del part1_matrix
    part2_sum = np.sum((points * (1.0 - points)).prod(axis=1))
    result = part1_sum / num_points ** 2.0
    result -= part2_sum * (2.0 ** (1.0 - dimension) / num_points)
    result += 12 ** -dimension
    return math.sqrt(result)



def expected_unanchored_L2_discrepancy(num_points, dimension):
    """Expected value for unanchored L2 discrepancy of random uniform points.

    Note that this is the square root of :math:`\\mathrm{E}(T^2)`, i.e.
    ``sqrt(1.0 / n * (6 ** -d) * (1 - 2 ** -d))``. For details see
    [Morokoff1994]_.

    """
    assert num_points > 0
    assert dimension > 0
    return math.sqrt(1.0 / num_points * (6 ** -dimension) * (1 - 2 ** -dimension))



def mean_dist_to_boundary(points):
    """Calculate the mean distance to the boundary of this point set."""
    if len(points) == 0:
        return 0.0
    points = np.asarray(points)
    assert np.all(points >= 0.0)
    assert np.all(points <= 1.0)
    dists = calc_dists_to_boundary(points)
    return np.mean(dists)



def expected_dist_to_boundary(dimension):
    """The expected distance to the boundary for random uniform points."""
    assert dimension > 0
    return 0.5 / (1 + dimension)



def averaged_hausdorff_dist(points1, points2, exponent=1, dist_matrix_function=None):
    """Calculate the averaged Hausdorff distance between two point sets.

    As defined in the paper [Schuetze2012]_.

    Parameters
    ----------
    points1 : array_like
        2-D data structure holding the first set.
    points2 : array_like
        2-D data structure holding the second set.
    exponent : int, optional
        An exponent to control the penalization of outliers (the higher the
        larger the exponent is).
    dist_matrix_function : callable, optional
        An arbitrary distance function. Default is Euclidean distance.

    Returns
    -------
    ahd : float

    References
    ----------
    .. [Schuetze2012] Schuetze, O.; Esquivel, X.; Lara, A.; Coello Coello,
        Carlos A. (2012). Using the Averaged Hausdorff Distance as a
        Performance Measure in Evolutionary Multiobjective Optimization.
        IEEE Transactions on Evolutionary Computation, Vol.16, No.4,
        pp. 504-522. https://dx.doi.org/10.1109/TEVC.2011.2161872

    """
    if math.isinf(exponent):
        return hausdorff_dist(points1, points2, dist_matrix_function)
    points1 = np.asarray(points1)
    num_points, dimension = points1.shape
    assert num_points > 0 and dimension > 0
    points2 = np.asarray(points2)
    num_points, dimension = points2.shape
    assert num_points > 0 and dimension > 0
    if dist_matrix_function is None:
        dist_matrix_function = calc_euclidean_dist_matrix
    dist_matrix = dist_matrix_function(points1, points2)
    min_dists1 = dist_matrix.min(axis=0)
    min_dists2 = dist_matrix.min(axis=1)
    part1 = (min_dists1 ** exponent).sum() / len(min_dists1) ** (1.0 / exponent)
    part2 = (min_dists2 ** exponent).sum() / len(min_dists2) ** (1.0 / exponent)
    ahd = max(part1, part2)
    return ahd



def hausdorff_dist(points1, points2, dist_matrix_function=None):
    """Calculate the Hausdorff distance between two point sets.

    Parameters
    ----------
    points1 : array_like
        2-D data structure holding the first set.
    points2 : array_like
        2-D data structure holding the second set.
    dist_matrix_function : callable, optional
        An arbitrary distance function. Default is Euclidean distance.

    Returns
    -------
    hd_dist : float

    """
    points1 = np.asarray(points1)
    num_points, dimension = points1.shape
    assert num_points > 0 and dimension > 0
    points2 = np.asarray(points2)
    num_points, dimension = points2.shape
    assert num_points > 0 and dimension > 0
    if dist_matrix_function is None:
        dist_matrix_function = calc_euclidean_dist_matrix
    dist_matrix = dist_matrix_function(points1, points2)
    min_dists1 = dist_matrix.min(axis=0)
    min_dists2 = dist_matrix.min(axis=1)
    hd_dist = max(min_dists1.max(), min_dists2.max())
    return hd_dist
