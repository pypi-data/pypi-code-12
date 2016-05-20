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
    printdevDAG._depth
    ==================

    Do a depth first search of DAG.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pydevDAG

from printdevDAG._utils import GeneralUtils


class GraphLineArrangementsConfig(object):
    """
    Class that represents the configuration for LineArrangements methods.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, info_func, conversion_func, sort_key):
        """
        Initializer.

        :param info_func: a function that returns information for a node
        :type info_func: see LineInfo.info
        :param conversion_func: converts info_func values to str
        :type conversion_func: (str * object) -> str
        :param str sort_key: the key/column name to sort on
        """
        self.info_func = info_func
        self.conversion_func = conversion_func
        self.sort_key = sort_key


class GraphLineArrangements(object):
    """
    Sort out nodes and their relationship to each other in printing.
    """
    # pylint: disable=too-few-public-methods

    @classmethod
    def node_strings_from_graph(cls, config, graph):
        """
        Generates print information about nodes in graph.
        Starts from the roots of the graph.

        :param LineArrangementsConfig: config
        :param `DiGraph` graph: the graph

        :returns: a table of information to be used for further display
        :rtype: list of dict of str * object

        Fields in table:
        * indent - the level of indentation
        * last - whether this node is the last child of its parent
        * node - the table of information about the node itself
        * orphan - whether this node has no parents
        """
        nodes = pydevDAG.DepthFirst.nodes(
           graph,
           key_func=GeneralUtils.str_key_func_gen(
              lambda n: config.info_func(n, [config.sort_key])[config.sort_key]
           )
        )

        for (depth, node, last) in nodes:
            yield {
               'indent' : depth,
               'last' : last,
               'node' :
                  config.info_func(
                     node,
                     keys=None,
                     conv=config.conversion_func
                  ),
               'orphan' : depth == 0
            }


class GraphXformLines(object):
    """
    Use information to transform the fields in the line.
    """

    _EDGE_STR = "|-"
    _LAST_STR = "`-"

    @classmethod
    def indentation(cls):
        """
        Return the number of spaces for the next indentation level.

        :returns: indentation
        :rtype: int
        """
        return len(cls._EDGE_STR)

    @classmethod
    def calculate_prefix(cls, line_info):
        """
        Calculate left trailing spaces and edge characters to initial value.

        :param line_info: a map of information about the line
        :type line_info: dict of str * object

        :returns: the prefix str for the first column value
        :rtype: str
        """
        edge_string = "" if line_info['orphan'] else \
           (cls._LAST_STR if line_info['last'] else cls._EDGE_STR)
        return " " * ((line_info['indent'] - 1)* cls.indentation()) + \
           edge_string

    @classmethod
    def xform(cls, column_headers, lines):
        """
        Transform column values and yield just the line info.

        :param column_headers: the column headers
        :type column_headers: list of str
        :param lines: information about each line
        :type lines: dict of str * str
        """
        key = column_headers[0]

        for line in lines:
            line_info = line['node']
            line_info[key] = cls.calculate_prefix(line) + line_info[key]
            yield line_info
