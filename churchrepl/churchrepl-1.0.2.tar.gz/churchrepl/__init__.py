"""
ChurchRepl is a lambda calculus REPL built for study of church's theses
"""

from __future__ import print_function
import argparse
from builtins import input  # pylint: disable=redefined-builtin
from churchrepl.repl import parse, lex


def _load_program(program, args, show_defs=False):
    """
    Loads a program string and runs it with args given.
    :param program: Program to run
    :param args: arguments to apply
    :return: N/A
    """
    ast, defs = parse(program)
    if ast is not None:

        curr = None
        try:
            lexes = lex(ast, defs)
            if show_defs:
                for j in defs:
                    print('Alias defined for ' + j[0])
            for j in lexes:
                curr = j
                # _TODO: Remove eval. Possibly replace with closures
                _place(str(eval(str(curr))  # pylint: disable=eval-used
                           (lambda x: x + 1)(0)),
                       str(curr), args)

        # _TODO: Make error catching more specific.
        except Exception as err:  # pylint: disable=broad-except
            _place(str('!!!') + str(err), str(curr), args)


def _place(val, verbose, args):
    """
    Print wrapper to handle verbose statements
    :param val: value to print
    :param verbose: optional verbose value to print
    :return: None
    """
    if args.verbose:
        val += " --> " + verbose
    print(val)


def set_args(args):
    """
    Creates the argset from an argumentParser
    :param args: the list of arg strings to parse
    :return: an argument object containing the arg vals
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-f", "--file", nargs="+", type=str)
    return parser.parse_args(args)


def repl_eval(prompt, args):
    """
    Runs a Read Eval Print Loop.
    ^D exits gracefully from the loop.
    files may be loaded into the repl
    verbosity may be included
    :param prompt: the command line prompt to print
    :param args: an args object, typically from set_args(args)
    :return: N/A
    """
    if args.file is not None and len(args.file) is not 0:
        program = '\n'.join([open(filename).read()
                             for filename in args.file])
        _load_program(program, args, True)

    try:
        while True:
            _load_program(input(prompt), args)
    except EOFError:
        pass
