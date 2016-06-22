#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
from .config import config
INDENT = config['INDENT']

from .string_to_list import string_to_list
from kivish.utils import error, LineInfo


class PrimaryNodesLocator:

    def __init__(self, code: str):
        self.code = string_to_list(code)

    def locate(self) -> dict:
        '''
        Locate root, rules and raw text in the given code.

        Returns a dict with generators of code for each entity.
        Example structure:
        {
            'root': code_generator
            'rules': {
                'some_label': code_generator
                'another_label': code_generator
            },
            'raw': list of tuples (num_line, text)
        }

        Each generator iteration returns a tuple of code and original
        line number. Example structure: (1, 'root:')
        '''
        code = self.code

        root = None
        rules = {}
        raw = []

        for num_line, line in enumerate(code):

            if not line:
                continue
            elif is_raw_text(line):
                raw.append((num_line + 1, clean_raw_text(line)))
            elif is_root(line):
                if not root:
                    root = traverse_node_tree(num_line, code)
                else:
                    error.report('found second root', num_line + 1)
            elif is_rule(line):
                label = get_rule_label(line)
                rules[label] = traverse_node_tree(num_line, code)

        return {'root': root, 'rules': rules, 'raw': raw}


def is_raw_text(line):
    return line.lstrip().startswith('##')


def clean_raw_text(line):
    parts = line.split('##', 1)
    if parts[1][0] == ' ':
        return parts[0] + parts[1][1:]
    return parts[0] + parts[1]


def is_root(line):
    return line[0] not in ' #<'


def traverse_node_tree(start_line, code):
    code = code[start_line:]
    num_line = start_line + 1

    check_indent(code[0], num_line)

    yield num_line, code[0]
    num_line += count_extra_node_height(code[0])

    for line in code[1:]:
        num_line += 1

        if not line:
            continue
        elif is_comment(line):
            continue
        elif not is_root(line) and not is_rule(line):
            check_indent(line, num_line)
            yield num_line, line.rstrip()
            num_line += count_extra_node_height(line)
        else:
            break


def count_extra_node_height(code):
    '''Multiline nodes take more than a single line of code.'''
    height = code.count('\n')
    if height > 0:
        height += 1
    return height


def is_comment(line):
    stripped = line.lstrip()
    if not stripped:
        return False
    if stripped[0] == '#':
        return True
    return False


def check_indent(line, num_line):
    if LineInfo(line).indent % INDENT != 0:
        error.report('bad indent', num_line)


def is_rule(line):
    return line[0] == '<'


def get_rule_label(string):
    return string.split('@')[0][1:]
