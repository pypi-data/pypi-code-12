# -*- coding: utf-8 -*-
"""
Module created to manage the filter criterion application on the input point
data.

@author: Matheus Boni Vicari (matheus.boni.vicari@gmail.com)
"""

import numpy
import scipy
from tin.basic_info import tri_info
from tin.params import criterion_function
from tin.unpack import F_unpack
from tin.unpack import neighbors_unpack


# Defining the criterion_check function.
def criterion_check(tri, point_data):

    """
    This function makes applies the filtering criterion on the point data
    through the use of the Delaunay triangulation information 'tri'. The
    criterion is created based on the work from Yand and Cui (2010).


    Parameters
    ----------
    tri: scipy.spatial.qhull.Delaunay
            Delaunay triangulation generated from the point_data variable.
    point_data: numpy.ndarray
            x and y coordinates from the input set of points.

    Returns
    -------
    pos_neighbors: numpy.ndarray
            Set of indices for the filtered points. This indices are relative
            of the point_data variable.

    Raises
    ------
    TypeError
        If input is the wrong data type.

    Usage
    -----
    >>> pos_neighbors = tinfiltering.criterion(tri, point_data)

    References
    ----------
    .. [1] X. Yang and W. Cui, "A Novel Spatial Clustering Algorithm Based on
           Delaunay Triangulation," Journal of Software Engineering and
           Applications, Vol. 3 No. 2, 2010, pp. 141-149. doi:
           10.4236/jsea.2010.32018.

    Usage
    -----

    >>> pos_neighbors = criterion.criterion_check(tri, point_data)

    """

    # Check the input variables.
    if type(tri) is not scipy.spatial.qhull.Delaunay:

        raise TypeError("input must be of type scipy.spatial.qhull.Delaunay.")

    elif type(point_data) is not numpy.ndarray:

        raise TypeError("input must be of type numpy.ndarray.")

    # Executing the tri_info function to get the parameters necessary to run
    # the criterion function.
    neighbors, n_degree, n_id, e_dist, e_id = tri_info(tri, point_data)

    # Executing the criterion function.
    F = criterion_function(neighbors, e_dist, point_data)

    # Unpacking the variables F (criterion function) and neighbors (list of
    # neighbors for every node in the triangulation) into a 1-D array to match
    # the shape of the e_dist (edge distances) variable.
    F_array = F_unpack(F, e_dist, e_id)
    neighbors_array = neighbors_unpack(neighbors, n_degree)

    # Applying the criterion check based on the criterion function (F) and the
    # edge distances (e_dist) values.
    pos_neighbors = neighbors_array[e_dist < F_array]

    # Removing duplicate values.
    pos_neighbors = numpy.unique(pos_neighbors)

    return pos_neighbors.astype(numpy.int)
