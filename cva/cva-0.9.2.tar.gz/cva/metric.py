# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
#  Copyright (c) 2016, Robert Whitinger <cva_account@wmkt.com>
#
#  Distributed under the terms of the LGPL license either version 2.1 or
#  (at your option) any later version.
#
#  The full license is in the file LICENSE.txt, distributed with this software,
#  and is also available at <http://www.gnu.org/licenses/>
#-----------------------------------------------------------------------------
"""
cva.metric

This module contains implementations of several metrics.  These
metrics accept two points in parameter space and return a single value.
That value may be a distance, or in a more general case it may be
an arbitrary objective functional.
"""


from __future__ import division
import numpy as np
import math

# project library
import cva

# Constants
PI = math.pi
TPI = 2.0*PI

def distance(sa, sb):
    """
    cva.metric.distance(sa, sb)

    Parameters
    ----------
    sa : array_like
        This parameter contains a starting point in the parameter space.
    sb : array_like
        This parameter contains an ending point in the parameter space.

    Returns
    -------
    metric : float64
        The Euclidean distance between the two surface points corresponding
        to sa and sb.

    Notes
    -----
    none

    Examples
    --------
    import cva
    sa = (0.4,0.5)
    sb = (0.6,0.7)
    cva.solve.select(cva.model.sphere,cva.model.distance)
    metric = cva.model.distance(sa,sb)

    In this example, the parameterization points sa and sb are mapped into
    their corresponding points on the surface of a unit sphere, and the
    Euclidean distance between those two points is returned.
    """

    G = cva.solve.get_parm('G')
    xa = np.asarray(G(sa))           # from point
    xb = np.asarray(G(sb))           # to point
    summation = np.sum((xb-xa)**2)
    metric = math.sqrt(summation)
    return metric

# Brachistochrone objective functional
def brachistochrone_earth(s0, s1):
    """
    cva.metric.brachistochrone_earth(sa, sb)

    Parameters
    ----------
    sa : array_like
        This parameter contains a starting point in the parameter space.
    sb : array_like
        This parameter contains an ending point in the parameter space.

    Returns
    -------
    metric : float64
        The time required to move between the two surface points corresponding
        to sa and sb on a straight line path in Earth gravity.

    Notes
    -----
    none

    Examples
    --------
    import cva
    sa = (0.4,0.5)
    sb = (0.6,0.7)
    cva.solve.select(cva.model.tilted_plane,cva.model.brachistochrone_earth)
    metric = cva.model.brachistochrone_earth(sa,sb)

    In this example, the parameterization points sa and sb are mapped into
    their corresponding points on the surface of a tilted plane, and the
    time required to traverse between those two points is returned.
    """
    G = cva.solve.get_parm('G')
    sa = cva.solve.get_parm('sa')
    x0, y0, z0 = G(s0[:])[0]  # from point
    x1, y1, z1 = G(s1[:])[0]  # to point
    _, _, za = G(sa[:])[0]  # model starting point
    g = 9.8
    if z1 >= za:
        metric = np.infty   # we can't reach points higher than our starting point
    else:
        metric = math.sqrt(((x1-x0)**2+(y1-y0)**2+(z1-z0)**2)/(2.0*g*(za-z1)))
    return metric

def brachistochrone_moon(s0, s1):
    """
    cva.metric.brachistochrone_moon(sa, sb)

    Parameters
    ----------
    sa : array_like
        This parameter contains a starting point in the parameter space.
    sb : array_like
        This parameter contains an ending point in the parameter space.

    Returns
    -------
    metric : float64
        The time required to move between the two surface points corresponding
        to sa and sb on a straight line path in Moon gravity.

    Notes
    -----
    none

    Examples
    --------
    import cva
    sa = (0.4,0.5)
    sb = (0.6,0.7)
    cva.solve.select(cva.model.tilted_plane,cva.model.brachistochrone_moon)
    metric = cva.model.brachistochrone_moon(sa,sb)

    In this example, the parameterization points sa and sb are mapped into
    their corresponding points on the surface of a tilted plane, and the
    time required to traverse between those two points is returned.
    """
    G = cva.solve.get_parm('G')
    sa = cva.solve.get_parm('sa')
    x0, y0, z0 = G(s0[:])[0]  # from point
    x1, y1, z1 = G(s1[:])[0]  # to point
    _, _, za = G(sa[:])[0]  # model starting point
    g = 1.62
    if z1 >= za:
        metric = np.infty   # we can't reach points higher than our starting point
    else:
        metric = math.sqrt(((x1-x0)**2+(y1-y0)**2+(z1-z0)**2)/(2.0*g*(za-z1)))
    return metric

