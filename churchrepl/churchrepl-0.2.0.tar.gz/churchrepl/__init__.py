"""
ChurchRepl is a lambda calculus REPL built for study of church's theses
"""

from __future__ import print_function
import argparse
from builtins import input, str

from churchrepl.repl import parse, lex


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


# def _add_(body, func):
#     """
#     Underlying Church enumeration adder
#     :param body: the lambda body
#     :param func: the lambda itself
#     :return: given the value of the application on the body,
#     returns the value if it is a lambda itself, else the value + 1
#     """
#     val = func(body) if body is not None else -1
#     if hasattr(val, '__call__'):
#         return val
#     else:
#         return val + 1
#
#
# def _add(body, func):
#     """
#     Wrapper Church enumeration adder
#     :param body: the lambda body
#     :param func: the lambda itself
#     :return: __add(x, a) or 0
#     """
#     return _add_(body, func) if body is not None else 0
#
#
# def _to_int(lambda_expr):
#     """
#     Church enumeration converter
#     :param lambda_expr: the lambda to convert
#     :return: x's enumerated value.
#     """
#     return lambda_expr + 1


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
        program = '\n'.join([open(filename).read() for filename in args.file])
        ast, defs = parse(program)
        if ast is not None:
            try:
                ast, defs = parse(program)
                lexes = lex(ast, defs)
                i = 0
                for i in defs:
                    _place(i, defs[i].evalstr(), args)
                for j in [eval(lexical.evalstr)(lambda x: x+1)(0)
                          for lexical in lexes]:
                    _place(str(j), str(lexes[i].evalstr()), args)
                    i += 1
            except Exception as err:
                _place('!!!', str(err), args)

    try:
        while True:
            program = input(prompt)
            try:
                ast, defs = parse(program)
                lexes = lex(ast, defs)
                i = 0
                for j in [eval(lexical.evalstr)(lambda x: x+1)(0)
                          for lexical in lexes]:
                    _place(str(j), str(lexes[i].evalstr()), args)
                    i += 1
            except Exception as err:
                _place('!!!', str(err), args)
    except EOFError:
        pass
