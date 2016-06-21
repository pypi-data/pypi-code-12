import logging
from edge import Edge, EdgeSet
from node import Node


logger = logging.getLogger(__name__)


class Graph:
    def __init__(self, networkx_graph,
                 source_conn_dict, target_conn_dict,
                 heavy, overwrite):
        self.source_conn_dict = source_conn_dict
        self.target_conn_dict = target_conn_dict
        self.heavy = heavy
        self.overwrite = overwrite

        self.edges_visited = EdgeSet()
        self.nodes_to_visit = []
        self.current_node = None

        self.load_nodes(networkx_graph)
        self.load_edges(networkx_graph)

    def load_nodes(self, networkx_graph):
        args = (
            self.source_conn_dict, self.target_conn_dict, self.heavy
        )
        self.nodes = [Node(n, *args) for n in networkx_graph.nodes()]

    def load_edges(self, networkx_graph):
        self.edges = []
        for networkx_edge in networkx_graph.edges(data=True):
            new_edge = Edge(networkx_edge[2]['label'])
            self.edges.append(new_edge)

    def equip_initial_node(self, node_name, column_name, column_values):
        n = self.get_node(node_name)
        n.add_where_clause_piece(column_name, column_values)
        n.add_value_lookup(column_name, column_values)
        self.nodes_to_visit = [n]
        self.current_node = n

    def get_other_node(self, edge, one_node):
        if edge.source_table == one_node.name:
            return self.get_node(edge.target_table)
        else:
            return self.get_node(edge.source_table)

    def __iter__(self):
        return self

    def next(self):
        self.current_node = self.nodes_to_visit.pop(0)
        return self.current_node

    def nodes_left_to_visit(self):
        return len(self.nodes_to_visit) > 0

    def add_edge_visited(self, edge):
        self.edges_visited.add(edge)

    def add_node_to_visit(self, node):
        self.nodes_to_visit.append(node)

    def get_node(self, name):
        return next(n for n in self.nodes if n.name == name)

    def account_for_edge(self, edge, home_node):
        logger.debug(
            "Visiting the edge {0} from the node {1}.".format(
                edge.to_string(), home_node.name
            )
        )
        away_node = self.get_other_node(edge, home_node)
        home_column, away_column = home_node.get_home_and_away_columns(edge)

        if home_column not in home_node.value_lookup.keys():
            home_node.compute_column_values(home_column)

        column_values = home_node.get_column_values(home_column)
        away_node.add_new_column(away_column, column_values)
