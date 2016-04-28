# -*- coding: utf-8 -*-
"""
This module performs the creation of the triangulated irregular network (TIN)
of a 2D point cloud.

@author: Matheus Boni Vicari (matheus.boni.vicari@gmail.com)
"""

import numpy
from scipy.spatial import Delaunay


# Defining the function delaunay_triangulation.
def delaunay_triangulation(x, y):

    """
    The delaunay_triangulation function performs the creation of a triangulated
    irregular network (TIN) on a set of 2D points using the Delaunay module
    contained within the scipy.spatial package.

    Parameters
    ----------
    x, y: list or numpy.ndarray
            Coordinates for the set of points to be filtered.

    Returns
    -------
    point_data: numpy.ndarray
            x and y coordinates from the input set of points.
    tri: scipy.spatial.qhull.Delaunay
            Delaunay triangulation generated from the point_data variable.

    Raises
    ------
    ValueError
        If input is the wrong shape (the shapes of x and y should match).
    TypeError
        If the input is of the wrong type (the inputs must be a 1-D array or
        list)

    See also
    --------
    scipy.spatial: spatial algorithms and data structures.

    scipy.spatial.Delaunay: Delaunay tesselation in N dimensions.

    Usage
    -----

    >>> point_data, tri = create.delaunay_triangulation(x, y)
    """

    # Check the input variables.
    if type(x) is list and type(y) is list:

        # If both x and y are lists, check if their size matches.
        if len(x) != len(y):

            raise ValueError("Input lists must be of the same size.")

    elif type(x) is numpy.ndarray and type(y) is numpy.ndarray:

        # If both x and y are numpy arrays, check if their size matches.
        if len(x) != len(y):

            raise ValueError("Input arrays must be of the same size.")

    else:

        raise TypeError("Input must be of type list or numpy.ndarray")

    # Concatenating the variables into a single variable for the point data.
    point_data = numpy.asarray([x, y]).T

    # Cleaning the duplicate values.
    point_data = numpy.vstack({tuple(row) for row in point_data})

    # Generating the triangulation.
    tri = Delaunay(point_data)

    return point_data, tri
