# coding: utf-8
"""
    pyextend.formula
    ~~~~~~~~~~~~~~~~
    pyextend formula package

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""
import math


def haversine(lng1, lat1, lng2, lat2):
    """Compute km by geo-coordinate
    See also: haversine define https://en.wikipedia.org/wiki/Haversine_formula
    """
    # Convert coordinates to floats.
    lng1, lat1, lng2, lat2 = map(float, [lng1, lat1, lng2, lat2])

    # Convert to radians from degrees
    lng1, lat1, lng2, lat2 = map(math.radians, [lng1, lat1, lng2, lat2])

    # Compute distance
    dlng = lng2 - lng1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    c = 2 * math.asin(math.sqrt(a))
    km = 6367 * c
    return km
