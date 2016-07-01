"""
This module provides functions for super-uniform sampling of the unit
hypercube. 'Super-uniform' in this context means that the obtained point
sample is more uniform than a random uniform sample, which is a desirable
property in many applications. After creation, the samples can be
transformed from the unit hypercube to arbitrary cuboids.
"""
import math
import random
import itertools

import numpy as np

from diversipy.distance import calc_euclidean_dist_matrix
from diversipy.distance import DistanceMatrixFunction



def unitcube(dimension):
    """Shortcut to generate a tuple of bounds of the unit hypercube."""
    assert dimension > 0
    return [0.0] * dimension, [1.0] * dimension



def scaled(points, from_cuboid, to_cuboid):
    """Linear transformation between arbitrary cuboids.

    This function does not check if the points are actually inside
    `from_cuboid`.

    Parameters
    ----------
    points : array_like
        2-D array of points.
    from_cuboid : tuple
        Contains lower and upper boundaries.
    to_cuboid : tuple
        Contains lower and upper boundaries.

    Returns
    -------
    scaled_points : numpy array
        A new array containing the scaled points.

    """
    # sanity checks
    min_bounds_to, max_bounds_to = to_cuboid
    assert len(min_bounds_to) == len(max_bounds_to)
    for min_bound_to, max_bound_to in zip(min_bounds_to, max_bounds_to):
        assert max_bound_to >= min_bound_to
    min_bounds_from, max_bounds_from = from_cuboid
    assert len(min_bounds_from) == len(max_bounds_from)
    for min_bound_from, max_bound_from in zip(min_bounds_from, max_bounds_from):
        assert max_bound_from >= min_bound_from
    # scale
    length_factors = (np.asarray(max_bounds_to) - min_bounds_to)
    length_factors /= (np.asarray(max_bounds_from) - min_bounds_from)
    scaled_points = (np.asarray(points) - min_bounds_from) * length_factors
    scaled_points += min_bounds_to
    return scaled_points



def grid(num_points, dimension):
    """Create conventional grid in unit hypercube.

    Also related to full factorial designs.

    Parameters
    ----------
    num_points : int
        The number of points to generate.
        ``num_points ** (1/dimension)`` must be integer.
    dimension : int
        The dimension of the space.

    Returns
    -------
    points : (`num_points`, `dimension`) numpy array

    """
    points_per_axis = int(num_points ** (1.0 / dimension))
    assert points_per_axis ** dimension == num_points
    possible_values = list(range(points_per_axis))
    divisor = points_per_axis - 1.0
    for i in range(points_per_axis):
        possible_values[i] /= divisor
    points = np.array(list(itertools.product(possible_values, repeat=dimension)))
    return points



def sukharev_grid(num_points, dimension):
    """Create Sukharev grid in unit hypercube.

    Special property of this grid is that points are not placed on the
    boundaries of the hypercube, but at centroids of the `num_points`
    subcells. This design offers optimal results for the covering radius
    regarding distances based on the max-norm.

    Parameters
    ----------
    num_points : int
        The number of points to generate.
        ``num_points ** (1/dimension)`` must be integer.
    dimension : int
        The dimension of the space.

    Returns
    -------
    points : (`num_points`, `dimension`) numpy array

    """
    points_per_axis = int(num_points ** (1.0 / dimension))
    assert points_per_axis ** dimension == num_points
    possible_values = [x + 0.5 for x in range(points_per_axis)]
    divisor = points_per_axis
    for i in range(points_per_axis):
        possible_values[i] /= divisor
    points = np.array(list(itertools.product(possible_values, repeat=dimension)))
    return points



def random_uniform(num_points, dimension):
    """Syntactic sugar for :func:`numpy.random.rand`."""
    return np.random.rand(num_points, dimension)



def halton(num_points, dimension, skip=0):
    """Generate a Halton point set.

    Quasirandom sequence using the default initialization with the first
    `dimension` prime numbers.

    Parameters
    ----------
    num_points : int
        The number of points to generate.
    dimension : int
        The dimension of the space.
    skip : int, optional
        The first `skip` points of the sequence will be left out.

    Returns
    -------
    points : (`num_points`, `dimension`) numpy array

    """
    def is_prime(number):
        number = float(number)
        if number % 2 == 0 and number != 2:
            return False
        for divisor in range(3, int(number ** 0.5) + 1, 2):
            if number % divisor == 0:
                return False
        return True

    def generator(index, base):
        result = 0
        f = 1.0 / base
        i = index
        while i > 0:
            result += f * (i % base)
            i = math.floor(i / base)
            f /= base
        return result

    bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59,
             61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131,
             137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197,
             199, 211, 223, 227, 229, 233, 239, 241, 251]
    while len(bases) < dimension:
        next_candidate = bases[-1] + 2
        while not is_prime(next_candidate):
            next_candidate += 2
        bases.append(next_candidate)
    points = []
    for i in range(skip, skip + num_points):
        point = [generator(i, bases[j]) for j in range(dimension)]
        points.append(point)
    return np.array(points)



