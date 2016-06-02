import re
import command_helpers
import commands
import sql_query_helpers
from config_helpers import load_config


POSSIBLE_ACTIONS = [
    'createstructure', 'getmostrecent', 'pulldata', 'deletedata',
    'actions', 'args'
]


def process_values(value_string):
    template = "(%s)"

    def format(value):
        it_doesnt_need_formatting = re.compile("^[0-9]+$").match(value)
        return value if it_doesnt_need_formatting else "\'{0}\'".format(value)
    return template % ', '.join(map(format, value_string.split(',')))


def get_invalid_actions(actions):
    return [a for a in actions if a not in POSSIBLE_ACTIONS]


def get_missing_pulldata_args(args):
    relevant_args = {
        "--table": args.table,
        "--column": args.column,
        "--values": args.values
    }
    return [a for a in relevant_args if relevant_args[a] is None]


def get_invalid_pulldata_args(args):
    relevant_args = {
        "--howmany": args.howmany,
        "--where": args.where
    }
    return [a for a in relevant_args if relevant_args[a]]


def get_missing_getmostrecent_args(args):
    relevant_args = {
        "--table": args.table,
        "--column": args.column,
        "--howmany": args.howmany
    }
    return [a for a in relevant_args if relevant_args[a] is None]


def well_formed_values_string(args):
    return re.compile("\(.*\)").match(args.values)


def get_query_status(actions, args, conn_dict):
    if 'pulldata' in actions:
        query = "SELECT * FROM {0} WHERE {1} IN {2}".format(
            args.table, args.column, args.values
        )
    elif 'getmostrecent' in actions:
        query = command_helpers.get_most_recent_id_query(
            args.table, args.column, args.where, args.howmany)
    else:
        query = ''

    try:
        result = sql_query_helpers.get_sql_result(query, conn_dict)
    except:
        return {"status": "error", "query": query}

    if len(result) == 0:
        return {"status": "empty", "query": query}

    return {"status": "success", "query": query}


def validity_info(args, actions):
    msgs = []

    invalid_actions = get_invalid_actions(actions)
    if len(invalid_actions) > 0:
        msgs.append(
            "The following actions are invalid: {0}."
            "Possible valid actions are: {1}.".format(
                ", ".join(invalid_actions),
                ", ".join(POSSIBLE_ACTIONS)
            )
        )

    missing_pulldata_args = get_missing_pulldata_args(args)
    if 'pulldata' in actions and len(missing_pulldata_args) > 0:
        msgs.append(
            "The following required arguments "
            "to use --pulldata are missing: {0}".format(
                ", ".join(missing_pulldata_args)
            )
        )

    invalid_pulldata_args = get_invalid_pulldata_args(args)
    if 'pulldata' in actions and len(invalid_pulldata_args) > 0:
        msgs.append(
            "The following required arguments "
            "are invalid with --pulldata: {0}".format(
                ", ".join(missing_pulldata_args)
            )
        )

    missing_getmostrecent_args = get_missing_getmostrecent_args(args)
    if 'getmostrecent' in actions and len(missing_getmostrecent_args) > 0:
        msgs.append(
            "The following required arguments "
            "to use --getmostrecent are missing: {0}".format(
                ", ".join(missing_getmostrecent_args)
            )
        )

    if 'pulldata' in actions and 'getmostrecent' in actions:
        msgs.append(
            "--pulldata and --getmostrecent should not be run "
            "in the same command."
        )

    source_db_conn_dict = load_config(args.config).SOURCE_DB
    query_status = get_query_status(actions, args, source_db_conn_dict)
    if 'pulldata' in actions or 'getmostrecent' in actions:
        if query_status['status'] == 'error':
            msgs.append(
                "Trying to run the query {0} "
                "against the database {1} threw an exception.".format(
                    query_status['query'], source_db_conn_dict['db']
                )
            )

        if query_status['status'] == 'empty':
            msgs.append(
                "Trying to run the query {0} "
                "against the database {1} returned no results.".format(
                    query_status['query'], source_db_conn_dict['db']
                )
            )

    if args.restrictionstring and args.restrictionstring not in args.table:
        msgs.append(
            "The table {0} does not contain the string {1}.".format(
                args.table, args.restrictionstring
            )
        )

    valid_message = ["The arguments passed in are valid."]

    return {
        'state': 'valid' if len(msgs) == 0 else 'invalid',
        'msgs': valid_message if len(msgs) == 0 else msgs
    }


# Processing the command and redirecting accordingly

def execute_action(action, args):
    source_db_conn_dict = load_config(args.config).SOURCE_DB
    target_db_conn_dict = load_config(args.config).TARGET_DB

    if action == 'createstructure':
        sql_query_helpers.drop_and_create(target_db_conn_dict)
        commands.create_structure(
            source_db_conn_dict, target_db_conn_dict, args.config
        )
    elif action == 'deletedata':
        commands.delete_data(source_db_conn_dict, target_db_conn_dict)
    elif action == 'pulldata':
        commands.pull_data(
            args.table, args.column, args.values,
            source_db_conn_dict, target_db_conn_dict,
            args.heavy, args.restrictionstring,
            args.includeonly, args.overwrite
        )
    elif action == 'getmostrecent':
        commands.get_most_recent(
            args.table, args.column, args.howmany, args.where,
            source_db_conn_dict, target_db_conn_dict,
            args.heavy, args.restrictionstring,
            args.includeonly, args.overwrite
        )
    elif action == 'actions':
        print """
            Actions: \n
            {0}
        """.format(POSSIBLE_ACTIONS)
    elif action == 'args':
        print """
            Arguments to pulldata: \n
            'table', 'column', 'values' \n
            Example: ./main.py pulldata --table=auth_user --column=id
            --values=1,2 \n
            \n
            Arguments to getmostrecent: \n
            'table', 'column', 'howmany', 'where' \n
            Example: ./main.py getmostrecent --table=auth_user --column=id
            --howmany=10
            \n
            Extra arguments: \n
            'config', 'heavy', 'overwrite', 'restrictionstring', includeonly'
        """
