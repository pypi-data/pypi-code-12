# -*- coding: utf-8 -*-

from .errors import MetzooInvalidData


def sanitize(value, name, expected_types):
    if type(expected_types) is not list:
        expected_types = [expected_types]

    if type(value) not in expected_types:
        raise MetzooInvalidData(got=type(value), expected="one of {} for {}".format(expected_types, name))

    return value