def random_k_means(num_points,
                   dimension,
                   num_steps=None,
                   initial_points=None,
                   dist_matrix_function=None,
                   callback=None):
    """MacQueen's method.

    In its default setup, this algorithm converges to a centroidal Voronoi
    tesselation of the unit hypercube. Further information is given in
    [MacQueen1967]_.

    Parameters
    ----------
    num_points : int
        The number of points to generate.
    dimension : int
        The dimension of the space.
    num_steps : int, optional
        The number of iterations to carry out. Default is
        ``100 * num_points``.
    initial_points : array_like, optional
        The point set to improve (if None, a random uniform sample is
        drawn).
    dist_matrix_function : callable, optional
        The function to compute the distances. Default is Euclidean
        distance.
    callback : callable, optional
        If provided, it is called in each iteration with the current point
        set as argument for monitoring progress.

    Returns
    -------
    cluster_centers : (`num_points`, `dimension`) numpy array

    References
    ----------
    .. [MacQueen1967] MacQueen, J. Some methods for classification and
        analysis of multivariate observations. Proceedings of the Fifth
        Berkeley Symposium on Mathematical Statistics and Probability,
        Volume 1: Statistics, pp. 281--297, University of California Press,
        Berkeley, Calif., 1967.
        http://projecteuclid.org/euclid.bsmsp/1200512992.

    """
    # initialization
    if num_steps is None:
        num_steps = 100 * num_points
    if initial_points is None:
        cluster_centers = np.random.rand(num_points, dimension)
    elif len(initial_points) == num_points:
        cluster_centers = np.array(initial_points)
    else:
        raise ValueError("len(initial_points) must be equal to num_points")
    weights = [1.0] * num_points
    if dist_matrix_function is None:
        dist_matrix_function = calc_euclidean_dist_matrix
    # begin iteration
    for _ in range(num_steps):
        if callback is not None:
            callback(cluster_centers)
        random_point = np.random.rand(1, dimension)
        distances = dist_matrix_function(random_point, cluster_centers)
        random_point = random_point.ravel()
        nearest_index = np.argmin(distances, axis=1)
        nearest_cluster_center = cluster_centers[nearest_index, :].ravel()
        if hasattr(dist_matrix_function, "max_dists_per_dim") and dist_matrix_function.max_dists_per_dim is not None:
            one_dim_dists = np.abs(nearest_cluster_center - random_point)
            virtual_point = np.array(random_point)
            for j, dist in enumerate(one_dim_dists):
                if dist > 0.5:
                    if nearest_cluster_center[j] < 0.5:
                        virtual_point[j] = 1.0 - random_point[j]
                    else:
                        virtual_point[j] = 1.0 + random_point[j]
        else:
            virtual_point = random_point
        weight = weights[nearest_index]
        cluster_centers[nearest_index, :] = (weight * nearest_cluster_center + virtual_point) / (weight + 1.0)
        cluster_centers[nearest_index, :] %= 1.0
        assert np.all(cluster_centers[nearest_index, :] <= 1.0)
        assert np.all(cluster_centers[nearest_index, :] >= 0.0)
        weights[nearest_index] += 1.0
    return cluster_centers