def schwarzschild(s0, s1):
    """
    cva.metric.schwarzschild(sa, sb)

    Parameters
    ----------
    sa : array_like
        This parameter contains a starting point in the parameter space.
    sb : array_like
        This parameter contains an ending point in the parameter space.

    Returns
    -------
    metric : float64
        The distance in spacetime between the two events in curved space,
        near a massive object, corresponding to sa and sb.

    Notes
    -----
    none

    Examples
    --------
    import cva
    sa = (0.4,0.5)
    sb = (0.6,0.7)
    cva.solve.select(cva.model.blackhole,cva.model.schwarzschild)
    metric = cva.model.schwarzschild(sa,sb)

    In this example, the parameterization points sa and sb are mapped into
    their corresponding events near a supermassive blackhole, and the
    spacetime distance between those two events is returned.

    The Schwarzschild metric forms the basis of general relativity.
    """
    G = cva.solve.get_parm('G')
    if np.ndim(s0) == 1:
        nparm = len(s0)
    else:
        nparm = np.shape(s0)[1]
    if nparm == 2:           # model surface at fixed time
        x0, y0, z0 = G(s0[:])[0]  # from point
        x1, y1, z1 = G(s1[:])[0]  # to point
        ct0 = ct1 = 0.0
    else:
        raise NotImplementedError
    C = 299792458.0   # speed of light (m/s)
    Ms = 1.98855e+30  # mass of the Sun (kg)
    Mb = 4.31e+6 * Ms # mass of Sagitarius A* (kg)
    Gc = 6.67384e-11  # gravitational constant (m^3 kg^-1 s^-2)
    gm = Gc*Mb
    Rs = 2.0*gm/(C*C) # Schwarzschild radius
    r0 = math.sqrt((x0-0.5)**2 + (y0-0.5)**2 + (z0-0.5)**2)
    r1 = math.sqrt((x1-0.5)**2 + (y1-0.5)**2 + (z1-0.5)**2)
    r = (r1+r0)/2.0
    theta0 = theta1 = theta = PI/2.0
    phi0 = (PI/2.0)-np.arctan2(z0, y0)
    if phi0 > PI:
        phi0 = phi0 - TPI
    phi1 = (PI/2.0)-np.arctan2(z1, y1)
    if phi1 > PI:
        phi1 = phi1 - TPI
    try:
        dphi = phi1 - phi0
        if dphi > PI:
            dphi = TPI - dphi
        metric = (1/C)*math.sqrt(-(1-(Rs/r))*(ct1-ct0)**2 + (1/(1-(Rs/r)))*(r1-r0)**2 + r**2 * (theta1-theta0)**2 + r**2 * np.sin(theta)**2 * (dphi**2))
    except:
        metric = np.infty
    return metric

def minkowski(s0, s1):
    """
    cva.metric.minkowski(sa, sb)

    Parameters
    ----------
    sa : array_like
        This parameter contains a starting point in the parameter space.
    sb : array_like
        This parameter contains an ending point in the parameter space.

    Returns
    -------
    metric : float64
        The distance in spacetime between the two events in flat space
        (a region of space void of massive objects) corresponding to sa and sb.

    Notes
    -----
    none

    Examples
    --------
    import cva
    sa = (0.4,0.5)
    sb = (0.6,0.7)
    cva.solve.select(cva.model.inflating_sphere,cva.model.minkowski)
    metric = cva.model.minkowski(sa,sb)

    In this example, the parameterization points sa and sb are mapped into
    their corresponding events in spacetime, and the spacetime distance
    between those two events is returned.

    The Minkowski metric forms the basis of special relativity.
    """
    G = cva.solve.get_parm('G')
    x0, y0, z0, ct0 = G(s0[:])[0]  # from point
    x1, y1, z1, ct1 = G(s1[:])[0]  # to point
    metric = math.sqrt(abs((ct1-ct0)**2 -(x1-x0)**2 - (y1-y0)**2 - (z1-z0)**2))
    if ct1 < ct0:
        metric = np.infty  # we don't allow negative time movements
    return metric


if __name__ == "__main__":

    print "running cva/metric.py"
