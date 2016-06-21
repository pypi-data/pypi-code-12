import logging
from database_structure import DatabaseStructure
from data_pulling_helpers import get_from_source_and_write_to_target
from command_helpers import get_default_tables, get_most_recent_ids
from data_slices.network_x_graph import NetworkXGraph
from data_slices.graph import Graph
from sql_query_helpers import list_tables


logger = logging.getLogger(__name__)


def create_structure(source_db_conn_dict, target_db_conn_dict,
                     config_file_path=None):
    d = initialize_database_structure(source_db_conn_dict, target_db_conn_dict)
    d.initially_populate(source_db_conn_dict)
    d.recursively_perform_operations('createstructure')
    get_default_tables(source_db_conn_dict, target_db_conn_dict)


def delete_data(source_db_conn_dict, target_db_conn_dict):
    d = initialize_database_structure(source_db_conn_dict, target_db_conn_dict)
    d.initially_populate(target_db_conn_dict)
    d.recursively_perform_operations('deletedata')
    get_default_tables(source_db_conn_dict, target_db_conn_dict)


def get_all_from_table(table_name, source_db_conn_dict, target_db_conn_dict):
    logger.info(
        "Filling the table {0}.{1} with full data from {2}.".format(
            target_db_conn_dict['db'], table_name,
            source_db_conn_dict['db']
        )
    )
    get_from_source_and_write_to_target(
        table_name, '0=0', source_db_conn_dict, target_db_conn_dict,
        overwrite=True
    )


def get_most_recent(table, column, howmany, where, source_db_conn_dict,
                    target_db_conn_dict, heavy=False, restriction_string='',
                    include_only=None, overwrite=False):
        ids = get_most_recent_ids(
            table, column, howmany, where, source_db_conn_dict
        )
        pull_data(
            table, column, ids, source_db_conn_dict, target_db_conn_dict,
            heavy, restriction_string, include_only, overwrite
        )


def initialize_database_structure(source_db_conn_dict, target_db_conn_dict):
    table_list = list_tables(source_db_conn_dict)
    d = DatabaseStructure(
        table_list,
        source_db_conn_dict,
        target_db_conn_dict
    )
    return d


def pull_data(table, column, column_values, source_db_conn_dict,
              target_db_conn_dict, heavy=False, restriction_string='',
              include_only=None, overwrite=False):
    structure_data = initialize_database_structure(
        source_db_conn_dict, target_db_conn_dict
    )

    networkx_graph = NetworkXGraph(
        structure_data, restriction_string, include_only
    ).graph_literal

    g = Graph(
        networkx_graph,
        source_db_conn_dict, target_db_conn_dict,
        heavy, overwrite
    )

    logger.info(
        "Now traversing the graph, starting from your initial data set."
    )
    g.equip_initial_node(table, column, column_values)

    while g.nodes_left_to_visit():
        current_node = g.next()

        for edge in current_node.get_edges(g):
            if edge in g.edges_visited:
                logger.debug(
                    "Not visiting edge {0}, already been visited".format(
                        edge.to_string()
                    )
                )
            else:
                g.account_for_edge(edge, current_node)
                g.add_edge_visited(edge)
                g.add_node_to_visit(g.get_other_node(edge, current_node))
        logger.debug("Nodes left to visit: {0}\n".format(
            [node.name for node in g.nodes_to_visit]
        ))
    logger.info(
        "Done traversing the graph. Now to get data into your database."
    )

    nodes = g.nodes
    if include_only:
        nodes = [n for n in g.nodes if n.name in include_only]
    for node in nodes:
        row_count = int(node.row_count()[0][0])
        logger.info("Number of rows to retrieve for table {0}: {1}.".format(
            node.name, row_count
        ))

        if row_count == 0:
            logger.info("Not dumping data for table with zero rows.")
        elif row_count < 100000:
            logger.info("Dumping data for table {0}.".format(node.name))
            get_from_source_and_write_to_target(
                node.name, node.compute_where_clause(), source_db_conn_dict,
                target_db_conn_dict, overwrite
            )
        else:
            logger.info("Sorry, too many rows in table {0}.".format(node.name))