def maximin_reconstruction(num_points,
                           dimension,
                           num_steps=None,
                           initial_points=None,
                           existing_points=None,
                           use_reflection_edge_correction=False,
                           dist_matrix_function=None,
                           callback=None):
    """Maximize the minimal distance in the unit hypercube with extensions.

    This algorithm carries out a user-specified number of iterations to
    maximize the minimal distance of a point in the set to 1) other points
    in the set, 2) existing (fixed) points, and 3) the boundary of the
    hypercube. Details can be found in [Wessing2015]_.

    Parameters
    ----------
    num_points : int
        The number of points to generate.
    dimension : int
        The dimension of the space.
    num_steps : int, optional
        The number of iterations to carry out. Default is
        ``100 * num_points``.
    initial_points : array_like, optional
        The point set to improve (if None, a random uniform sample is
        drawn).
    existing_points : array_like, optional
        Points that cannot be modified anymore, but should be considered in
        the distance computations.
    use_reflection_edge_correction : bool, optional
        If True, selection pressure in boundary regions will be increased by
        considering additional distances to virtual points, which are
        created by mirroring the real points at the boundary.
    dist_matrix_function : callable, optional
        The function to compute the distances. Default is Manhattan distance
        on a torus.
    callback : callable, optional
        If provided, it is called in each iteration with the current point
        set as argument for monitoring progress.

    Returns
    -------
    points : (`num_points`, `dimension`) numpy array

    References
    ----------
    .. [Wessing2015] Wessing, Simon (2015). Two-stage Methods for Multimodal
        Optimization. PhD Thesis, Technische Universitaet Dortmund.
        http://hdl.handle.net/2003/34148

    """
    def dist_to_bound(point):
        return min(point.min(), (1.0 - point).min())

    # initialization and sanity checks
    assert num_points > 0
    if num_steps is None:
        num_steps = 100 * num_points
    if initial_points is None:
        points = np.random.rand(num_points, dimension)
    elif len(initial_points) == num_points:
        points = np.array(initial_points)
        assert np.all(points >= 0.0)
        assert np.all(points <= 1.0)
    else:
        raise ValueError("len(initial_points) must be equal to num_points")
    if existing_points is None:
        existing_points = []
    existing_points = np.atleast_2d(existing_points)
    if existing_points.size == 0:
        num_existing_points = 0
    else:
        num_existing_points = len(existing_points)
    if dist_matrix_function is None:
        dist_matrix_function = DistanceMatrixFunction(exponent=1,
                                                      max_dists_per_dim=[1.0] * dimension)
    norm_of_one_vector = 2.0 * dist_matrix_function(np.atleast_2d([0.0] * dimension),
                                                    np.atleast_2d([0.5] * dimension))[0, 0]
    remaining_indices = list(range(num_points))
    random.shuffle(remaining_indices)
    removal_candidate_index = remaining_indices.pop()
    removal_candidate = points[removal_candidate_index]
    # initial distance calculations
    distances = dist_matrix_function(np.atleast_2d(removal_candidate), points)[0]
    distances[removal_candidate_index] = np.inf
    current_dist = distances.min()
    if num_existing_points > 0:
        dists_to_existing_points = dist_matrix_function(np.atleast_2d(removal_candidate),
                                                        existing_points)[0]
        current_dist = min(current_dist, dists_to_existing_points.min())
    if use_reflection_edge_correction:
        # compare with 2 * ||1|| * (distance to nearest boundary)
        relaxed_boundary_dist = 2.0 * norm_of_one_vector * dist_to_bound(removal_candidate)
        current_dist = min(current_dist, relaxed_boundary_dist)
    # maximize minimal distance
    for _ in range(num_steps):
        if callback is not None:
            callback(points)
        new_point = np.random.rand(1, dimension)
        new_dist = np.inf
        if use_reflection_edge_correction:
            # compare with 2 * ||1|| * (distance to nearest boundary)
            relaxed_boundary_dist = 2.0 * norm_of_one_vector * dist_to_bound(new_point)
            new_dist = relaxed_boundary_dist
        if new_dist >= current_dist:
            distances = dist_matrix_function(new_point, points)[0]
            distances[removal_candidate_index] = np.inf
            new_dist = min(new_dist, distances.min())
            if new_dist >= current_dist and num_existing_points > 0:
                dists_to_existing_points = dist_matrix_function(new_point, existing_points)[0]
                new_dist = min(new_dist, dists_to_existing_points.min())
        if new_dist >= current_dist:
            # accept new point
            points[removal_candidate_index] = new_point
            current_dist = new_dist
            removal_candidate = new_point
            # removal_candidate_index stays the same, but reset other indices
            remaining_indices = list(range(num_points))
            remaining_indices.remove(removal_candidate_index)
            random.shuffle(remaining_indices)
        else:
            # failed to find better point in this iteration
            if remaining_indices:
                # carry out one attempt to find new removal candidate
                removal_candidate_candidate_index = remaining_indices.pop()
                removal_candidate_candidate = points[removal_candidate_candidate_index]
                # calculate minimal distance
                distances = dist_matrix_function(np.atleast_2d(removal_candidate_candidate), points)[0]
                distances[removal_candidate_candidate_index] = np.inf
                candidate_candidate_dist = distances.min()
                if num_existing_points > 0:
                    dists_to_existing_points = dist_matrix_function(np.atleast_2d(removal_candidate_candidate),
                                                                    existing_points)[0]
                    candidate_candidate_dist = min(candidate_candidate_dist,
                                                   dists_to_existing_points.min())
                if use_reflection_edge_correction:
                    # compare with 2 * ||1|| * (distance to nearest boundary)
                    relaxed_boundary_dist = 2.0 * norm_of_one_vector
                    relaxed_boundary_dist *= dist_to_bound(removal_candidate_candidate)
                    candidate_candidate_dist = min(candidate_candidate_dist,
                                                   relaxed_boundary_dist)
                if candidate_candidate_dist <= current_dist:
                    # found new removal candidate
                    removal_candidate = removal_candidate_candidate
                    current_dist = candidate_candidate_dist
                    removal_candidate_index = removal_candidate_candidate_index
    return points



