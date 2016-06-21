import logging
from data_pulling_helpers import get_from_source_and_write_to_target
from config_helpers import load_config
from sql_query_helpers import get_sql_result


logger = logging.getLogger(__name__)


def get_default_tables(source_db_conn_dict, target_db_conn_dict,
                       config_file_path=None):
    try:
        default_tables = load_config(config_file_path).DEFAULT_TABLES
    except ImportError:
        return

    logger.info(
        "Getting full data for default tables in configuration: {0}".format(
            ", ".join(default_tables)
        )
    )

    for table_name in default_tables:
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


def get_most_recent_id_query(table, column, where, howmany):
    where_clause = 'WHERE {}'.format(where) if where else ''
    return "SELECT {1} FROM {0} {2} ORDER BY {1} DESC LIMIT {3}".format(
        table, column, where_clause, howmany
    )


def get_most_recent_ids(table, column, howmany, where, source_db_conn_dict):
    sql = get_most_recent_id_query(table, column, where, howmany)
    return "({0})".format(','.join(
        [str(r[0]) for r in get_sql_result(sql, source_db_conn_dict)]
    ))
