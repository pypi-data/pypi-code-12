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
cva.model

This module contains implementations of several surface models.  These
implementations are in the form of mappings from a <u,v> plane to an <x,y,z>
surface, or in the general case of higher dimensional hypersurfaces in
the form of mappings from a <u0,u1,...uj> parameter space into an
<x0,x1,...,xk> hypersurface.

We adopt the convention that the surface is described by u-parameters in
the range of [0,1].  Models are required to accept out of range inputs
over the range of [-1,2] and return valid manifold surface mappings.  In other
words, the responsibility for wraparound lies with the model.  This is
reasonable since wraparound rules tend to be model-specific.
"""

from __future__ import division
import numpy as np
import math
from copy import deepcopy

# Constants
PI = math.pi
TPI = 2.0*PI

# here we store this module's parameter set and make it accessible
global _parms
# initialize default parameters
_parms = {'periodicity' : (False, True)
         }
def set_parm(parm_name, parm_value):
    """
    cva.model.set_parm(parm_name, parm_value)
    """
    _parms[parm_name] = parm_value

def get_parm(parm_name):
    """
    parm_value = cva.model.get_parm(parm_name)
    """
    return _parms[parm_name]

def list_parms():
    """
    keys = cva.solve.list_parms()
    """
    keys = _parms.keys()
    return keys

def startmodel(s, periodicity=True):
    """
    startmodel(x,s)

    This function is called by every model immediately on entry.
    """
    global entry_id
    entry_id = id(s)

    # if we are called with an array we just use it after making a local copy
    if type(s) is np.ndarray:
        local_copy = deepcopy(s)
    else:
        # but we also accept tuples and lists, others generate an error
        if type(s) is not tuple and type(s) is not list:
            raise TypeError("Expected tuple or list but got %s" % (type(s)))
        local_copy = np.asarray(s)
    # single points are converted into a uniform array format
    if np.ndim(local_copy) == 1:
        local_copy = local_copy.reshape(1, -1)
    s = local_copy
    # create a suitably sized array x for the model's path array
    length, nparameters = np.shape(s)
    x = np.zeros((length, nparameters+1))

    # save periodicity
    # periodicity = True  means that this model takes the default, that is
    # the last parameter in our list is periodic.
    # A model may pass a mask in order to override, for example,
    # a model with two parameters may set periodicity=(False,False) in
    # order to declare that neither parameter is periodic.

    # if the model does not override then we apply the default which
    # is to assume that the last parameter is periodic
    if periodicity == True:
        periodicity = (False,)*(np.shape(s)[1]-1)
        periodicity += (True,)
    set_parm('periodicity', periodicity)
    exit_id = (id(s))
    # make sure we have a local copy of s for our model
    assert entry_id != exit_id
    return s, x

def finishmodel(x, s):
    """
    finishmodel(x, s)

    This function is called by every model just prior to its return.
    """
    # code any general model exit conventions here
    # verify that the model did not alter s
    exit_id = id(s)
    assert entry_id != exit_id
    return x

def vertical_plane(s):
    """
    Model a vertical plane in R3.

    Parameters
    ----------
    s : array_like
        This parameter contains one or more points in the parameter
        space.  Multiple parameters are of the form s[length,nparm] where
        nparm is the dimensionality of the parameter space.  Single
        points are accepted as an ndarray s[1,nparm], tuple (u0,u1,...), or
        as a list [u0, u1, ...].

    Returns
    -------
    x : ndarray of surface points
        In R^3, x[:,0] corresponds to the x dimension, x[:,1] to the y
        and x[:,2] to the z.

    Notes
    -----
    none

    Examples
    --------
    import cva
    sa = (0.4,0.5)
    x = cva.model.vertical_plane(sa)

    In this example, the point defined by u = 0.4 and v = 0.5 is mapped into
    its corresponding point on the model's surface and that result is returned
    as a row array of points in cartesian coordinates.
    """
    s, x = startmodel(s, (False, False))

    # start of model mapping
    u = s[:, 0]
    v = s[:, 1]
    x[:, 0] = u
    x[:, 1] = np.zeros_like(u)  # this obtains a zero vector with the shape of u
    x[:, 2] = v
    # end of model mapping

    x = finishmodel(x, s)
    return x

def tilted_plane(s):
    """
    Model a tilted plane in R3.

    Parameters
    ----------
    s : array_like
        This parameter contains one or more points in the parameter
        space.  Multiple parameters are of the form s[length,nparm] where
        nparm is the dimensionality of the parameter space.  Single
        points are accepted as an ndarray s[1,nparm], tuple (u0,u1,...), or
        as a list [u0, u1, ...].

    Returns
    -------
    x : ndarray of surface points
        In R^3, x[:,0] corresponds to the x dimension, x[:,1] to the y
        and x[:,2] to the z.

    Notes
    -----
    none

    Examples
    --------
    import cva
    sa = (0.4,0.5)
    x = cva.model.tilted_plane(sa)

    In this example, the point defined by u = 0.4 and v = 0.5 is mapped into
    its corresponding point on the model's surface and that result is returned
    as a row array of points in cartesian coordinates.
    """
    s, x = startmodel(s, (False, False))

    # start of model mapping
    u = s[:, 0]
    v = s[:, 1]
    alpha = -np.pi/4.0
    # rotate around the x axis by pi/4
    x[:, 0] = u
    x[:, 1] = v*np.cos(alpha)
    x[:, 2] = -v*np.sin(alpha)
    # end of model mapping

    x = finishmodel(x, s)
    return x

def hyperboloid(s):
    """
    Model a hyperboloid in R3.

    Parameters
    ----------
    s : array_like
        This parameter contains one or more points in the parameter
        space.  Multiple parameters are of the form s[length,nparm] where
        nparm is the dimensionality of the parameter space.  Single
        points are accepted as an ndarray s[1,nparm], tuple (u0,u1,...), or
        as a list [u0, u1, ...].

    Returns
    -------
    x : ndarray of surface points
        In R^3, x[:,0] corresponds to the x dimension, x[:,1] to the y
        and x[:,2] to the z.

    Notes
    -----
    none

    Examples
    --------
    import cva
    sa = (0.4,0.5)
    x = cva.model.hyperboloid(sa)

    In this example, the point defined by u = 0.4 and v = 0.5 is mapped into
    its corresponding point on the model's surface and that result is returned
    as a row array of points in cartesian coordinates.
    """
    s, x = startmodel(s)

    # start of model mapping
    u = s[:, 0]
    v = s[:, 1]
    theta = (v-0.5)*TPI
    x[:, 0] = np.cosh(3.0*(0.5-u))*np.cos(theta)
    x[:, 1] = np.cosh(3.0*(0.5-u))*np.sin(theta)
    x[:, 2] = np.sinh(3.0*(0.5-u))
    # end of model mapping

    x = finishmodel(x, s)
    return x

def cylinder(s):
    """
    Model a cylinder in R3.

    Parameters
    ----------
    s : array_like
        This parameter contains one or more points in the parameter
        space.  Multiple parameters are of the form s[length,nparm] where
        nparm is the dimensionality of the parameter space.  Single
        points are accepted as an ndarray s[1,nparm], tuple (u0,u1,...), or
        as a list [u0, u1, ...].

    Returns
    -------
    x : ndarray of surface points
        In R^3, x[:,0] corresponds to the x dimension, x[:,1] to the y
        and x[:,2] to the z.

    Notes
    -----
    none

    Examples
    --------
    import cva
    sa = (0.4,0.5)
    x = cva.model.cylinder(sa)

    In this example, the point defined by u = 0.4 and v = 0.5 is mapped into
    its corresponding point on the model's surface and that result is returned
    as a row array of points in cartesian coordinates.
    """
    s, x = startmodel(s)

    # start of model mapping
    u = s[:, 0]
    v = s[:, 1]
    x[:, 0] = np.cos(v*TPI)
    x[:, 1] = np.sin(v*TPI)
    x[:, 2] = 1.0 - u
    # end of model mapping

    x = finishmodel(x, s)
    return x

def capped_cylinder(s):
    """
    Model a capped_cylinder in R3.

    Parameters
    ----------
    s : array_like
        This parameter contains one or more points in the parameter
        space.  Multiple parameters are of the form s[length,nparm] where
        nparm is the dimensionality of the parameter space.  Single
        points are accepted as an ndarray s[1,nparm], tuple (u0,u1,...), or
        as a list [u0, u1, ...].

    Returns
    -------
    x : ndarray of surface points
        In R^3, x[:,0] corresponds to the x dimension, x[:,1] to the y
        and x[:,2] to the z.

    Notes
    -----
    none

    Examples
    --------
    import cva
    sa = (0.4,0.5)
    x = cva.model.capped_cylinder(sa)

    In this example, the point defined by u = 0.4 and v = 0.5 is mapped into
    its corresponding point on the model's surface and that result is returned
    as a row array of points in cartesian coordinates.
    """
    s, x = startmodel(s)

    # start of model mapping
    u = s[:, 0]
    v = s[:, 1]
    p = 4.0/32.0
    theta = (v-0.5)*TPI
    x[:, 0] = np.cos(theta)
    x[:, 0] = np.where(u < p, x[:, 0]*(u/p), x[:, 0])
    x[:, 0] = np.where(u > (1.0-p), x[:, 0]*(1.0-u)/p, x[:, 0])
    x[:, 1] = np.sin(theta)
    x[:, 1] = np.where(u < p, x[:, 1]*(u/p), x[:, 1])
    x[:, 1] = np.where(u > (1.0-p), x[:, 1]*(1.0-u)/p, x[:, 1])
    x[:, 2] = (u-p)/(1.0-(2.0*p))
    x[:, 2] = np.where(u < p, 0.0, x[:, 2]) # add top cap
    x[:, 2] = np.where(u > (1.0-p), 1.0, x[:, 2]) # add bottom cap

    # end of model mapping

    x = finishmodel(x, s)
    return x

def moebius(s):
    """
    Model a Moebius strip in R3.

    Parameters
    ----------
    s : array_like
        This parameter contains one or more points in the parameter
        space.  Multiple parameters are of the form s[length,nparm] where
        nparm is the dimensionality of the parameter space.  Single
        points are accepted as an ndarray s[1,nparm], tuple (u0,u1,...), or
        as a list [u0, u1, ...].

    Returns
    -------
    x : ndarray of surface points
        In R^3, x[:,0] corresponds to the x dimension, x[:,1] to the y
        and x[:,2] to the z.

    Notes
    -----
    none

    Examples
    --------
    import cva
    sa = (0.4,0.5)
    x = cva.model.moebius(sa)

    In this example, the point defined by u = 0.4 and v = 0.5 is mapped into
    its corresponding point on the model's surface and that result is returned
    as a row array of points in cartesian coordinates.
    """
    s, x = startmodel(s)

    # start of model mapping
    band_width = 2.0
    u = s[:, 0]  # u runs around the strip
    v = s[:, 1]  # v runs from edge to edge
    w = (u-0.5)*(band_width)
    x[:, 0] = (1.0+w*np.cos(v*PI))*np.cos(v*TPI)
    x[:, 1] = (1.0+w*np.cos(v*PI))*np.sin(v*TPI)
    x[:, 2] = w*np.sin(v*PI)
    # end of model mapping

    x = finishmodel(x, s)
    return x

def torus(s):
    """
    Model a torus in R3.

    Parameters
    ----------
    s : array_like
        This parameter contains one or more points in the parameter
        space.  Multiple parameters are of the form s[length,nparm] where
        nparm is the dimensionality of the parameter space.  Single
        points are accepted as an ndarray s[1,nparm], tuple (u0,u1,...), or
        as a list [u0, u1, ...].

    Returns
    -------
    x : ndarray of surface points
        In R^3, x[:,0] corresponds to the x dimension, x[:,1] to the y
        and x[:,2] to the z.

    Notes
    -----
    none

    Examples
    --------
    import cva
    sa = (0.4,0.5)
    x = cva.model.torus(sa)

    In this example, the point defined by u = 0.4 and v = 0.5 is mapped into
    its corresponding point on the model's surface and that result is returned
    as a row array of points in cartesian coordinates.
    """
    s, x = startmodel(s)

    # start of model mapping
    u = s[:, 0]
    v = s[:, 1]
    R = 2  # the distance from the origin to the center of the torus
    D = 1  # the diameter of the torus
    phi = (u-0.5)*TPI          # where phi in [-pi,pi]
    theta = (v-0.5)*TPI  # where theta in [-pi,pi]
    x[:, 0] = (R + D*np.cos(phi))*np.cos(theta)
    x[:, 1] = (R + D*np.cos(phi))*np.sin(theta)
    x[:, 2] = D*np.sin(phi)
    # end of model mapping

    x = finishmodel(x, s)
    return x

def sphylinder(s):
    """
    Model a sphylinder in R3.

    Parameters
    ----------
    s : array_like
        This parameter contains one or more points in the parameter
        space.  Multiple parameters are of the form s[length,nparm] where
        nparm is the dimensionality of the parameter space.  Single
        points are accepted as an ndarray s[1,nparm], tuple (u0,u1,...), or
        as a list [u0, u1, ...].

    Returns
    -------
    x : ndarray of surface points
        In R^3, x[:,0] corresponds to the x dimension, x[:,1] to the y
        and x[:,2] to the z.

    Notes
    -----
    none

    Examples
    --------
    import cva
    sa = (0.4,0.5)
    x = cva.model.vertical_plane(sa)

    In this example, the point defined by u = 0.4 and v = 0.5 is mapped into
    its corresponding point on the model's surface and that result is returned
    as a row array of points in cartesian coordinates.
    """
    s, x = startmodel(s)

    # start of model mapping

    # "latitude" ranges from u=0 (north pole) to u=1 (south pole) with special wrapping
    # "longitude ranges from v=0 to v=1 (2pi) with wrapping
    s[:, 1] = np.abs(s[:, 1])      # wraparound v assuming negative and positive latitudes are equal
    s[:, 1] = np.mod(s[:, 1], 2.0)  # wraparound v handling 2pi multiples
    s[:, 0] = np.where(s[:, 1] > 1.0, 1.0-s[:, 0], s[:, 0]) # wraparound u at "south pole"
    s[:, 1] = np.where(s[:, 1] > 1.0, 2.0-s[:, 1], s[:, 1]) # wraparound v at "south pole"
    u = s[:, 0]
    v = s[:, 1]
    # Convert the unit u,v plane into phi, theta representation
    phi = u*PI
    theta = (v-0.5)*TPI
    p = 1.0/2.0
    # Convert to rectangular coordinate system
    x[:, 0] = (np.sin(phi)**p)*np.cos(theta)
    x[:, 1] = (np.sin(phi)**p)*np.sin(theta)
    x[:, 2] = np.where(u < 0.50, np.abs(np.cos(phi))**p, -np.abs(np.cos(phi))**p)
    # end of model mapping

    x = finishmodel(x, s)
    return x

def latlon(lat, lon):
    """
    A utility function to convert latitude and longitude into a <u,v>
    representation suitable for use in the cva.model.earth.

    Parameters
    ----------
    lat : float
        Latitude in the range of -90 (south pole) to +90 (north pole).
    lon : float
        Longitude in the range of -180 (west) to +180 degrees (east).

    Returns
    -------
    sa : tuple of <u,v> coordinates

    Notes
    -----
    See also cva.model.earth()
    """
    sa = ((90.0 - lat)/180.0, (lon+180.0)/360.0)
    return sa

def earth(s):
    """
    Model the Earth (WGS84) in R3.

    Parameters
    ----------
    s : array_like
        This parameter contains one or more points in the parameter
        space.  Multiple parameters are of the form s[length,nparm] where
        nparm is the dimensionality of the parameter space.  Single
        points are accepted as an ndarray s[1,nparm], tuple (u0,u1,...), or
        as a list [u0, u1, ...].

    Returns
    -------
    x : ndarray of surface points
        In R^3, x[:,0] corresponds to the x dimension, x[:,1] to the y
        and x[:,2] to the z.

    Notes
    -----
    This is the WGS84 (World Geodetic System 1984) geocentric
    equipotential ellipsoid model of the Earth surface as projected onto the
    ECEF (Earth centered Earth fixed) cartesian coordinate system in units
    of kilometers.

    Circumference of Earth:

    40,075.017 km (equatorial)
    40,007.860 km (meridional)


    See also the utility function cva.model.latlon().

    Examples
    --------
    import cva
    sa = (0.4,0.5)
    x = cva.model.earth(sa)

    In this example, the point defined by u = 0.4 and v = 0.5 is mapped into
    its corresponding point on the model's surface and that result is returned
    as a row array of points in cartesian coordinates.

    import cva
    lat = 36.303181
    lon = -82.368280
    sa = cva.model.latlon(lat,lon)
    x = cva.model.earth(sa)

    In this example we show the use of the utility function
    cva.model.latlon() to find the coordinates of a point on the
    Earth's surface corresponding to a geographical location expressed
    in decimal latitude and longitude.
    """
    s, x = startmodel(s)

    # start of model mapping

    # WGS84 defining constants
    a = 6378.1370  # Semi-major axis in units of kilometers
    f = 1.0/298.257223563 # flattening
    # Derived constants
    # b = a*(1-f)  # Semi-minor axis (6356752.31425)
    e2 = 2*f - f*f  # First eccentricity squared
    # "latitude" ranges from u=0 (north pole) to u=1 (south pole) with special wrapping
    # "longitude ranges from v=0 (-pi) to v=1 (pi) with wrapping
    u = np.empty_like(s[:, 0])
    v = np.empty_like(s[:, 1])
    u = np.where(s[:, 0] > 1.0, 2.0-s[:, 0], s[:, 0])   # if u is wrapped at south pole
    v = np.where(s[:, 0] > 1.0, s[:, 1]+0.5, s[:, 1])   # then wrap v correspondingly
    u = np.where(s[:, 0] < 0.0, -s[:, 0], s[:, 0])      # if u is wrapped at north pole
    v = np.where(s[:, 0] < 0.0, s[:, 1]+0.5, s[:, 1])   # then wrap v correspondingly
    # Convert the unit u,v plane into phi, theta representation
    phi = u*PI           # where phi ranges from 0 (north pole) to pi (south pole)
    theta = (v-0.5)*TPI  # theta in [-pi,pi] where theta = 0 is on the prime meridian
    # Convert to ECEF rectangular coordinate system
    Nphi = a/(np.sqrt(1+e2*np.cos(phi)**2))
    x[:, 0] = Nphi*np.sin(phi)*np.cos(theta)
    x[:, 1] = Nphi*np.sin(phi)*np.sin(theta)
    x[:, 2] = Nphi*np.cos(phi)
    # end of model mapping

    x = finishmodel(x, s)
    return x

def blackhole(s):
    """
    Model a region of space as a plane intersecting a massive object.

    Parameters
    ----------
    s : array_like
        This parameter contains one or more points in the parameter
        space.  Multiple parameters are of the form s[length,nparm] where
        nparm is the dimensionality of the parameter space.  Single
        points are accepted as an ndarray s[1,nparm], tuple (u0,u1,...), or
        as a list [u0, u1, ...].

    Returns
    -------
    x : ndarray of surface points
        where x[:,0] corresponds to the x dimension, x[:,1] to the y
        and x[:,2] to the z.

    Notes
    -----
    none

    Examples
    --------
    import cva
    sa = (0.0,0.4,0.5)
    x = cva.model.blackhole(sa)

    In this example, the point defined by u = 0.4 and v = 0.5 is mapped into
    its corresponding point on the model's surface and that result is returned
    as a row array of points in cartesian coordinates.
    """
    s, x = startmodel(s, (False, False))  # we declare that neither axis is periodic

    # start of model mapping

    u = s[:, 0]
    v = s[:, 1]
    C = 299792458.0   # speed of light (m/s)
    Ms = 1.98855e+30  # mass of the Sun (kg)
    Mb = 4.31e+6 * Ms # mass of Sagitarius A* (kg)
    Gc = 6.67384e-11  # gravitational constant (m^3 kg^-1 s^-2)
    gm = Gc * Mb        # we use the mass of the Sgr A* supermassive blackhole
    Rs = 2.0*gm/(C*C)   # Schwarzschild radius
    R = 20.0 * Rs       # our region is 10x the Schwarzschild radius

    x[:, 0] = u * 0.0
    x[:, 1] = (u - 0.5) * R
    x[:, 2] = (v - 0.5) * R
    # end of model mapping

    x = finishmodel(x, s)
    return x

def inflating_sphere(s):
    """
    Model a sphere inflating in spacetime at 1/2 the speed of light.

    Parameters
    ----------
    s : array_like
        This parameter contains one or more points in the parameter
        space.  Multiple parameters are of the form s[length,nparm] where
        nparm is the dimensionality of the parameter space.  Single
        points are accepted as an ndarray s[1,nparm], tuple (u0,u1,...), or
        as a list [u0, u1, ...].

    Returns
    -------
    x : ndarray of surface points
        In R^3, x[:,0] corresponds to the x dimension, x[:,1] to the y
        and x[:,2] to the z.

    Notes
    -----
    none

    Examples
    --------
    import cva
    sa = (0.4,0.5,0.6)
    x = cva.model.inflating_sphere(sa)

    In this example, the point defined by ct = 0.4, u = 0.5, and v = 0.6 is
    mapped into its corresponding point on the model's surface and that result
    is returned as a row array of points in cartesian coordinates.
    """
    s, x = startmodel(s)

    # start of model mapping

    # u[0] = ct (time * light speed)
    # u[1] = "latitude" ranges from u[1]=0 (north pole) to u[1]=1 (south pole) with special wrapping
    # u[2] = "longitude ranges from v=0 (-pi) to v=1 (pi) (periodic)
    ct = s[:, 0]
    u = np.empty_like(s[:, 1])
    v = np.empty_like(s[:, 2])
    u = np.where(s[:, 1] > 1.0, 2.0-s[:, 1], s[:, 1])   # if u is wrapped at south pole
    v = np.where(s[:, 1] > 1.0, s[:, 2]+0.5, s[:, 2])   # then wrap v correspondingly
    u = np.where(s[:, 1] < 0.0, -s[:, 1], s[:, 1])      # if u is wrapped at north pole
    v = np.where(s[:, 1] < 0.0, s[:, 2]+0.5, s[:, 2])   # then wrap v correspondingly
    # Convert the unit u,v plane into phi, theta representation
    phi = u*PI           # where phi ranges from 0 (north pole) to pi (south pole)
    theta = (v-0.5)*TPI  # theta in [-pi,pi] where theta = 0 is on the prime meridian

    # define the rate of inflation
    radius = 0.5*ct+0.5  # inflation rate is 1/2 light speed
    # Convert to rectangular coordinate system
    x[:, 0] = np.sin(phi)*np.cos(theta)*radius
    x[:, 1] = np.sin(phi)*np.sin(theta)*radius
    x[:, 2] = np.cos(phi)*radius
    x[:, 3] = ct
    # end of model mapping

    x = finishmodel(x, s)
    return x

def collapsing_sphere(s):
    """
    Model a sphere collapsing in spacetime at 1/2 the speed of light.

    Parameters
    ----------
    s : array_like
        This parameter contains one or more points in the parameter
        space.  Multiple parameters are of the form s[length,nparm] where
        nparm is the dimensionality of the parameter space.  Single
        points are accepted as an ndarray s[1,nparm], tuple (u0,u1,...), or
        as a list [u0, u1, ...].

    Returns
    -------
    x : ndarray of surface points
        In R^3, x[:,0] corresponds to the x dimension, x[:,1] to the y
        and x[:,2] to the z.

    Notes
    -----
    none

    Examples
    --------
    import cva
    sa = (0.4,0.5,0.6)
    x = cva.model.collapsing_sphere(sa)

    In this example, the point defined by ct = 0.4, u = 0.5, and v = 0.6 is
    mapped into its corresponding point on the model's surface and that result
    is returned as a row array of points in cartesian coordinates.
    """
    s, x = startmodel(s)

    # start of model mapping

    # u[0] = ct (time * light speed)
    # u[1] = "latitude" ranges from u[1]=0 (north pole) to u[1]=1 (south pole) with special wrapping
    # u[2] = "longitude ranges from v=0 (-pi) to v=1 (pi) (periodic)
    ct = s[:, 0]
    u = np.empty_like(s[:, 1])
    v = np.empty_like(s[:, 2])
    u = np.where(s[:, 1] > 1.0, 2.0-s[:, 1], s[:, 1])   # if u is wrapped at south pole
    v = np.where(s[:, 1] > 1.0, s[:, 2]+0.5, s[:, 2])   # then wrap v correspondingly
    u = np.where(s[:, 1] < 0.0, -s[:, 1], s[:, 1])      # if u is wrapped at north pole
    v = np.where(s[:, 1] < 0.0, s[:, 2]+0.5, s[:, 2])   # then wrap v correspondingly
    # Convert the unit u,v plane into phi, theta representation
    phi = u*PI           # where phi ranges from 0 (north pole) to pi (south pole)
    theta = (v-0.5)*TPI  # theta in [-pi,pi] where theta = 0 is on the prime meridian

    # define the rate of deflation
    radius = 1.0-0.5*ct  # deflation rate is 1/2 light speed
    # Convert to rectangular coordinate system
    x[:, 0] = np.sin(phi)*np.cos(theta)*radius
    x[:, 1] = np.sin(phi)*np.sin(theta)*radius
    x[:, 2] = np.cos(phi)*radius
    x[:, 3] = ct
    # end of model mapping

    x = finishmodel(x, s)
    return x

def sphere(s):
    """
    Model a sphere in R^N.

    Parameters
    ----------
    s : array_like
        This parameter contains one or more points in the parameter
        space.  Multiple parameters are of the form s[length,nparm] where
        nparm is the dimensionality of the parameter space.  Single
        points are accepted as an ndarray s[1,nparm], tuple (u0,u1,...), or
        as a list [u0, u1, ...].

    Returns
    -------
    x : ndarray of surface points
        In R^3, x[:,0] corresponds to the x dimension, x[:,1] to the y
        and x[:,2] to the z.

    Notes
    -----
    This function generalizes an n-dimensional sphere by examining its
    input s to determine the number of parameters in the request.  For example
    a parameter request of dimension 2 (s[0]=latitude, s[1=longitude) implies
    a 2-sphere in R^3.  A three parameter request (s[0]=first latitude,
    s[1]=second latitude, s[2]=longitude implies a 3-sphere in R^4, etc.

    Examples
    --------
    import cva
    sa = (0.4,0.5)
    x,y,z = cva.model.sphere(sa)

    In this example, the point defined by u = 0.4 and v = 0.5 is mapped into
    its corresponding point on the model's surface and that result is returned
    as a row array of points in cartesian coordinates.
    """
    s, x = startmodel(s)

    # start of model mapping
    n = np.shape(s)[1]

    # Convert to rectangular coordinate system
    prod = 1.0
    for i in range(n-1):
        x[:, n-i] = prod * np.cos(np.pi * s[:, i])
        prod = prod * np.sin(np.pi * s[:, i])
    x[:, 0] = prod * np.cos(2*np.pi * (s[:, n-1]-0.5))
    x[:, 1] = prod * np.sin(2*np.pi * (s[:, n-1]-0.5))
    # end of model mapping

    x = finishmodel(x, s)
    return x


if __name__ == "__main__":

    print "running cva/model.py"
