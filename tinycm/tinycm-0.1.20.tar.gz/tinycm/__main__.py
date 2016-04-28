from tinycm import InvalidParameterError, UndefinedTypeError
from tinycm.log import setup_logger
from tinycm.parser import CMParser
from tinycm.graph import CMGraph
from socket import getfqdn
import os
import logging
import argparse
import colorama

from tinycm.state import get_state_diff
from tinycm.utils import http_dirname
import tinycm.backup


def main():
    parser = argparse.ArgumentParser(description="Tiny Configuration Manager")
    parser.add_argument('--apply', action='store_true', help="Apply configuration instead of verify")
    parser.add_argument('--hostname', help="Override hostname", default=getfqdn())
    parser.add_argument('--modulepath', help="Override the module path")
    parser.add_argument('--verbose', action='store_true', help="Show verbose messages")
    parser.add_argument('--debug', action='store_true', help="Show very verbose messages")
    parser.add_argument('configuration', help=".cm.yml file to verify or apply")
    args = parser.parse_args()

    colorama.init()

    level = logging.WARNING
    if args.verbose:
        level = logging.INFO
    if args.debug:
        level = logging.DEBUG

    logger = setup_logger('tinycm', level)

    if not args.modulepath:
        if args.configuration.startswith('http://') or args.configuration.startswith('https://'):
            args.modulepath = http_dirname(args.configuration)
        else:
            args.modulepath = os.path.dirname(args.configuration)

    logger.info('Starting TinyCM run')
    logger.info('Configuration: {}'.format(args.configuration))
    logger.info('Module path  : {}'.format(args.modulepath))
    logger.info('Hostname     : {}'.format(args.hostname))

    logger.debug('Starting parse stage')
    try:
        configuration = CMParser(args.configuration, args.hostname, module_path=args.modulepath)
    except UndefinedTypeError as e:
        logger.error("Undefined type {0}. You might need to install tinycm_{0}".format(e.missing_type))
        exit(1)

    logger.debug('Starting graph stage')
    try:
        graph = CMGraph(configuration)
    except InvalidParameterError as e:
        logger.error(str(e))
        exit(1)

    config_id = configuration.get_unique_id()
    logger.info('Unique ID for this configuration: {}'.format(config_id))
    tinycm.backup.current_id = config_id

    logger.debug('Starting sort stage')
    tasks = graph.get_sorted_jobs()

    state_diffs = get_state_diff(tasks)
    if args.apply:
        logger.debug('Starting apply stage')
        for state_diff in state_diffs:
            if not state_diff.correct:
                print("Applying {}".format(state_diff.identifier))
                state_diff.task.update_state(state_diff)
    else:
        logger.debug('Starting report stage')
        changelog = []
        for state_diff in state_diffs:
            if not state_diff.correct:
                changelog.append(state_diff)
                print(state_diff.identifier)
                state_diff.print_diff(indent=4)

        if len(changelog) == 0:
            logging.info('System state is correct, no changes required')
        else:
            print()
            print("Definitions that don't match the current system state:")
            for change in changelog:
                print("- {}: {}".format(change.identifier, ', '.join(change.changed_keys())))


if __name__ == '__main__':
    main()
