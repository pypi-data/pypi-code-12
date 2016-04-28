import networkx as nx
from tinycm import InvalidParameterError


class CMGraph(object):
    def __init__(self, configuration):
        self.graph = nx.DiGraph()

        # Add the nodes in the graph
        for identifier in configuration.definitions:
            self.graph.add_node(configuration.definitions[identifier])

        # Add the edges in the graph
        for identifier in configuration.definitions:
            if len(configuration.definitions[identifier].after) > 0:
                for edge in configuration.definitions[identifier].after:
                    edge_from = configuration.definitions[identifier]
                    if edge in configuration.definitions:
                        edge_to = configuration.definitions[edge]
                    else:
                        raise InvalidParameterError(
                            'Definition {} does not exist (referenced in {}->after)'.format(edge, identifier))
                    self.graph.add_edge(edge_from, edge_to)

    def get_sorted_jobs(self):
        return nx.topological_sort(self.graph, reverse=True)
