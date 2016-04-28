# -*- coding: utf-8 -*-
"""
This module performs the reshape of the TIN filter variables in order to make
them compatible among themselves as to perform the calculations.

@author: Matheus Boni Vicari (matheus.boni.vicari@gmail.com)
"""

import numpy
import collections


# Defining the neighbors_unpack function.
def neighbors_unpack(neighbors, node_degree):

    """
    The neighbors_unpack function performs the unpacking/reshaping of the
    'neighbors' variable.

    Parameters
    ----------
    neighbors: collections.defaultdict
            Sets of neighboring nodes for each node in the triangulation.
    node_degree: numpy.ndarray
            Degree of each node in the triangulation.

    Returns
    -------
    neighbors_array: numpy.ndarray
            Neighbors indices for all nodes.

    Raise
    -----
    TypeError
        If input is the wrong type.

    Usage
    -----
    >>> neighbors_array = unpack.neighbors_unpack(neighbors, node_degree)

    """

    # Checking the input variables.
    if type(neighbors) is not collections.defaultdict:

        raise TypeError("Input must be of type collections.defaultdict.")

    elif type(node_degree) is not numpy.ndarray:

        raise TypeError("Input must be of type numpy.ndarray.")

    # Setting the counter to 0.
    count = 0

    # Calculating the total number of nodes in the triangulation.
    total_nodes = int(numpy.sum(node_degree))

    # Initializing the output variable as an array of zeros.
    neighbors_array = numpy.zeros(total_nodes)

    # Looping over the nodes in the triangulation.
    for node in neighbors:
        # Looping over the neighbors for the current node.
        for nei_id in neighbors[node]:

            # Assigning the current neighbor id to the output variable for the
            # current count.
            neighbors_array[count] = nei_id

            # Increasing the counter.
            count += 1

    return neighbors_array


# Defining the F_unpack function.
def F_unpack(F, edge_distances, edge_id):

    """
    The F_unpack function performs the unpacking/reshaping of the 'F' variable.

    Parameters
    ----------
    F: numpy.ndarray
            Criterion function for the evaluated triangulation.
    edge_distances: numpy.ndarray
            Distance between every pair of neighboring nodes (edges).
    edge_id: numpy.ndarray
            Indices for each edge in the triangulation.

    Returns
    -------
    F_array: numpy.ndarray
            Criterion function for all nodes.

    Raises
    ------
    TypeError
        If input is the wrong type.

    Usage
    -----
    >>> F_array = unpack.F_unpack(F, edge_distances, edge_id)

    """

    # Checking the input variables.
    if type(edge_id) is not collections.defaultdict:

        raise TypeError("Input must be of type collections.defaultdict.")

    elif type(edge_distances) is not numpy.ndarray:

        raise TypeError("Input must be of type numpy.ndarray.")

    elif type(F) is not numpy.ndarray:

        raise TypeError("Input must be of type numpy.ndarray.")

    # Setting the counter to 0.
    count = 0

    # Initializating the output array.
    F_array = numpy.zeros(edge_distances.shape)

    # Looping over all edges.
    for idx in edge_id:

        # Looping over the nodes in the edges.
        for node in edge_id[idx]:

            # Assigning the F value for the current index to the output
            # variable in the position 'count'.
            F_array[count] = F[idx]

            # Incrementing the counter.
            count += 1

    return F_array


# Defining node_id_unpack function.
def node_id_unpack(edge_id, edge_distances):

    """
    The node_id_unpack function performs the unpacking/reshaping of the
    'node_id' variable.

    Parameters
    ----------
    edge_id: numpy.ndarray
            Indices for each edge in the triangulation.
    edge_distances: numpy.ndarray
            Distance between every pair of neighboring nodes (edges).

    Returns
    -------
    node_array: numpy.ndarray
            Node indices for all nodes.

    Raises
    ------
    TypeError
        If input is the wrong type.

    Usage
    -----
    >>> node_array = unpack.node_unpack(edge_id, edge_distances)

    """

    # Checking the input variables.
    if type(edge_id) is not collections.defaultdict:

        raise TypeError("Input must be of type collections.defaultdict.")

    elif type(edge_distances) is not numpy.ndarray:

        raise TypeError("Input must be of type numpy.ndarray.")

    # Setting the counter to 0.
    count = 0

    # Initializating the output array.
    node_array = numpy.zeros(edge_distances.shape)

    # Looping over all edges.
    for node in edge_id:
        # Looping over the neighbor nodes in the edges.
        for neighbor in edge_id[node]:

            # Assigning the current node to the output variable in the position
            # 'count'.
            node_array[count] = node

            # Incrementing the counter.
            count += 1

    return node_array
