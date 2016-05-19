'''
Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.
'''
from sxclient.query.query_handler import JSONBodyQueryHandler
from sxclient.exceptions import SXClusterNonFatalError

OPERATION_CLASSES = {}

__all__ = [
    'OPERATION_CLASSES', 'BaseOperation', 'SingleNodeOperation',
    'VolumeNodeOperation'
]


class BaseOperationMeta(type):
    '''
    It gathers all classes that inherit from BaseOperation
    and stores them in OPERATION_CLASSES.
    '''

    def __new__(mcls, name, bases, nmspc):
        if name in OPERATION_CLASSES:
            raise NameError('Operation with name %s already defined' % name)

        hidden_key = 'HIDDEN'
        hidden = nmspc.setdefault(hidden_key, False)

        cls = super(BaseOperationMeta, mcls).__new__(
            mcls, name, bases, nmspc
        )

        if not hidden:
            OPERATION_CLASSES[name] = cls

        return cls


class BaseOperation(object):
    __metaclass__ = BaseOperationMeta

    HIDDEN = True
    QUERY_HANDLER = JSONBodyQueryHandler

    def __init__(self, cluster, session):
        self.cluster = cluster
        self.session = session

    def call(self, *args, **kwargs):
        return self.call_on_cluster(*args, **kwargs)

    def json_call(self, *args, **kwargs):
        return self.call(*args, **kwargs).json()

    def _generate_body(self, *args, **kwargs):
        return {}

    def _generate_query_params(self, *args, **kwargs):
        raise NotImplementedError

    def _make_query(self, address, params, body):
        query_handler = self.QUERY_HANDLER(
            address, self.cluster, self.session
        )
        query_handler.prepare_query(params, body)
        query_handler.make_query()
        return query_handler.response

    def _get_all_cluster_nodes(self):
        ListNodes = OPERATION_CLASSES['ListNodes']
        operation = ListNodes(self.cluster, self.session)
        response = operation.json_call()
        return response[u'nodeList']

    def call_on_node(self, address, *args, **kwargs):
        body = self._generate_body(*args, **kwargs)
        query_params = self._generate_query_params(*args, **kwargs)
        return self._make_query(address, query_params, body)

    def call_on_nodelist(self, nodes, *args, **kwargs):
        response = None
        last_exception = None
        for node in nodes:
            try:
                response = self.call_on_node(node, *args, **kwargs)
                break
            except SXClusterNonFatalError as exc:
                last_exception = exc

        if response is None:
            raise last_exception

        return response

    def call_on_cluster(self, *args, **kwargs):
        nodes = self._get_all_cluster_nodes()
        return self.call_on_nodelist(nodes, *args, **kwargs)


class VolumeNodeOperation(BaseOperation):
    HIDDEN = True

    def call(self, volume, *args, **kwargs):
        LocateVolume = OPERATION_CLASSES['LocateVolume']
        operation = LocateVolume(self.cluster, self.session)
        response = operation.json_call(volume)
        nodelist = response[u'nodeList']
        return self.call_on_nodelist(nodelist, volume, *args, **kwargs)


class SingleNodeOperation(BaseOperation):
    HIDDEN = True

    def call(self, node_address, *args, **kwargs):
        return self.call_on_node(node_address, *args, **kwargs)
