#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging.config
from argparse import RawDescriptionHelpFormatter
import cli_helpers
import config_helpers


def main():
    parser = argparse.ArgumentParser(
        description="""
            Pulling data from and manipulating databases. \n
            Example 1: ./main.py createstructure \n
            Example 2: ./main.py pulldata --table=auth_user
                --column=username --values=andre.kuney@newsela.com \n
            Example 3: ./main.py createstructure,pulldata
                --table=articles_article --column=header_id --values=3325
                --heavy --overwrite --restrictionstring=articles
            Example 4: ./main.py getmostrecent --table articles_header
                --column id --howmany 10 --where
                    'date_published IS NOT NULL AND publication_ready = 1'\n
            Example 5: ./main.py createstructure,pulldata
                --table=articles_article --column=header_id --values=3325
                "--includeonly articles_article,articles_quizquestion""",
        formatter_class=RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'actions',
        help="""
            Which actions would you like to perform? (separate by commas
                without spaces).  "Possible actions: {0}. Required.
            """.format(", ".join(cli_helpers.POSSIBLE_ACTIONS))
    )

    parser.add_argument(
        '--table',
        action='store',
        help="Which table would you like some data from?"
    )

    parser.add_argument(
        '--column',
        action='store',
        help="Which column would you like your data from?"
    )

    parser.add_argument(
        '--values',
        action='store',
        help="Which values would you like for your data? \
        Separate by commas without spaces."
    )

    parser.add_argument(
        '--howmany',
        action='store',
        help="How many results would you like to retrieve?"
    )

    parser.add_argument(
        '--where',
        action='store',
        help="How would you like to filter your most recent resultset?"
    )

    parser.add_argument(
        '--config',
        action='store',
        help="Where is your configuration file located?"
    )

    parser.add_argument(
        '--heavy',
        action='store_true',
        help="""
            Will evaluate per-table WHERE clauses with OR instead of AND.
            Can be slow.
            """
    )

    parser.add_argument(
        '--overwrite',
        action='store_true',
        help="Overwrite data for relevant tables."
    )

    parser.add_argument(
        '--restrictionstring',
        default='',
        help="""
            Restricts the universe of tables to those containing a certain
            string, such as 'people' or 'wire'.
            """
    )

    parser.add_argument(
        '--includeonly',
        action="store",
        help="Include only specific tables in the graph traversal."
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help="Execute with verbose output."
    )

    args = parser.parse_args()
    log_level = "INFO" if not args.debug else "DEBUG"
    logging.config.dictConfig(config_helpers.get_logging_config(log_level))

    if args.values is not None:
        args.values = cli_helpers.process_values(args.values)

    actions = args.actions.split(",")
    validity_info = cli_helpers.validity_info(args, actions)

    if validity_info['state'] == 'invalid':
        raise Exception("\n".join(validity_info['msgs']))
    else:
        print validity_info['msgs'][0]

    print "Running the following actions, in order: {0}.\n".format(
        ", ".join(actions)
    )

    for action in actions:
        print "Running the action '{0}'.\n".format(action)
        cli_helpers.execute_action(action, args)
