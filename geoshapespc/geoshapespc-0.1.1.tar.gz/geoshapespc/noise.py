# -*- coding: utf-8 -*-
"""
Module to generate a point cloud of random noise around the original point
cloud. These functions can be applied either to 2D or 3D data.

@author: Matheus Boni Vicari (matheus.boni.vicari@gmail.com)

"""

from __future__ import division
import numpy as np
import regular_shape
import sys
import os

# Appending parent directory to import auxiliary module.
sys.path.insert(0, os.pardir)


# Defining function to apply exponential noise to a set of 3D point
# coordinates.
def exponential_noise_3D(x, y, z, xr, yr, n_points, nrange):

    """
    Function to generate a randomly placed point cloud of simulated noise,
    exponentialy distributed around any given 3D geometric shape.

    Parameters:
    -----------
    x, y, z: numpy.ndarray
            Sets of axis coordinates of the shape point cloud.
    xr, yr: float or numpy.float
            Radii of the shape along x and y axis, respectivelly.
    n_points: numpy.int64
            Number of noise points to be created. For 3D point clouds, the
            total amount of noise points will be (n_points * unique(z)).
    nrange: numpy.float64
            Range/distance along which the noise points are to be placed.

    Returns
    -------
    xrand, yrand, zrand: numpy.ndarray
            Sets of coordinates for the n_points of noise data.

    Usage
    -----
    >>> xrand, yrand, zrand = noise.exponential_noise_3D(x, y, z, xr, yr,\
 n_points, nrange)

    """

    # Initializing empty output variables.
    xrand = []
    yrand = []
    zrand = []

    # Obtaining the set of unique z coordinates values to loop over.
    z_vals = np.unique(z)

    # Looping over the range of z_vals.
    for i in range(len(z_vals)):

        # Obtaining x and y set of coordinates relatives to the ith z value.
        xin = x[z == z_vals[i]]
        yin = y[z == z_vals[i]]

        # Executing the exponential_noise_2D function to the set of xin and yin
        # points.
        xtemp, ytemp = exponential_noise_2D(xin, yin, xr, yr, n_points, nrange)

        # Filling up an array of z ith coordinate with the same size as xtemp
        # and ytemp.
        ztemp = np.full([len(xtemp)], z_vals[i])

        # Appending the temporary noise arrays to the output array.
        xrand = np.append(xrand, xtemp)
        yrand = np.append(yrand, ytemp)
        zrand = np.append(zrand, ztemp)

    return xrand, yrand, zrand


# Defining function to apply uniform noise to the outside of a set of 3D point
# coordinates.
def out_uniform_noise_3D(x, y, z, xr, yr, n_points, nrange):

    """
    Function to generate a randomly placed point cloud of simulated noise,
    uniformly distributed outside any given 3D geometric shape.

    Parameters:
    -----------
    x, y, z: numpy.ndarray
            Sets of axis coordinates of the shape point cloud.
    xr, yr: float or numpy.float
            Radii of the shape along x and y axis, respectivelly.
    n_points: numpy.int64
            Number of noise points to be created. For 3D point clouds, the
            total amount of noise points will be (n_points * unique(z)).
    nrange: numpy.float64
            Range/distance along which the noise points are to be placed.

    Returns
    -------
    xrand, yrand, zrand: numpy.ndarray
            Sets of coordinates for the n_points of noise data.

    Usage
    -----
    >>> xrand, yrand, zrand = noise.out_uniform_noise_3D(x, y, z, xr, yr,\
 n_points, nrange)

    """

    # Initializing empty output variables.
    xrand = []
    yrand = []
    zrand = []

    # Obtaining the set of unique z coordinates values to loop over.
    z_vals = np.unique(z)

    # Looping over the range of z_vals.
    for i in range(len(z_vals)):

        # Obtaining x and y set of coordinates relatives to the ith z value.
        xin = x[z == z_vals[i]]
        yin = y[z == z_vals[i]]

        # Executing the out_uniform_noise_2D function to the set of xin and yin
        # points.
        xtemp, ytemp = out_uniform_noise_2D(xin, yin, xr,
                                            yr, n_points, nrange)

        # Filling up an array of z ith coordinate with the same size as xtemp
        # and ytemp.
        ztemp = np.full([len(xtemp)], z_vals[i])

        # Appending the temporary noise arrays to the output array.
        xrand = np.append(xrand, xtemp)
        yrand = np.append(yrand, ytemp)
        zrand = np.append(zrand, ztemp)

    return xrand, yrand, zrand


# Defining function to apply uniform noise to a set of 3D point coordinates.
def uniform_noise_3D(xc, yc, xr, yr, length, n_points, nrange):

    """
    Function to generate a randomly placed point cloud of simulated noise,
    uniformly distributed in the same region of any given 3D geometric shape.

    Parameters:
    -----------
    x, y, z: numpy.ndarray
            Sets of axis coordinates of the shape point cloud.
    xr, yr: float or numpy.float
            Radii of the shape along x and y axis, respectivelly.
    n_points: numpy.int64
            Number of noise points to be created. For 3D point clouds, the
            total amount of noise points will be (n_points * unique(z)).
    nrange: numpy.float64
            Range/distance along which the noise points are to be placed.

    Returns
    -------
    xrand, yrand, zrand: numpy.ndarray
            Sets of coordinates for the n_points of noise data.

    Usage
    -----
    >>> xrand, yrand, zrand = noise.uniform_noise_3D(x, y, z, xr, yr, n_points\
, nrange)

    """

    # Initializing empty output variables.
    xrand = []
    yrand = []
    zrand = []




    # Obtaining the set of unique z coordinates values to loop over.
    z_vals = np.unique(z)

    # Looping over the range of z_vals.
    for i in range(len(z_vals)):

        # Obtaining x and y set of coordinates relatives to the ith z value.
        xin = x[z == z_vals[i]]
        yin = y[z == z_vals[i]]

        # Executing the uniform_noise_2D function to the set of xin and yin
        # points.
        xtemp, ytemp = uniform_noise_2D(xin, yin, n_points, nrange)
        ztemp = np.full([len(xtemp)], z_vals[i])

        # Appending the temporary noise arrays to the output array.
        xrand = np.append(xrand, xtemp)
        yrand = np.append(yrand, ytemp)
        zrand = np.append(zrand, ztemp)

    return xrand, yrand, zrand
