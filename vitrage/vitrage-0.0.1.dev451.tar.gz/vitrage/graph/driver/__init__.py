# Copyright 2016 - Nokia
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from elements import *  # noqa
from graph import *  # noqa
from networkx_graph import NXGraph


def create_graph(name, root_id=None):
    """Create a Graph instance

    For now only return NXGraph

    :param root_id:
    :type name: str
    :rtype: Graph
    """
    return NXGraph(name, root_id)
