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
    """Compute km by geo-coordinates
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


def calc_distance(lng1, lat1, lng2, lat2):
    """Calc distance (km) by geo-coordinates.
        @:param lng1: first coordinate.lng
        @:param lat1: first coordinate.lat
        @:param lng2: second coordinate.lng
        @:param lat2: second coordinate.lat
        @:return distance: km
    """
    ra = 6378.140  # 赤道半径 (km)
    rb = 6356.755  # 极半径 (km)
    flatten = (ra - rb) / ra  # 地球扁率
    rad_lat_1 = math.radians(lat1)
    rad_lng_1 = math.radians(lng1)
    rad_lat_2 = math.radians(lat2)
    rad_lng_2 = math.radians(lng2)
    p1 = math.atan(rb / ra * math.tan(rad_lat_1))
    p2 = math.atan(rb / ra * math.tan(rad_lat_2))
    xx = math.acos(math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(rad_lng_1 - rad_lng_2))
    c1 = (math.sin(xx) - xx) * (math.sin(p1) + math.sin(p2)) ** 2 / math.cos(xx / 2) ** 2
    c2 = (math.sin(xx) + xx) * (math.sin(p1) - math.sin(p2)) ** 2 / math.sin(xx / 2) ** 2
    dr = flatten / 8 * (c1 - c2)
    distance = ra * (xx + dr)
    return distance
