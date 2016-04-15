from __future__ import print_function

import argparse
import shlex
import sys

from globus_cli.helpers import (
    outformat_is_json, cliargs, CLIArg, print_json_response)
from globus_cli.services.transfer.helpers import get_client
from globus_cli.services.transfer.activation import autoactivate


def add_submission_id(client, datadoc):
    submission_id = client.get_submission_id()['value']
    datadoc['submission_id'] = submission_id


def _validate_transfer_args(args, parser):
    if (args.source_path is None or args.dest_path is None) and (
            args.batch is None):
        parser.error('async-transfer requires either --source-path and '
                     '--dest-path OR --batch')
    if ((args.source_path is not None and args.batch is not None) or
            (args.dest_path is not None and args.batch is not None)):
        parser.error('async-transfer cannot take --batch in addition to '
                     '--source-path or --dest-path')


@cliargs(('Copy a file or directory from one endpoint '
          'to another as an asynchronous task'),
         CLIArg('source-endpoint', required=True,
                help='ID of the endpoint from which to transfer'),
         CLIArg('dest-endpoint', required=True,
                help='ID of the endpoint to which to transfer'),
         CLIArg('source-path',
                help='Path to the file/dir to move on source-endpoint'),
         CLIArg('dest-path',
                help='Desired location of the file/dir on dest-endpoint'),
         CLIArg('recursive', default=False, action='store_true',
                help=('source-path and dest-path are both directories, do a '
                      'recursive dir transfer. Ignored when using --batch')),
         CLIArg('sync-level', default="mtime", type=str.lower,
                choices=("exists", "mtime", "checksum"),
                help=('How will the transfer task determine whether or not to '
                      'actually transfer a file?\n'
                      'EXISTS: if the dest file is absent\n'
                      'MTIME: if source is newer (modififed time) than dest\n'
                      'CHECKSUM: if source and dest contents differ')),
         CLIArg('batch', default=False, action='store_true',
                help=('Accept a batch of source/dest path pairs on stdin. '
                      'Skips empty lines and allows '
                      'comments beginning with "#"')),
         arg_validator=_validate_transfer_args)
def submit_transfer(args):
    """
    Executor for `globus transfer async-transfer`
    """
    client = get_client()

    if args.batch is not None:
        # if input is interactive, print help to stderr
        if sys.stdin.isatty():
            print(('Enter transfers, line by line, as\n\n'
                   '    [--recursive] source-path dest-path\n\n'
                   'Lines are split with shlex in POSIX mode: '
                   'https://docs.python.org/library/shlex.html#parsing-rules\n'
                   'Terminate input with Ctrl+D or <EOF>\n'), file=sys.stderr)

        def parse_batch_line(line):
            """
            Parse a line of batch input and turn it into a transfer submission
            item.
            """
            # define a parser to handle the batch line
            parser = argparse.ArgumentParser(
                description='async-transfer batch parser')
            parser.add_argument('--recursive', default=False,
                                action='store_true')
            parser.add_argument('source')
            parser.add_argument('dest')

            # get the argument vector:
            # do a shlex split to handle quoted paths with spaces in them
            # also lets us have comments with #
            argv = shlex.split(line, comments=True)
            if not argv:
                return None

            args = parser.parse_args(argv)

            return client.make_submit_transfer_item(
                args.source, args.dest, recursive=args.recursive)

        # nested comprehensions to filter the results to remove None
        # use readlines() rather than implicit file read line looping to force
        # python to properly capture EOF (otherwise, EOF acts as a flush and
        # things get weird)
        transfer_items = [item for item in (parse_batch_line(line)
                                            for line in sys.stdin.readlines())
                          if item is not None]
    else:
        transfer_items = [client.make_submit_transfer_item(
            args.source_path, args.dest_path, recursive=args.recursive)]

    datadoc = client.make_submit_transfer_data(
        args.source_endpoint, args.dest_endpoint, transfer_items,
        label='globus-cli transfer', sync_level=args.sync_level)

    # autoactivate after parsing all args and putting things together
    autoactivate(client, args.source_endpoint, if_expires_in=60)
    autoactivate(client, args.dest_endpoint, if_expires_in=60)

    res = client.submit_transfer(datadoc)

    if outformat_is_json(args):
        print_json_response(res)
    else:
        print(res['message'])


@cliargs(('Delete a file or directory from one endpoint '
          'as an asynchronous task'),
         CLIArg('endpoint-id', required=True,
                help='ID of the endpoint from which to delete file(s)'),
         CLIArg('path', required=True, help='Path to the file/dir to delete'),
         CLIArg('recursive', default=False, action='store_true',
                help='Recursively delete dirs'),
         CLIArg('ignore-missing', default=False, action='store_true',
                help='Don\'t throw errors if the file or dir is absent'))
def submit_delete(args):
    """
    Executor for `globus transfer submit-delete`
    """
    client = get_client()
    autoactivate(client, args.endpoint_id, if_expires_in=60)

    datadoc = {
        'DATA_TYPE': 'delete',
        'label': 'globus-cli delete',
        'endpoint': args.endpoint_id,
        'recursive': args.recursive,
        'ignore_missing': args.ignore_missing,
        'DATA': [
            {
                'DATA_TYPE': 'delete_item',
                'path': args.path
            }
        ]
    }
    add_submission_id(client, datadoc)
    res = client.submit_delete(datadoc)

    if outformat_is_json(args):
        print_json_response(res)
    else:
        print(res['message'])
