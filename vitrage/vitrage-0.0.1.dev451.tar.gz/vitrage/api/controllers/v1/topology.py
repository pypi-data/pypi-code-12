# Copyright 2016 - Alcatel-Lucent
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import json

from oslo_log import log
import pecan
from pecan.core import abort

from vitrage.api.controllers.rest import RootRestController
from vitrage.api.policy import enforce

# noinspection PyProtectedMember
from vitrage.i18n import _LI


LOG = log.getLogger(__name__)


class TopologyController(RootRestController):

    @pecan.expose('json')
    def post(self, depth, graph_type, query, root):
        enforce("get topology", pecan.request.headers,
                pecan.request.enforcer, {})

        LOG.info(_LI('received get topology: depth->%(depth)s '
                     'graph_type->%(graph_type)s root->%(root)s') %
                 {'depth': depth, 'graph_type': graph_type, 'root': root})

        if query:
            query = json.loads(query)

        LOG.info(_LI("query is %s") % query)

        if pecan.request.cfg.api.use_mock_file:
            return self.get_mock_data('graph.sample.json', graph_type)
        else:
            return self.get_graph(graph_type, depth, query, root)

    @staticmethod
    def get_graph(graph_type, depth, query, root):

        try:
            graph_data = pecan.request.client.call(pecan.request.context,
                                                   'get_topology',
                                                   graph_type=graph_type,
                                                   depth=depth,
                                                   query=query, root=root)
            LOG.info(graph_data)
            graph = json.loads(graph_data)
            if graph_type == 'graph':
                return graph
            if graph_type == 'tree':
                return RootRestController.as_tree(graph)

        except Exception as e:
            LOG.exception('failed to get topology %s ', e)
            abort(404, str(e))
