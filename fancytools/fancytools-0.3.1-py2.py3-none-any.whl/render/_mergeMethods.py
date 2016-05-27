# -*- coding: utf-8 *-*
'''
This module includes all methods to merge values from
GridRender.
"Merge" means in this case to handle an incoming  new value at a place in
the target where other values exists already.
Depending on the chosen target-class :mod:`nIOp.target` its also
possible that incoming values have an intensity < 1 because the orig.
values were splitted.
'''

from numpy import isnan



def last(values, position, intensity, value):
    values[position] = value * intensity
    return True


def max(values, position, intensity, value):
    old_value = values[position]
    if not isnan(old_value):
        value = old_value + intensity * (value - old_value)
        if value < old_value:
            return False
    values[position] = value
    return True


def min(values, position, intensity, value):
    old_value = values[position]
    if not isnan(old_value):
        value = old_value + intensity * (value - old_value)
        if value > old_value:
            return False
    values[position] = value
    return True


def sum(values, position, intensity, value):
    old_value = values[position]
    if not isnan(old_value):
        value = old_value + intensity * value
    else:
        value *= intensity
    values[position] = value
    return True


def density(values, position, intensity, value):
    values[position] += intensity
    return True
