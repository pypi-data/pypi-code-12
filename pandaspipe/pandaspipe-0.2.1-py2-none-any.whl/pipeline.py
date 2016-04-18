# -*- coding:utf-8 -*-
import abc
import sys
import inspect
import types
import itertools
import networkx as nx
from _util import patch_list, isSubset
from base import PipelineEntity
import logging

_log = logging.getLogger(__name__)
_log.addHandler(logging.StreamHandler(stream=sys.stdout))


class Pipeline:
    def __init__(self, name='Undefined Pipeline', env=None):
        """(Pipeline, str) -> NoneType
        Creating the contents of the Pipeline Object
        """
        if env is None:
            env = {}
        self._entities = []
        self.name = name
        self.env = env
        self.graph = None

    def process(self, channels=('root',), ignore_outlet_node=False, output_channels=()):
        """(Pipeline, pandas.DataFrame, str) -> type(df_map)
        *Description*
        :param ignore_outlet_node:
        """
        start_nodes = [self._get_start_node(channel) for channel in channels]
        active_dfs = {}
        active_nodes = []
        acomplete_nodes = self.graph.nodes()
        complete_nodes = []
        active_nodes.extend(start_nodes)
        while len(active_nodes) > 0:
            next_nodes = []
            processed = False
            for active_node in active_nodes:
                pred_nodes = self.graph.pred.get(active_node).keys()
                depencencies = active_node.external_dependencies
                if (len(pred_nodes) == 0 or isSubset(complete_nodes, pred_nodes)) and isSubset(active_dfs.keys(), depencencies):
                    _log.info('Call entity %s' % active_node)
                    processed = True
                    # Process
                    parameters = [active_dfs[channel] for channel in active_node.input_channels]
                    if active_node.type in ('node', 'bignode'):
                        external_dependencies = {}
                        if active_node.external_dependencies:
                            for external_dependency in active_node.external_dependencies:
                                external_dependencies[external_dependency] = active_dfs[external_dependency]
                        self.env['ext_dep'] = external_dependencies
                    result = active_node(*parameters)
                    active_nodes.remove(active_node)
                    complete_nodes.append(active_node)
                    acomplete_nodes.remove(active_node)
                    # Update active dataframes
                    if len(active_node.output_channels) == 1:
                        active_dfs[active_node.output_channels[0]] = result
                    elif len(active_node.output_channels) > 1:
                        active_dfs.update(result)
                    # Add next nodes
                    for node in self.graph.succ.get(active_node).keys():
                        if node not in active_nodes and node not in next_nodes:
                            next_nodes.append(node)
            if not processed:
                _log.error('Infinite cycle detected!')
                return None
            active_nodes.extend(next_nodes)
            # Clear useless dfs
            # Check if required by next node
            for channel in active_dfs.keys():
                if channel not in output_channels and len(
                        [active_node for active_node in active_nodes if channel in active_node.input_channels]) == 0:
                    # Check if required by external dependencies
                    required = reduce(lambda x, y: x or y, [channel in node.external_dependencies for node in acomplete_nodes], False)
                    if not required:
                        active_dfs.pop(channel)
        if len(active_dfs.keys()) == 1:
            return active_dfs.values()[0]
        return active_dfs

    def append(self, cls, channel=None, output_channel=None, construct_arguments=()):
        """(Pipeline, classobj, str, str) -> NoneType
        *Description*
        :param construct_arguments:
        :param cls:
        :param channel:
        :param output_channel:
        """
        self(channel, output_channel, construct_arguments=construct_arguments)(cls)

    def build_process_graph(self):
        builder = GraphBuilder(self._entities)
        return builder.build()

    def _check_graph(self):
        if self.graph is None:
            self.graph = self.build_process_graph()

    def _get_start_node(self, channel):
        self._check_graph()
        nodes = filter(lambda x: channel in x.output_channels and x.type == 'source', self.graph.nodes())
        if len(nodes) > 0:
            return nodes[0]
        raise Exception('You can\'t use channel without source node')

    def _process_entity(self, cls, channel, outchannel, construct_arguments, priority):
        """(Pipeline, type(cls), type(channel), type(outchannel),
        type(entity_map)) -> type(cls)
        *Description*
        """
        obj = cls(*construct_arguments)
        obj.env = self.env
        if priority:
            obj.priority = priority
        obj.register(self)
        self._entities.append(obj)
        if channel is None and len(obj.input_channels) == 0 and len(obj.output_channels) == 0:
            channel = 'root'
        if channel:
            if outchannel is None:
                outchannel = channel
            if obj.type == 'node':
                obj.input_channels = channel[:1] if isinstance(channel, list) else [channel]
                obj.output_channels = outchannel[:1] if isinstance(outchannel, list) else [outchannel]
            elif obj.type == 'bignode':
                patch_list(obj.input_channels, channel)
                patch_list(obj.output_channels, outchannel)
            elif obj.type == 'source':
                obj.input_channels = []
                patch_list(obj.output_channels, outchannel)
            elif obj.type == 'outlet':
                patch_list(obj.input_channels, channel)
                obj.output_channels = []
            else:
                raise Exception('Well, you use bad type for entity ....')
        return cls

    def __call__(self, channel=None, outchannel=None, construct_arguments=(), priority=None):
        """(Pipeline, str, str) ->
        type(process_function)
        *Description*
        """

        def process_function(cls):
            """(type(cls)) ->
            type(self._process_entity(cls, channel, outchannel, self._filters))
            *Description*
            :param cls:
            """
            cls_mro = inspect.getmro(cls)
            if PipelineEntity in cls_mro:
                self._process_entity(cls, channel, outchannel, construct_arguments, priority)
            return cls

        if isinstance(channel, types.ClassType) or isinstance(channel, abc.ABCMeta):
            cls = channel
            channel = None
            return process_function(cls)

        return process_function