def stratified_sampling(num_points, dimension):
    """Stratified sampling in the unit hypercube.

    This algorithm divides the hypercube into `num_points` subcells and
    draws a random uniform point from each cell. Thus, the result is
    stochastic, but more uniform than a random uniform sample. For further
    information see [McKay1979]_.

    Parameters
    ----------
    num_points : int
        The number of points to generate.
        ``num_points ** (1/dimension)`` must be integer.
    dimension : int
        The dimension of the space.

    Returns
    -------
    points : (`num_points`, `dimension`) numpy array

    """
    points_per_axis = int(num_points ** (1.0 / dimension))
    assert points_per_axis ** dimension == num_points
    possible_values = [x + 0.5 for x in range(points_per_axis)]
    divisor = points_per_axis
    for i in range(points_per_axis):
        possible_values[i] /= divisor
    points = np.array(list(itertools.product(possible_values, repeat=dimension)))
    points += (np.random.rand(num_points, dimension) - 0.5) / divisor
    return points



def lhd_matrix(num_points, dimension):
    """Generate a random latin hypercube design matrix.

    Latin hypercube designs sometimes give an advantage over random uniform
    samples due to their perfect uniformity of one-dimensional projections.
    For further information see [McKay1979]_.

    Parameters
    ----------
    num_points : int
        The number of points to generate.
    dimension : int
        The dimension of the space.

    Returns
    -------
    design : (`num_points`, `dimension`) numpy array
        Contains integers corresponding to the bins of a virtual grid.

    References
    ----------
    .. [McKay1979] McKay, M.D.; Beckman, R.J.; Conover, W.J. (May 1979).
        A Comparison of Three Methods for Selecting Values of Input
        Variables in the Analysis of Output from a Computer Code.
        Technometrics 21(2): 239-245.

    """
    design = np.zeros((num_points, dimension), dtype="i")
    permutation = np.random.permutation
    for i in range(dimension):
        design[:, i] = permutation(np.arange(0, num_points))
    return design



