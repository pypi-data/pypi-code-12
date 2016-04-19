import sys
import os
import argparse
from traceback import format_exc

from dfp_sync.cli import (
    cmd_service, 
    cmd_ls_service,
    cmd_cloud_auth
)


def setup(parser):
    """
    Install all subcommands.
    """

    subparser = parser.add_subparsers(help='Commands', dest='cmd')

    MODULES = [
        cmd_service,
        cmd_cloud_auth,
        cmd_ls_service
    ]
    subcommands = {}
    for module in MODULES:
        cmd_name, run_func = module.setup(subparser)
        subcommands[cmd_name] = run_func
    return subcommands


def run():
    """
    The main cli function.
    """

    # create an argparse instance
    parser = argparse.ArgumentParser(prog='dfp-sync')
    parser.add_argument('--aws-key', default=os.getenv('AWS_ACCESS_KEY_ID'))
    parser.add_argument('--aws-secret', default=os.getenv('AWS_SECRET_ACCESS_KEY'))
    
    # add the subparser "container"
    subcommands = setup(parser)

    # parse the arguments + options
    opts = parser.parse_args()

    # check for proper subcommands
    if opts.cmd not in subcommands:
        print("Error: No such subcommand '{}'".format(opts.cmd))

    try:
        subcommands[opts.cmd](opts)

    except KeyboardInterrupt as e:
        print('Interrupted by user.')
        sys.exit(2)  # interrupt

    except Exception as e:
        print(format_exc())
        sys.exit(1)
