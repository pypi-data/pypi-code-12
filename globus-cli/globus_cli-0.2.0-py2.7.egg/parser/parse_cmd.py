from __future__ import print_function

from globus_cli.excepthook import set_excepthook
from globus_cli.parser.command_tree import build_command_tree


def _load_args():
    """
    Load commandline arguments, and do any necessary post-processing.
    """
    parser = build_command_tree()
    args = parser.parse_args()

    if args.func.cli_argument_validator:
        args.func.cli_argument_validator(args, parser)

    return args


def run_command():
    """
    Whatever arguments were loaded, they set a function to be invoked on the
    arguments themselves -- somewhat circular, but a nifty way of passing the
    args to a function that this module doesn't even know about
    """
    set_excepthook()
    args = _load_args()
    args.func(args)