def improved_lhd_matrix(num_points,
                        dimension,
                        num_candidates=100,
                        target_value=None,
                        dist_matrix_function=None):
    """Generate an 'improved' latin hypercube design matrix.

    This implementation uses an algorithm with quadratic run time. It is a
    greedy construction heuristic starting with a randomly chosen point.
    In each iteration, a number of random candidates is evaluated by a
    criterion that considers a candidate's distance to the previously chosen
    points. The best point according to this criterion is included in the
    LHD. The concept originally stems from [Beachkofski2002]_. The algorithm
    implemented here was proposed in [Wessing2015]_.

    Parameters
    ----------
    num_points : int
        The number of points to generate.
    dimension : int
        The dimension of the space.
    num_candidates : int, optional
        The number of random candidates considered for every point to be
        added to the LHD.
    target_value : float, optional
        The distance a candidate should ideally have to the already chosen
        points of the LHD.
    dist_matrix_function : callable, optional
        Defines the distance used. Default is Manhattan distance on a torus
        (maximum distance is ``num_points - 1``, well-suited for
        :func:`edge_lhs`).

    Returns
    -------
    design : (`num_points`, `dimension`) numpy array
        Contains integers corresponding to the bins of a virtual grid.

    References
    ----------
    .. [Beachkofski2002] Beachkofski, B.; Grandhi, R. (2002). Improved
        Distributed Hypercube Sampling. American Institute of Aeronautics
        and Astronautics Paper 1274.

    """
    # shortcuts & initialization
    dimensions = list(range(dimension))
    permutation = np.random.permutation
    if dist_matrix_function is None:
        max_dists = [num_points - 1.0] * dimension
        dist_matrix_function = DistanceMatrixFunction(exponent=1, max_dists_per_dim=max_dists)
    if target_value is None:
        target_value = np.inf
    design = np.empty((num_points, dimension), dtype="i")
    available_bins = []
    first_point = []
    bins = range(num_points)
    for _ in dimensions:
        dim_bins = list(bins)
        random.shuffle(dim_bins)
        first_point.append(dim_bins.pop())
        available_bins.append(dim_bins)
    design[0, :] = first_point
    # begin choosing other points
    for i in range(1, num_points - 1):
        # create a set of num_candidates random points obeying the LHD property
        available_bins_array = np.array(available_bins).T
        num_available = float(num_points - i)
        duplication_factor = int(math.ceil(num_candidates / num_available))
        candidates = np.vstack([available_bins_array] * duplication_factor)
        for dim in dimensions:
            candidates[:, dim] = permutation(candidates[:, dim])
        # calculate distances to already chosen points
        distances = dist_matrix_function(design[0:i, :], candidates[0:num_candidates, :])
        min_dists = distances.min(axis=0)
        # select best point according to distance criterion
        if not math.isinf(target_value):
            selected_index = np.argmin(np.abs(min_dists - target_value))
        else:
            selected_index = np.argmax(min_dists)
        selected_point = candidates[selected_index, :]
        design[i, :] = selected_point
        # maintain bin data structure
        for value, avail in zip(selected_point, available_bins):
            avail.remove(value)
    last_point = [avail.pop() for avail in available_bins]
    for avail in available_bins:
        assert not avail  # should be empty
    design[-1, :] = last_point
    return design



def has_lhd_property(design_matrix):
    """Check if design matrix has the LHD property.

    It is assumed that counting starts from zero and points are arranged
    row-wise. So, each column must consist of a permutation of
    ``range(num_points)``.

    Parameters
    ----------
    design_matrix : array_like
        2-D array of integer coordinates.

    Returns
    -------
    is_lhd : bool

    """
    design_matrix = np.asarray(design_matrix)
    num_points, dimension = design_matrix.shape
    required_numbers = list(range(num_points))
    for i in range(dimension):
        ith_column = design_matrix[:, i].tolist()
        if required_numbers != sorted(ith_column):
            return False
    return True



def perturbed_lhs(design_matrix):
    """Transform a design matrix into a sample in the unit hypercube.

    Applies random perturbations so that each point is distributed randomly
    uniform in its grid cell. This is the variant proposed by [McKay1979]_.
    It is not checked if `design_matrix` actually is a LHD.

    Parameters
    ----------
    design_matrix : array_like
        Array containing integers to indicate the bins occupied by each
        point.

    Returns
    -------
    points : (`num_points`, `dimension`) numpy array

    """
    design_matrix = np.asarray(design_matrix)
    num_points, num_dimensions = design_matrix.shape
    # make a copy
    points = design_matrix + np.random.rand(num_points, num_dimensions)
    points /= float(num_points)
    return points



def centered_lhs(design_matrix):
    """Transform a design matrix into a sample in the unit hypercube.

    Each point is placed at the centroid of a subcell in the assumed grid
    over the cube. It is not checked if `design_matrix` actually is a LHD.

    Parameters
    ----------
    design_matrix : array_like
        Array containing integers to indicate the bins occupied by each
        point.

    Returns
    -------
    points : (`num_points`, `dimension`) numpy array

    """
    design_matrix = np.asarray(design_matrix)
    num_points, _ = design_matrix.shape
    # make a copy
    points = design_matrix + 0.5
    points /= float(num_points)
    return points



def edge_lhs(design_matrix):
    """Transform a design matrix into a sample in the unit hypercube.

    The transformation is so that each face of the hypercube is sampled by
    exactly one point. Use this transformation if you want to maximize the
    minimal distance between points in the design. It is not checked if
    `design_matrix` actually is a LHD.

    Parameters
    ----------
    design_matrix : array_like
        Array containing integers to indicate the bins occupied by each
        point.

    Returns
    -------
    points : (`num_points`, `dimension`) numpy array

    """
    design_matrix = np.asarray(design_matrix)
    num_points, _ = design_matrix.shape
    # make a copy
    points = np.array(design_matrix, dtype="d")
    points /= (num_points - 1.0)
    return points
