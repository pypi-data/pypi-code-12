import networkx as nx
from ..config_helpers import load_config


class NetworkXGraph:
    def __init__(self, structure_data, restriction_string, include_only):
        self.graph_literal = nx.MultiGraph()
        self.restriction_string = restriction_string
        self.include_only = include_only
        self.build_nodes(structure_data.table_list)
        self.build_edges(structure_data.foreign_keys)

    def add_node(self, table_name):
        self.graph_literal.add_node(table_name)

    def add_edge(self, source_table, target_table,
                 label, config_file_path=None):
        try:
            default_tables = load_config(config_file_path).DEFAULT_TABLES
        except (KeyError, ImportError):
            default_tables = []

        rules = (
            source_table not in default_tables,
            target_table not in default_tables
        )
        if self.restriction_string:
            rules += (
                self.restriction_string in source_table,
                self.restriction_string in target_table
            )
        if self.include_only:
            rules += (
                source_table in self.include_only,
                target_table in self.include_only
            )
        if all(rules):
            self.graph_literal.add_edge(
                source_table, target_table, label=label
            )
            return source_table, target_table
        else:
            return None

    def build_nodes(self, table_names):
        for table_name in table_names:
            if self.restriction_string in table_name:
                self.add_node(table_name)

    def build_edges(self, foreign_keys):
        for fk in foreign_keys:
            self.add_edge(fk.source_table, fk.target_table, fk)
