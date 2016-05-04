#!/usr/bin/python
# -*- coding: utf-8 -*-

import math

def floor(value, places):
    """
    Rounds the provided value to the upper most value
    according to the provided number of places.

    This is just a proxy function that allows working
    with the floor operation with a variable number of
    decimal places instead of a plain integer.

    @type value: float
    @param value: The value fo which the floor value is
    going to be calculated.
    @type places: int
    @param places: The number of decimal places that are
    going to be used in the floor operation.
    @rtype: float
    @return: The floating point number representing the
    floor version of the provided value, according to the
    requested number of places.
    """

    multiplier = math.pow(10, places)
    value = value * multiplier
    value = math.floor(value)
    return value / multiplier

def ceil(value, places):
    """
    Rounds the provided value to the upper most value
    according to the provided number of places.

    This is just a proxy function that allows working
    with the ceil operation with a variable number of
    decimal places instead of a plain integer.

    @type value: float
    @param value: The value fo which the ceil value is
    going to be calculated.
    @type places: int
    @param places: The number of decimal places that are
    going to be used in the ceil operation.
    @rtype: float
    @return: The floating point number representing the
    ceil version of the provided value, according to the
    requested number of places.
    """

    multiplier = math.pow(10, places)
    value = value * multiplier
    value = math.ceil(value)
    return value / multiplier
