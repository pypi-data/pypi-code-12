"""
Basic infrastructure for DFO methods.
"""

import math


INFINITY = float("inf")


def create_standard_basis(dimension, scale_factor=1.0):
    """Create an orthogonal, maximal, positive basis."""
    assert dimension >= 1
    assert scale_factor > 0.0
    pattern = []
    for i in range(dimension):
        for offset in (scale_factor, -scale_factor):
            vector = [0.0] * dimension
            vector[i] = offset
            pattern.append(vector)
    return pattern



def create_std_basis_simplex(position, side_length=1.0):
    """Create a simplex based on the standard basis of Euclidean space.

    Parameters
    ----------
    position : iterable
        The position being used as location vector for the simplex. In this
        construction, `position` is also a vertex in the simplex.
    side_length : float, optional
        The side length of the basis vectors.

    Returns
    -------
    simplex : list of list
        A list containing ``len(position) + 1`` points.

    """
    assert len(position) > 0
    assert side_length > 0.0
    simplex = [list(position)]
    for i in range(len(position)):
        point = list(position)
        point[i] += side_length
        simplex.append(point)
    return simplex



def create_regular_simplex(position, side_length=1.0):
    """Create a regular simplex.

    Parameters
    ----------
    position : iterable
        The position being used as location vector for the simplex. In this
        construction, `position` is the centroid of the simplex.
    side_length : float, optional
        The side length of all edges of the simplex.

    Returns
    -------
    simplex : list of list
        A list containing ``len(position) + 1`` points.

    """
    assert len(position) > 0
    assert side_length > 0.0
    dimension = len(position)
    sqrt = math.sqrt
    # assume some distance between vertices
    distance = 1.0
    dist_squared = distance ** 2
    # begin with simplex in one dimension
    simplex = [[-0.5 * distance], [0.5 * distance]]
    current_dim = 1
    while current_dim < dimension:
        center = center_of_mass(simplex)
        diff_vector = [center[i] - simplex[0][i] for i in range(current_dim)]
        dist_squared_center_to_corner = sum(x * x for x in diff_vector)
        pyramid_height = sqrt(dist_squared - dist_squared_center_to_corner)
        for vector in simplex:
            vector.append(0.0)
        center.append(pyramid_height)
        simplex.append(center)
        current_dim += 1
    final_center = center_of_mass(simplex)
    simplex = scale(simplex, final_center, side_length)
    # shift to final offset vector
    for vector in simplex:
        for i in range(dimension):
            vector[i] -= final_center[i]
            vector[i] += position[i]
    return simplex



def displace(point1, point2, factor):
    """Displace `point1` by ``factor * (point1 - point2)``.

    Parameters
    ----------
    point1 : iterable
        The position vector.
    point2 : iterable
        The second vector necessary to calculate the displacement vector.
    factor : float
        The scale factor.

    Returns
    -------
    new_point : list
        The displaced point.

    """
    dim = len(point1)
    new_point = [None] * dim
    coeff1 = 1.0 + factor
    for i in range(dim):
        new_point[i] = coeff1 * point1[i] - factor * point2[i]
    return new_point



def center_of_mass(points):
    """Calculate the center of mass of the given points."""
    dim = len(points[0])
    center = [0.0] * dim
    for i in range(dim):
        center[i] = math.fsum(point[i] for point in points)
        center[i] /= len(points)
    return center



def scale(points, fixed_point, factor):
    """Scale a point cloud by a given factor.

    Parameters
    ----------
    points : iterable of iterable
        The points to scale.
    fixed_point : iterable
        The fixed point of the transformation.
    factor : float
        The scale factor.

    Returns
    -------
    scaled_points : list of list
        List containing scaled points.

    """
    scaled_points = []
    for point in points:
        new_point = displace(point, fixed_point, -1.0 + factor)
        scaled_points.append(new_point)
    return scaled_points



def lexicographic_sort_key(individual):
    """Sort key for lexicographic sorting with special treatment of None.

    None is replaced with infinity (the worst possible value).

    """
    try:
        iter(individual.objective_values)
        key = []
        for objective in individual.objective_values:
            if objective is None:
                objective = INFINITY
            key.append(objective)
    except TypeError:
        key = individual.objective_values
        if key is None:
            key = INFINITY
    return key



class Observable(object):
    """Part of the Observer/Observable design pattern."""

    def __init__(self):
        self.observers = []


    def attach(self, observer):
        """Add observer to the list of observers.

        Parameters
        ----------
        observer : callable
            The object to be informed about changes.

        """
        if observer not in self.observers:
            self.observers.append(observer)


    def detach(self, observer):
        """Remove observer from the list of observers.

        Parameters
        ----------
        observer : callable
            The object to be informed about changes.

        """
        try:
            self.observers.remove(observer)
        except ValueError:
            pass


    def notify_observers(self):
        """Inform the observers about a potential state change."""
        for observer in self.observers:
            observer(self)



def order(values, sort_key=None):
    """Return the ordering of the elements of `values`.

    The list ``[values[j] for j in order(values)]`` is a sorted version of
    `values`.

    Adapted from
    https://code.activestate.com/recipes/491268-ordering-and-ranking-for-lists/

    Parameters
    ----------
    values : list
        The list to process
    sort_key : callable, optional
        A callable to determine the ordering. Default sort key is
        ``(value is None, value)``.

    Returns
    -------
    order : list
        The indices the values would have in a sorted list.

    """
    def default_sort_key(argument):
        return argument is None, argument

    if sort_key is None:
        sort_key = default_sort_key
    decorated = [(sort_key(value), i) for i, value in enumerate(values)]
    decorated.sort()
    indices = [index for _, index in decorated]
    return indices



def rank(values, sort_key=None, ties="average"):
    """Return the ranking of the elements of `values`.

    The best obtainable rank is 1. Calls the function :func:`order`.

    Adapted from
    https://code.activestate.com/recipes/491268-ordering-and-ranking-for-lists/

    Parameters
    ----------
    values : list
        The list to process
    sort_key : callable, optional
        A callable to determine the ordering. Default sort key is
        ``(value is None, value)``.
    ties : string
        The tie-breaking criterion. Choices are: "first", "average", "min",
        and "max".

    Returns
    -------
    ranks : list
        The ranks of the values in the same order.

    """
    def default_sort_key(argument):
        return argument is None, argument

    if sort_key is None:
        sort_key = default_sort_key
    ordered_indices = order(values, sort_key)
    ranks = ordered_indices[:]
    num_values = len(ordered_indices)
    for i in range(num_values):
        ranks[ordered_indices[i]] = i + 1
    if ties == "first":
        return ranks
    elif ties not in ["first", "average", "min", "max"]:
        raise Exception("unknown tie breaking")

    blocks = []
    new_block = []
    for i in range(1, num_values):
        key1 = sort_key(values[ordered_indices[i]])
        key2 = sort_key(values[ordered_indices[i - 1]])
        if key1 == key2:
            if i - 1 not in new_block:
                new_block.append(i)
            new_block.append(i + 1)
        else:
            if len(new_block) > 0:
                blocks.append(new_block)
                new_block = []
    if len(new_block) > 0:
        blocks.append(new_block)

    for i, block in enumerate(blocks):
        if ties == "average":
            value = sum(block) / float(len(block))
        elif ties == "min":
            value = min(block)
        elif ties == "max":
            value = max(block)
        for j in block:
            ranks[ordered_indices[j - 1]] = value
    return ranks
