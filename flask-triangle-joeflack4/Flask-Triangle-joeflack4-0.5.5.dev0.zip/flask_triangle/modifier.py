# -*- encoding: utf-8 -*-
"""
"""

from __future__ import absolute_import, division, print_function, unicode_literals


class Modifier(object):
    """
    The base class for every validators.
    """

    def __init__(self):
        self.attributes = dict()

    def alter_schema(self, schema, fqn):
        return True
