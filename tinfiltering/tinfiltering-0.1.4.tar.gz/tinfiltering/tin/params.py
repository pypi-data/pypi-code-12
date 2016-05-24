# -*- coding: utf-8 -*-
"""
Module created to perform the calculation of parameters, based on the edge
distances of the triangles in a given triangulation.

@author: Matheus Boni Vicari (matheus.boni.vicari@gmail.com)
"""

import numpy
import collections
from scipy.spatial.distance import euclidean


# Defining the criterion_function function.
def criterion_function(neighbors, edge_distances, point_data):

    """
    The criterion_function performs the calculation of F, the criterion
    function, which is used in the tin_filtering package. For more information
    about the idea behind the criterion function and how it's applied into the
    TIN filtering, refere to Yang and Cui (2010).

    Parameters
    ----------
    neighbors: collections.defaultdict
            Sets of neighboring nodes for each node in the triangulation.
    e_dist: numpy.ndarray
            Distance between every pair of neighboring nodes (edges).
    point_data: numpy.ndarray
            x and y coordinates from the input set of points.

    Returns
    -------
    F: numpy.ndarray
            Criterion function for the evaluated triangulation.

    Raises
    ------
    TypeError
        If input is the wrong type.

    Usage
    -----
    >>> F = params.criterion_function(neighbors, edge_distances, point_data)

    References
    ----------
    .. [1] X. Yang and W. Cui, "A Novel Spatial Clustering Algorithm Based on
           Delaunay Triangulation," Journal of Software Engineering and
           Applications, Vol. 3 No. 2, 2010, pp. 141-149. doi:
           10.4236/jsea.2010.32018.
    """

    # Check the input variables.
    if type(neighbors) is not collections.defaultdict:

        raise TypeError("Input must be of type scipy.spatial.qhull.Delaunay.")

    elif type(point_data) is not numpy.ndarray:

        raise TypeError("Input must be of type numpy.ndarray.")

    elif type(edge_distances) is not numpy.ndarray:

        raise TypeError("Input must be of type numpy.ndarray.")

    # Executing the anciliary functions to obtain the output variables.
    local_mean = local_mean_distance(neighbors, point_data)
    global_mean = global_mean_distance(edge_distances)
    global_std = global_sta_dev(edge_distances)

    # Calculating the criterion function based on the work from Yang and Cui
    # (2010).
    F = global_mean + global_std * (global_mean / local_mean)

    return F


# Defining the global_sta_dev function.
def global_sta_dev(edge_distances):

    """
    The global_sta_dev function calculates the standard deviation of the set
    of edge distances (edge_distances) in the triangulation.

    Parameters
    ----------
    edge_distances: numpy.ndarray
            Distance between every pair of neighboring nodes (edges).

    Returns
    -------
    global_sta_dev: numpy.float64
            Standard deviation of all the edges distances in the triangulation.

    Usage
    -----
    >>> global_std_distance = params.global_sta_dev(edge_distances)

    """

    # Calculating the standard deviation from the array of edge distances.
    global_sta_dev = numpy.std(edge_distances)

    return global_sta_dev


# Defining the global_mean_distance function.
def global_mean_distance(edge_distances):

    """
    The global_mean_distance function calculates the global mean distance,
    that being the mean distance of all edges in the triangulation.

    Parameters
    ----------
    edge_distances: numpy.ndarray
            Distance between every pair of neighboring nodes (edges).

    Returns
    -------
    global_mean_distance: numpy.float64
            Mean distance of all the edges distances in the triangulation.

    Usage
    -----
    >>> global_mean_distance = params.global_mean_distance(edge_distances)

    """

    # Calculating the mean distance from the array of edge distances.
    global_mean_distance = numpy.mean(edge_distances)

    return global_mean_distance


# Defining the local_mean_distance function.
def local_mean_distance(neighbors, points):

    """
    The local_mean_distance function calculates the local mean distance, that
    is, the mean distance of all edges around a node in the triangulation. In
    this sense, every node shall have a local mean distance value based on the
    distance from its neighbors.

    Parameters
    ----------
    neighbors: collections.defaultdict
            Sets of neighboring nodes for each node in the triangulation.
    point_data: numpy.ndarray
            x and y coordinates from the input set of points.

    Returns
    -------
    local_mean_distance: numpy.ndarray
            Local mean distance of every node in the triangulation.

    Usage
    -----
    >>> local_mean_distance = params.local_mean_distance(neighbors,\
 point_data)
    """

    # Initializating the output variable as an array of zeros with the same
    # length as the 'neighbors' variable.
    local_mean_distance = numpy.zeros(len(neighbors))

    # Looping over the set of nodes in the triangulation.
    for start_id in neighbors:

        # Setting the temp_dist variable to an empty list.
        temp_dist = []

        # Looping over each neighbor for the current node.
        for end_id in neighbors[start_id]:

            # Calculating the edge distance for the current edge and appending
            # it to the temporary list 'temp_dist'
            temp_dist.append(euclidean(points[start_id], points[end_id]))

        # Assignin the temp_dist list for the current node into the output
        # variable.
        local_mean_distance[start_id] = numpy.mean(temp_dist)

    return local_mean_distance
