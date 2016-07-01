"""
Command line interface for vcdb.
"""
# Copyright (C) 2016 Thomas Aglassinger.
# Distributed under the GNU Lesser General Public License v3 or later.
import argparse
import logging
import os
import sys
import tempfile

from sqlalchemy.exc import SQLAlchemyError

import vcdb
import vcdb.common
import vcdb.subversion

_log = logging.getLogger('vcdb')


def vcdb_command(arguments=None):
    result = 1
    if arguments is None:
        arguments = sys.argv[1:]
    default_database = 'sqlite:///' + os.path.join(tempfile.gettempdir(), 'vcdb.db')
    parser = argparse.ArgumentParser(description='build SQL database from version control repository')
    parser.add_argument('repository', metavar='REPOSITORY', help='URI to repository')
    parser.add_argument(
        'database', metavar='DATABASE', nargs='?', default=default_database,
        help='URI for sqlalchemy database engine; default: %s' % default_database)
    parser.add_argument('--verbose', '-v', action='store_true', help='explain what is being done')
    parser.add_argument('--version', action='version', version='%(prog)s ' + vcdb.__version__)
    args = parser.parse_args(arguments)
    if args.verbose:
        _log.setLevel(logging.DEBUG)
    try:
        _log.info('connect to database %s', args.database)
        session = vcdb.common.vcdb_session(args.database)
        vcdb.subversion.update_repository(session, args.repository)
        _log.info('finished')
        result = 0
    except KeyboardInterrupt:
        _log.error('interrupted as requested by user')
    except OSError as error:
        _log.error(error)
    except SQLAlchemyError as error:
        _log.error('cannot access database: %s', error)
    except Exception as error:
        _log.exception(error)
    return result


def main():
    logging.basicConfig(level=logging.INFO)
    sys.exit(vcdb_command())


if __name__ == '__main__':
    main()
