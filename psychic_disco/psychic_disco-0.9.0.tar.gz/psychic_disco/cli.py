""" Provides a simple convention for defining cli arguments and subcommands """
import argparse
import inspect

parser = argparse.ArgumentParser(prog='psychic_disco')
subparsers = parser.add_subparsers(help='sub-command help')
args = None


def _apply_args_to_func(global_args, func):
    """ Unpacks the argparse Namespace object and applies its
    contents as normal arguments to the function func """
    global_args = vars(global_args)
    local_args = dict()
    for argument in inspect.getargspec(func).args:
        local_args[argument] = global_args[argument]
    return func(**local_args)


def subcommand(f):
    """ Define a subcommand for the psychic_disco function
    Expects functions to supply a list of their arguments
    Converts these to arg_parse arguments, and transforms
    the argparse Namespace object so that commands can be
    invoked as though they are normal functions (which they are)"""
    sp = subparsers.add_parser(f.__name__, help=f.__doc__)
    for argument in inspect.getargspec(f).args:
        sp.add_argument(argument)
    sp.set_defaults(func=lambda args: _apply_args_to_func(args, f))
    return f


def parse_args():
    """ Parse command line arguments and assign contents to
    `cli.args` variable"""
    global args
    args = parser.parse_args()
    return args


def argument(*args, **kwargs):
    """ Set up a new argument for the psychic_disco program.
    Follows same conventions as argparse's add_argument """
    parser.add_argument(*args, **kwargs)
