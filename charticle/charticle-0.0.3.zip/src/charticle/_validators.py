"""Validation routines for specifying values to objects."""
import re

import attr
import numbers
import six

from matplotlib import colors


def _pretty_value_error(inst, attrib, value, comment):
    raise ValueError("%s %s value %r %s"
                     % (type(inst), attrib.name, value, comment))

# Attributes for various validation executions.
is_string = attr.validators.instance_of(six.string_types)
is_integer = attr.validators.instance_of(six.integer_types)
is_real = attr.validators.instance_of(numbers.Real)

optional_string = attr.validators.optional(is_string)


def non_negative(inst, attrib, value):
    is_real(inst, attrib, value)
    if value < 0.0:
        _pretty_value_error(inst, attrib, value, "is negative")


def positive(inst, attrib, value):
    is_real(inst, attrib, value)
    if value <= 0.0:
        _pretty_value_error(inst, attrib, value, " not positive")


def zero_to_one(inst, attrib, value):
    is_real(inst, attrib, value)
    if value < 0.0 or value > 1.0:
        _pretty_value_error(inst, attrib, value, "outside of [0,1] interval")


def positive_int(inst, attrib, value):
    is_integer(inst, attrib, value)
    positive(inst, attrib, value)


def legal_color(inst, attrib, value):
    is_string(inst, attrib, value)
    if (value not in colors.cnames and not re.match(r'^#[0-9a-fA-F]{6}$',
                                                    value)):
        _pretty_value_error(inst, attrib, value, "not a legal color name")


optional_legal_color = attr.validators.optional(legal_color)