class GraphBuilder:

    def __init__(self, entities):
        self.entities = entities
        self.channel_io_nodes = {}
        self.graph = nx.DiGraph()
        pass

    def build(self):
        self.graph.add_nodes_from(self.entities)
        self._build_inchannel_connections()
        self._build_multichannel_connections()
        self._validate_external_dependencies()
        return self.graph

    def _build_inchannel_connections(self):
        all_channels = set(
            itertools.chain(*map(lambda x: set(itertools.chain(x.input_channels, x.output_channels)), self.entities)))
        for channel in all_channels:
            # Process simple nodes
            channel_nodes = filter(lambda x: x.type == 'node'
                                             and channel in x.input_channels and channel in x.output_channels,
                                   self.entities)
            channel_nodes.sort(key=lambda x: (x.priority, x.__class__.__name__))
            self.channel_io_nodes[channel] = {}
            if len(channel_nodes) > 0:
                self.channel_io_nodes[channel]['input'] = channel_nodes[0]
                self.channel_io_nodes[channel]['output'] = channel_nodes[-1]
            # noinspection PyCompatibility
            for i in xrange(0, len(channel_nodes) - 1):
                self.graph.add_edge(channel_nodes[i], channel_nodes[i + 1])
            # Process outlet and source
            input_nodes = filter(lambda x: x.type == 'source' and channel in x.output_channels, self.entities)
            assert len(input_nodes) in (0, 1), 'You can\'t use many input nodes for one channel'
            if len(input_nodes) > 0:
                if len(channel_nodes) > 0:
                    self.graph.add_edge(input_nodes[0], self.channel_io_nodes[channel]['input'])
                else:
                    self.graph.add_node(input_nodes[0])
                    self.channel_io_nodes[channel]['output'] = input_nodes[0]
            output_nodes = filter(lambda x: x.type == 'outlet' and channel in x.input_channels, self.entities)
            self.graph.add_nodes_from(output_nodes)
            if len(output_nodes) > 0:
                self.channel_io_nodes[channel]['outlets'] = output_nodes
                if len(channel_nodes) > 0:
                    for output_node in output_nodes:
                        self.graph.add_edge(self.channel_io_nodes[channel]['output'], output_node)
        pass

    def _build_multichannel_connections(self):
        for node in filter(lambda x: x.type in ('bignode', 'node') and x.input_channels != x.output_channels,
                           self.entities):
            for input_channel in node.input_channels:
                self.graph.add_edge(self.channel_io_nodes[input_channel]['output'], node)
            for output_channel in node.output_channels:
                channel_info = self.channel_io_nodes[output_channel]
                if not channel_info.get('input') and not channel_info.get('outlets'):
                    raise Exception('You have problem with graph')
                if channel_info.get('input'):
                    self.graph.add_edge(node, channel_info['input'])
                if channel_info.get('outlets'):
                    for outlet in channel_info.get('outlets'):
                        self.graph.add_edge(node, outlet)

    def _validate_external_dependencies(self):

        pass
