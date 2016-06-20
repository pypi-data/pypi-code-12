#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
from .config import config
INDENT = config['INDENT']

from kivish.utils import error


class Analyzer:

    def __init__(self, code):
        self.code = string_to_list(code)

    def check(self):
        '''
        Check for bad indentation and number of roots.

        Raises SyntaxError.
        '''
        roots = 0

        for i, line in enumerate(self.code, 1):

            if not line.strip():
                continue

            if check_bad_indent(line) is True:
                error.report('bad indent', i)

            roots += check_root_node(line)
            if roots > 1:
                error.report('second root', i)

        if roots == 0:
            error.report('no root node')


def string_to_list(string):
    if isinstance(string, list):
        return string

    result = []
    for line in string.split('\n'):
        result.append(line)
    return result


def check_root_node(line):
    if is_significant_line(line) and not is_rule_declaration(line):
        return 1
    return 0


def is_significant_line(line):
    return line[0] != ' ' and line[0] != '#'


def is_rule_declaration(line):
    return line.lstrip()[0] == '<'


def check_bad_indent(line):
    if is_indentation_neutral_line(line):
        return False

    line_indent = get_line_indent(line)

    if line_indent % INDENT != 0 and not is_rule_declaration(line):
        return True

    if is_rule_declaration(line) and line_indent != 0:
        return True


def is_indentation_neutral_line(line):
    return line[0] != ' ' or line.lstrip()[0] == '#'


def get_line_indent(line):
    line = line.rstrip()
    return len(line) - len(line.strip())
