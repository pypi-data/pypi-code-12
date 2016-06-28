"""
This module contains the application's argument parser.
"""
import argparse


HELP_LOG_LVL = 'Secify the log level: 1 = ALL, 10 = DEBUG, 20 = INFO, ' \
    '30 = WARNINGS, 40 = ERRORS'


def parse_args():
    """
    Configures argument parser and parse args.
    :return: args namespace
    """
    parser = argparse.ArgumentParser(
        description='Experimental IDE built with Python and Qt')
    parser.add_argument('paths', type=str, nargs='*',
                        help='Optional list of files/folders to open')
    parser.add_argument('--log', dest='log', action='store_true',
                        help='Display the content of the last log file.')
    parser.add_argument('--log-level', action="store", dest="log_level",
                        type=int, help=HELP_LOG_LVL)
    parser.add_argument('--verbose', dest='verbose', action='store_true',
                        help='Same as --log-level 10, ignored if --log-level '
                        'is used.')
    parser.add_argument('--version', dest='version', action='store_true',
                        help='Display the version of the application and its '
                        'main components')
    parser.add_argument('--style', dest='style',
                        help='Select the qt style')
    parser.add_argument('--autoquit', dest='autoquit', action='store_true',
                        help='Automatically quit the app after a small delay,'
                             'for testing purposes')
    parser.add_argument('--dev', dest='dev', action='store_true',
                        help='Enable developer mode (yellowish toolbars)')
    return parser.parse_args()
