# -*- coding: utf-8 -*-
# Copyright (C) 2015  Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# the GNU General Public License v.2, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY expressed or implied, including the implied warranties of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the
# GNU General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.  Any Red Hat trademarks that are incorporated in the
# source code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission of
# Red Hat, Inc.
#
# Red Hat Author(s): Anne Mulhern <amulhern@redhat.com>

"""
    printdevDAG._print._graph
    =========================

    Textual display of graph.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from printdevDAG._utils import GeneralUtils


class GraphLineInfo(object):
    """
    Class that generates info for a single line that represents a graph.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, graph, keys, alignment, getters):
        """
        Initializer.

        :param graph: the relevant networkx graph
        :param keys: a list of keys which are also column headings
        :param alignment: alignment for column headers
        :type alignment: dict of str * str {'<', '>', '^'}
        :param getters: getters for each column, indexed by column name
        :type getters: map of str * NodeGetter
        """
        self.keys = keys
        self.alignment = alignment
        self.graph = graph

        # functions, indexed by column name
        self._funcs = dict(
           (k, GeneralUtils.composer([g.getter for g in getters[k]])) \
              for k in keys
        )

    def info(self, node, keys=None, conv=lambda k, v: v):
        """
        Function to generate information to be printed for ``node``.

        :param `Node` node: the node
        :param keys: list of keys for values or None
        :type keys: list of str or NoneType
        :param conv: a conversion function that converts values to str
        :type conv: (str * object) -> str
        :returns: a mapping of keys to values
        :rtype: dict of str * (str or NoneType)

        Only values for elements at x in keys are calculated.
        If keys is None, return an item for every index.
        If keys is the empty list, return an empty dict.
        Return None for key in keys that can not be satisfied.

        If strings is set, convert all values to their string representation.
        """
        if keys is None:
            keys = self.keys

        return dict(
           (
              k,
              conv(k, self._funcs.get(k, lambda n: None)(self.graph.node[node]))
           ) for k in keys
        )
