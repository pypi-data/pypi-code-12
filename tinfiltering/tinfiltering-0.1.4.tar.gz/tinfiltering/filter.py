# -*- coding: utf-8 -*-
"""
This is the main file/function within the tin_filter package. The purpose of
it is to perform the steps required to apply the TIN filtering to a set of
points.

@author: Matheus Boni Vicari (matheus.boni.vicari@gmail.com)
"""

from criterion import criterion_check
from tin import delaunay_triangulation
import numpy


# Defining the apply_filter function.
def apply_filter(x, y):

    """
    This apply_filter is the main function of this package and makes use of the
    anciliary functions created for the tin_filtering package to apply the
    filter on a set of points.


    Parameters
    ----------
    x, y: list or numpy.ndarray
            Coordinates for the set of points to be filtered.

    Returns
    -------
    out_points: 2D numpy.ndarray
            Coordinates for the filtered set of points.

    Raises
    ------
    ValueError
        If input is in the wrong shape (the shapes of x and y should match).
    TypeError
        If the input is of the wrong type (the inputs must be a 1-D array or
        list)

    References
    ----------
    .. [1] X. Yang and W. Cui, "A Novel Spatial Clustering Algorithm Based on
           Delaunay Triangulation," Journal of Software Engineering and
           Applications, Vol. 3 No. 2, 2010, pp. 141-149. doi:
           10.4236/jsea.2010.32018.

    Usage
    -----

    >>> out_points = tinfiltering.apply_filter(x, y)

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

    # Generating the triangulation from the input points. Also, concatenating
    # the input coordinates into a single variable.
    point_data, tri = delaunay_triangulation(x, y)

    # Applying the function criterion on the triangulation 'tri' to remove
    # noise points from the input points 'point_data'.
    pos_neighbors = criterion_check(tri, point_data)

    # Obtaining the final set of points based on their indices 'pos_neighbors'.
    out_points = point_data[pos_neighbors]

    return out_points
