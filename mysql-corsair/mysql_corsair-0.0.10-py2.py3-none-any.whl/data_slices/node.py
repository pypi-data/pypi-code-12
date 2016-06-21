import logging
from .. import sql_query_helpers


logger = logging.getLogger(__name__)


class Node:
    def __init__(self, name, source_conn_dict, target_conn_dict, heavy):
        self.name = name
        self.where_clause_pieces = []
        self.value_lookup = {}

        self.source_conn_dict = source_conn_dict
        self.target_conn_dict = target_conn_dict
        self.heavy = heavy

    def get_edges(self, g):
        return [e for e in g.edges if self.name in e.node_names]

    def add_where_clause_piece(self, column_name, column_values):
        if isinstance(column_values, list):
            column_values = "({})".format(
                ','.join([str(s) for s in column_values])
            )
        self.where_clause_pieces.append(
            '{0} IN {1}'.format(column_name, column_values)
        )

    def add_value_lookup(self, column_name, column_values):
        self.value_lookup[column_name] = column_values

    def is_source_table_of(self, edge):
        return (edge.source_table == self.name)

    def compute_column_values(self, column_name):
        logger.debug(
            "Computing column values for {0} for the table {1}.".format(
                column_name, self.name
            )
        )

        sql_result = sql_query_helpers.get_sql_result(
            "SELECT DISTINCT {0} FROM {1} WHERE {2}".format(
                column_name,
                self.name,
                self.compute_where_clause()
            ),
            self.source_conn_dict
        )
        column_values = sql_query_helpers.convert_to_query_ready_string(
            sql_result
        )
        logger.debug("Column values: {0}".format(column_values))
        self.add_value_lookup(column_name, column_values)

    def compute_where_clause(self):
        conjunction = 'OR' if self.heavy else 'AND'
        if len(self.where_clause_pieces) > 0:
            return " {0} ".format(conjunction).join(self.where_clause_pieces)
        return "null"

    def row_count(self):
        return sql_query_helpers.get_sql_result(
            "SELECT COUNT(1) FROM {0} WHERE {1}".format(
                self.name, self.compute_where_clause()
            ),
            self.source_conn_dict
        )

    def get_home_and_away_columns(self, edge):
        source, target = edge.source_column, edge.target_column
        home_and_away_columns = (target, source)
        if self.is_source_table_of(edge):
            home_and_away_columns = (source, target)
        return home_and_away_columns

    def get_column_values(self, column_name):
        return self.value_lookup[column_name]

    def add_new_column(self, column_name, column_values):
        self.add_value_lookup(
            column_name, column_values
        )
        if column_values != '()':
            logger.debug(
                "Storing values {0} for column {1} in node {2}.".format(
                    column_values, column_name, self.name
                )
            )
            self.add_where_clause_piece(
                column_name, column_values
            )
