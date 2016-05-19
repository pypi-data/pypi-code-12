'''
Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.
'''
import copy

from sxclient.exceptions import OperationError
from sxclient.operations.base import BaseOperation, OPERATION_CLASSES
from sxclient.models.query_parameters import QueryParameters

__all__ = [
    'GetClusterStatus', 'GetClusterMetadata', 'SetClusterMetadata',
    'ModifyCluster', 'ResizeCluster'
]


class GetClusterStatus(BaseOperation):
    '''
    Get status information about the cluster.

    Required access: admin.
    '''

    def _generate_query_params(self):
        return QueryParameters(
            sx_verb='GET',
            bool_params={
                'clusterStatus',
                'operatingMode',
                'raftStatus',
                'distZones',
            }
        )


class GetClusterMetadata(BaseOperation):
    '''
    Get metadata associated with the cluster.

    Required access: normal.
    '''

    def _generate_query_params(self):
        return QueryParameters(
            sx_verb='GET',
            bool_params={'clusterMeta'}
        )


class SetClusterMetadata(BaseOperation):
    '''
    Set metadata associated with the cluster.

    Required access: admin.

    Query-specific parameters:
      - clusterMeta -- dictionary containing key-value metadata pairs. The
        values have to be hex-encoded.
    '''

    def _generate_body(self, cluster_meta):
        return {u'clusterMeta': cluster_meta}

    def _generate_query_params(self, cluster_meta):
        return QueryParameters(
            sx_verb='JOB_PUT',
            path_items=['.clusterMeta']
        )


class ModifyCluster(BaseOperation):
    '''
    Modify the cluster by adding, removing or resizing nodes.

    Required access: admin.

    Query-specific parameters:
      - node_list -- list containing new definitions of the nodes. Every
        element should be a dictionary with "nodeAddress", "nodeCapacity" and
        "nodeUUID" keys.
      - zone_info -- string describing zone distribution.
    '''

    def _generate_body(self, node_list, zone_info=None):
        body = {u'nodeList': node_list}
        if zone_info is not None:
            body[u'distZones'] = zone_info
        return body

    def _generate_query_params(self, node_list, zone_info=None):
        return QueryParameters(
            sx_verb='JOB_PUT',
            path_items=['.nodes']
        )


class ResizeCluster(ModifyCluster):
    '''
    Resize the cluster by proportionally resizing the nodes.

    Required access: admin.

    Query-specific parameters:
      - size -- number of bytes to change the cluster size with.
    '''

    def _get_cluster_status(self):
        get_status_class = OPERATION_CLASSES['GetClusterStatus']
        get_status_inst = get_status_class(self.cluster, self.session)
        response = get_status_inst.json_call()
        return response

    def _update_node_sizes(self, node_list, size):
        new_node_list = copy.deepcopy(node_list)

        old_size = sum(elt['nodeCapacity'] for elt in node_list)
        new_size = old_size + size
        if new_size <= 0:
            raise OperationError('Resize value exceeds cluster size')

        for elt in new_node_list:
            old_capacity = elt['nodeCapacity']
            new_capacity = int(float(old_capacity) / old_size * new_size)
            elt['nodeCapacity'] = new_capacity
        return new_node_list

    def call(self, size):
        size = int(size)
        status = self._get_cluster_status()
        distribution_models = status['clusterStatus']['distributionModels']
        if len(distribution_models) > 1:
            raise OperationError(
                'The cluster is being rebalanced and cannot be resized'
            )

        model = distribution_models[0]
        if isinstance(model[-1], basestring):
            zone_info = model.pop()
        else:
            zone_info = None
        new_node_list = self._update_node_sizes(model, size)
        return super(ResizeCluster, self).call(new_node_list, zone_info)
