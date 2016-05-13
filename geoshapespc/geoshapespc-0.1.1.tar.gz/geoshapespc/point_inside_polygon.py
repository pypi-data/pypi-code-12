# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 15:07:54 2015

Module created to check if a given point is located inside a given polygon
by checking the point coordinates against the boundaries of the polygon.

This module was created and modified based in a code provided by Joel Lawhead
at GeospatialPython (http://geospatialpython.com/2011/08/point-in-polygon
-2-on-line.html).

The original code is hosted at:
https://geospatialpython.googlecode.com/svn/trunk/PiP_Edge.py

@author: Matheus Boni Vicari (matheus.boni.vicari@gmail.com)
"""


# determine if a point is inside a given polygon or not
# Polygon is a list of (x,y) pairs.
def point_inside_polygon(x, y, poly):

    """
    Function defined to check if a given point is inside a given polygon by
    checking the point coordinates agains the boundaries coordinates. This
    function also consider points placed on the boundaries/vertices as being
    inside of the polygon.

    Params
    ------
    x, y: numpy.float64
            Pair of coordinates of the point to check.
    poly: numpy.ndarray
            Sets of 2D coordinates that are part of the polygon boundaries/
            vertices.

    Returns
    -------
    inside: bool
            Value stating True if the point is inside the polygon and False if
            the point is not inside the polygon.

    Usage
    -----
    >>> inside = point_inside_polygon.point_inside_polygon(x, y, poly)

    """

    # Check if point is a vertex.
    if (x, y) in poly:
        return True

    # check if point is on a boundary
    for i in range(len(poly)):
        p1 = None
        p2 = None
        if i == 0:
            p1 = poly[0]
            p2 = poly[1]
        else:
            p1 = poly[i-1]
            p2 = poly[i]
        if (p1[1] == p2[1] and p1[1] == y and x > min(p1[0], p2[0]) and
           x < max(p1[0], p2[0])):
            return True

    n = len(poly)
    inside = False

    p1x, p1y = poly[0]
    for i in range(n+1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y

    if inside:
        return True
    else:
        return False

if __name__ == "__main__":

    # Test a vertex for inclusion.
    poly1 = [(-33.416032, -70.593016), (-33.415370, -70.589604),
             (-33.417340, -70.589046), (-33.417949, -70.592351),
             (-33.416032, -70.593016)]
    lat = -33.416032
    lon = -70.593016
    point_inside_polygon(lat, lon, poly1)

    # Test a boundary point for inclusion.
    poly2 = [(1, 1), (5, 1), (5, 5), (1, 5), (1, 1)]
    x = 3
    y = 1
    point_inside_polygon(x, y, poly2)
