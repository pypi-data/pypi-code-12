#!venv/bin/python
"""
The underlying semantic, syntax and lexical analysis module
"""

from __future__ import print_function
from grako.buffering import Buffer
from .parser import LambdaParser, LambdaSemantics
parser = LambdaParser()


def parse(program):
    """
    Parse a string into a list of lexical objects
    :param program: string to parse
    :return: Lexcial object lists
    """
    return parser.parse(Buffer(program, nameguard=False), 'program',
                        semantics=LambdaSemantics())


def lex(ast, definitions):
    """
    Lexical object emplacement of aliases
    :param ast: the lexical objects to replace aliases
    :param definitions: valid aliases
    :return: The formatted lexical object list
    """
    ret = []
    for line in ast:
        line, rep = line.replace_alias(definitions)
        while rep:
            line, rep = line.replace_alias(definitions)
        ret.append(line)

    # return redux_eta(redux_beta(redux_alpha(ret)))
    return [line.alpha for line in ret]
