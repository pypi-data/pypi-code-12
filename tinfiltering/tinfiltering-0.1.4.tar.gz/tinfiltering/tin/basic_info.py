# -*- coding: utf-8 -*-
"""
Module created to perform the extraction of nodes and edges information from
a Delaunay triangulation of type scipy.spatial.qhull.Delaunay.

@author: Matheus Boni Vicari (matheus.boni.vicari@gmail.com)
"""

import numpy
import scipy
from collections import defaultdict
from scipy.spatial.distance import euclidean


# Defining the tri_info function.
def tri_info(tri, point_data):

    """
    The tri_info function retrieves the information from the Delaunay
    triangulation by running the anciliary functions defined within this
    module.

    Parameters
    ----------
    tri: scipy.spatial.qhull.Delaunay
            Delaunay triangulation generated from the point_data variable.
    point_data: numpy.ndarray
            x and y coordinates from the input set of points.

    Returns
    -------
    neighbors: collections.defaultdict
            Sets of neighboring nodes for each node in the triangulation.
    n_degree: numpy.ndarray
            Degree of each node in the triangulation.
    n_id: numpy.ndarray
            Indices for the nodes in the triangulation.
    e_dist: numpy.ndarray
            Distance between every pair of neighboring nodes (edges).
    e_id: numpy.ndarray
            Indices for each edge in the triangulation.

    Raises
    ------
    TypeError
        If input is of the wrong data type.

    Usage
    -----
    >>> neighbors, n_degree, n_id, e_dist, e_id = basic_info.tri_info(tri,\
 point_data)

    """

    # Check the input variables.
    if type(tri) is not scipy.spatial.qhull.Delaunay:

        raise TypeError("Input must be of type scipy.spatial.qhull.Delaunay.")

    elif type(point_data) is not numpy.ndarray:

        raise TypeError("Input must be of type numpy.ndarray.")

    # Executing the find_neighbors, node_degree and edge_distances functions
    # to obtain the output variables.
    neighbors = find_neighbors(tri)
    n_degree, n_id = node_degree(neighbors)
    e_dist, e_id = edge_distances(neighbors, point_data)

    return neighbors, n_degree, n_id, e_dist, e_id


# Defining the edge_distances function.
def edge_distances(neighbors, point_data):

    """
    This function calculates the Euclidean distance between every neighboring
    pair of nodes in the triangulation.

    Parameters
    ----------
    neighbors: collections.defaultdict
            Sets of neighboring nodes for each node in the triangulation.
    point_data: numpy.ndarray
            x and y coordinates from the input set of points.

    Returns
    -------
    edge_dist: numpy.ndarray
            Distance between every pair of neighboring nodes (edges).
    edge_id: numpy.ndarray
            Indices for each edge in the triangulation.

    See also
    --------
    scipy.spatial.distance.euclidean: Computes the Euclidean distance between
    two 1-D arrays.

    Usage
    -----
    >>> edge_dist, edge_id = basic_info.edge_distances(neighbors, point_data)

    """

    # Initializating the output variables edge_dist and edge_id.
    edge_dist = numpy.zeros(numpy.sum([len(idx) for idx in
                            neighbors.values()]))
    edge_id = defaultdict(set)

    # Setting the counter to 0, as it will be used later on the indexing of
    # the edge_dist variable.
    count = 0

    # Looping over the node sets of neighbors.
    for start_id in neighbors:

        # Setting the temp_id variable to empty list.
        temp_id = []

        # Looping over all neighbors for each node.
        for end_id in neighbors[start_id]:

            # Calculating the euclidean distance between the current pair
            # node-neighbor,
            edge_dist[count] = euclidean(point_data[start_id],
                                         point_data[end_id])
            # Appending the count value to the id list.
            temp_id.append(count)

            # Incrementing the counter.
            count += 1

        # Assigning the temp_id variable to the current node position on the
        # edge_id varible.
        edge_id[start_id] = temp_id

    return edge_dist, edge_id


# Defining the node_degree function.
def node_degree(neighbors):

    """
    The node_degree function performs the calculation of the node degree for
    each node in the triangulation. The node degree is the total amount of
    neighbors of each node.

    Parameters
    ----------
    neighbors: collections.defaultdict
            Sets of neighboring nodes for each node in the triangulation.

    Returns
    -------
    node_degree: numpy.ndarray
            Degree of each node in the triangulation.
    node_id: numpy.ndarray
            Indices for the nodes in the triangulation.

    Usage
    -----
    >>> node_degree, node_id = basic_info.node_degree(neighbors)

    """

    # Initializating the output variables as arrays of zeros with the same
    # length as the input variable 'neighbors'.
    node_id = numpy.zeros(len(neighbors))
    node_degree = numpy.zeros(len(neighbors))

    # Looping over the amount of sets inside the variable 'neighbors'.
    for node in range(len(neighbors)):

        # Assigning the node_id variable the node instance value.
        node_id[node] = node
        # Assigning the node_degree variable the total amount (length) of
        # values inside the node's set of neighbors. This is equivalent of the
        # count of all neighboring nodes, which is defined as the node degree.
        node_degree[node] = len(neighbors[node])

    return node_degree, node_id


# Defining the find_neighbors function.
def find_neighbors(tri):

    """
    The find_neighbors function performes the listing of all the neighboring
    nodes for each node in the triangulation. It is based on an idea provided
    at stackoverflow about listing the neighboring points of triangulation
    nodes.

    Parameters
    ----------
    tri: scipy.spatial.qhull.Delaunay
            Delaunay triangulation generated from the point_data variable.

    Returns
    -------
    neighbors: collections.defaultdict
            Sets of neighboring nodes for each node in the triangulation.

    Reference
    ---------
    .. [1] Answers provided by astrofrog and glyg at https://stackoverflow.\
com/questions/12374781/how-to-find-all-neighbors-of-a-given-point-in-a-\
delaunay-triangulation-using-sci/17811731.

    See also
    --------
    scipy.spatial: spatial algorithms and data structures.

    scipy.spatial.Delaunay: Delaunay tesselation in N dimensions.

    Usage
    -----
    >>> neighbors = basic_info.find_neighbors(tri)

    """

    # Importing required modules.
    from collections import defaultdict

    # Initializating the output variable as a defaultdict of sets.
    neighbors = defaultdict(set)

    # Looping over all triangles (set of vertices) of the triangulation.
    for simplex in tri.simplices:
        # Looping over every verice in the current triangle.
        for pid in simplex:

            # Get the set of vertices in the current triangle.
            other = set(simplex)

            # Remove the current node from the list.
            other.remove(pid)

            # Perform the union of the current set with the other sets in which
            # the current node is also present.
            neighbors[pid] = neighbors[pid].union(other)

    # Looping over to set the right amount of points in neighbors. This is a
    # temporary bugfix for some specific cases.
    for node in range(len(neighbors)):
        (len(neighbors[node]))

    return neighbors
