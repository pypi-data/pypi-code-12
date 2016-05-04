from __future__ import print_function
import click
import shlex
import sys

from globus_sdk import TransferData

from globus_cli.helpers import (
    CaseInsensitiveChoice, common_options, outformat_is_json,
    print_json_response)
from globus_cli.services.transfer.helpers import get_client
from globus_cli.services.transfer.activation import autoactivate


@click.command('async-transfer', short_help='Submit a Transfer Task',
               help=("""\
    Copy a file or directory from one Endpoint to another as an asynchronous
    task.

    \b
    Single-Item Mode vs. Batch Mode
    ===

    Has two modes of operation: single-item, and batchmode.

    ---

    Single-item has behavior similar to `cp` and `cp -r`, across endpoints of
    course.

    It is the behavior you get if you use `--source-path` and `--dest-path`.

    ---

    Batchmode is the way in which `async-transfer` can be used to
    submit a Task which transfers of multiple files or directories, and it is
    used to accept paths to transfer on stdin.

    Batchmode splits each line on spaces, and treats every line as a file or
    directory item to transfer.
    Splitting is done using Python shlex in POSIX mode:
    https://docs.python.org/2/library/shlex.html

    \b
    Lines are of the form
    [--recursive] SRCPATH DSTPATH

    Skips empty lines and allows comments beginning with "#".

    \b
    Example of --batch usage:
        $ cat dat
        # file 1, simple
        ~/dir1/sourcepath1 /abspath/destpath1
        # file 2, with spaces in dest path
        # paths without explicit ~ implicitly use ~
        dir2/sourcepath2   "path with spaces/dest2"
        # dir 1, requires --recursive option
        --recursive ~/srcdir1/ /somepath/destdir1
    \b
        $ cat dat | globus transfer async-transfer \\
            --batch --sync-level checksum \\
            --source-endpoint "..." --dest-endpoint "..."

    \b
    Sync Levels
    ===

    Sync Levels are ways in which the Task determines whether or not to
    actually move a file over the network.
    Choosing a higher sync level will reduce your network traffic when files in
    your transfer already exist on the destination, but will increase local IO
    and CPU load marginally at each end of the transfer.
    We recommend using high sync levels for tasks where you know or suspect
    that a non-negligible percentage of files already exist on the destination.

    EXISTS: Determine whether or not to transfer based on file existence.
    If the destination file is absent, do the transfer.

    MTIME: Determine whether or not to transfer based on modification times.
    If source has a newer modififed time than the destination, do the transfer.

    CHECKSUM: Determine whether or not to transfer based on checksums of file
    contents.
    If source and destination contents differ, as determined by a checksum of
    their contents, do the transfer.
    """))
@common_options
@click.option('--source-endpoint', required=True,
              help='ID of the Endpoint from which to transfer')
@click.option('--dest-endpoint', required=True,
              help='ID of the Endpoint to which to transfer')
@click.option('--source-path',
              help=('Path to the file/dir to move on source-endpoint in '
                    'single-item mode'))
@click.option('--dest-path',
              help=('Desired location of the file/dir on dest-endpoint in '
                    'single-item mode'))
@click.option('--recursive', is_flag=True,
              help=('source-path and dest-path are both directories, do a '
                    'recursive dir transfer. Ignored in batchmode'))
@click.option('--sync-level', default="mtime", show_default=True,
              type=CaseInsensitiveChoice(("exists", "mtime", "checksum")),
              help=('How will the Transfer Task determine whether or not to '
                    'actually transfer a file over the network?'))
@click.option('--batch', is_flag=True,
              help=('Accept a batch of source/dest path pairs on stdin (i.e. '
                    'run in batchmode). '
                    'Uses --source-endpoint and --dest-endpoint as passed on '
                    'the commandline.'))
def async_transfer_command(batch, sync_level, recursive, dest_path,
                           source_path, dest_endpoint, source_endpoint):
    """
    Executor for `globus transfer async-transfer`
    """
    print(str((batch, sync_level, recursive, dest_path,
               source_path, dest_endpoint, source_endpoint)))

    if (source_path is None or dest_path is None) and (not batch):
        raise click.UsageError(
            ('async-transfer requires either --source-path and --dest-path OR '
             '--batch'))
    if ((source_path is not None and batch) or
            (dest_path is not None and batch)):
        raise click.UsageError(
            ('async-transfer cannot take --batch in addition to --source-path '
             'or --dest-path'))

    client = get_client()
    transfer_data = TransferData(
        client, source_endpoint, dest_endpoint,
        label='globus-cli transfer', sync_level=sync_level)

    if batch is not None:
        # if input is interactive, print help to stderr
        if sys.stdin.isatty():
            print(('Enter transfers, line by line, as\n\n'
                   '    [--recursive] source-path dest-path\n\n'
                   'Lines are split with shlex in POSIX mode: '
                   'https://docs.python.org/library/shlex.html#parsing-rules\n'
                   'Terminate input with Ctrl+D or <EOF>\n'), file=sys.stderr)

        @click.command()
        @click.option('--recursive', is_flag=True)
        @click.argument('source_path')
        @click.argument('dest_path')
        def process_batch_line(dest_path, source_path, recursive):
            """
            Parse a line of batch input and turn it into a transfer submission
            item.
            """
            transfer_data.add_item(source_path, dest_path,
                                   recursive=recursive)

        # use readlines() rather than implicit file read line looping to force
        # python to properly capture EOF (otherwise, EOF acts as a flush and
        # things get weird)
        for line in sys.stdin.readlines():
            # get the argument vector:
            # do a shlex split to handle quoted paths with spaces in them
            # also lets us have comments with #
            argv = shlex.split(line, comments=True)
            if argv:
                try:
                    process_batch_line(args=argv)
                except SystemExit:
                    pass
    else:
        transfer_data.add_item(source_path, dest_path,
                               recursive=recursive)

    # autoactivate after parsing all args and putting things together
    autoactivate(client, source_endpoint, if_expires_in=60)
    autoactivate(client, dest_endpoint, if_expires_in=60)

    res = client.submit_transfer(transfer_data)

    if outformat_is_json():
        print_json_response(res)
    else:
        print(res['message'])
