# -*- encoding: utf-8 -*-
"""
    flask_triangle.modifiers.limits
    -------------------------------

    A collection of modifiers for Flask-Triangle's widgets.

    :copyright: (c) 2013 by Morgan Delahaye-Prat.
    :license: BSD, see LICENSE for more details.
"""


from __future__ import absolute_import, division, print_function, unicode_literals

from .required import Required
from .patterns import Regexp, PatternProperty
from .multiple import Multiple
from .types import AsBoolean, AsInteger
from .limits import Minimum, Maximum, MinimumLength, MaximumLength
from .noschema import NoSchema

__all__ = ['Required', 'Regexp', 'PatternProperty', 'Multiple', 'AsBoolean',
           'Minimum', 'Maximum', 'MinimumLength', 'MaximumLength', 'AsInteger',
           'NoSchema']
