#!venv/bin/python
"""
The underlying semantic, syntax and lexical analysis module
"""

from __future__ import print_function
from functools import partial
from grako.buffering import Buffer
from .parser import LambdaParser, LambdaSemantics
from .lexer import replace_alias
from .redux import alpha  # , beta, eta
parser = LambdaParser()


def parse(program):
    """
    Parse a string into a list of lexical objects
    :param program: string to parse
    :return: Lexcial object lists
    """
    return parser.parse(Buffer(program, nameguard=False), 'program',
                        semantics=LambdaSemantics())


def redux_(func, ast):
    """
    Reduction partial wrapper
    :param func: function to wrap
    :param ast: the ast to be passed to the function
    :return: a reduced (or converted) ast
    """
    ret = []
    for line in ast:
        line, rep = func(line)
        while rep:
            line, rep = func(line)
        ret.append(line)
    return ret

redux_alpha = partial(redux_, alpha)
# redux_beta = partial(redux_, beta)
# redux_eta = partial(redux_, eta)


def lex(ast, definitions):
    """
    Lexical object emplacement of aliases
    :param ast: the lexical objects to replace aliases
    :param definitions: valid aliases
    :return: The formatted lexical object list
    """
    ret = []
    for line in ast:
        line, rep = replace_alias(line, definitions)
        while rep:
            line, rep = replace_alias(line, definitions)
        ret.append(line)

    # return redux_eta(redux_beta(redux_alpha(ret)))
    return redux_alpha(ret)
