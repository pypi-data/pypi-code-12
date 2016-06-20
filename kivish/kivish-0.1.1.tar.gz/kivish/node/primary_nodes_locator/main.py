#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
from .string_to_list import string_to_list


class PrimaryNodesLocator:

    def __init__(self, code: str):
        self.code = string_to_list(code)

    def locate(self) -> dict:
        '''
        Locate root and rules in the given code.

        Returns a dict with generators of code for each entity.
        Example structure:
        {
            'root': code_generator
            'rules': {
                'some_label': code_generator
                'another_label': code_generator
            }
        }

        Each generator iteration returns a tuple of code and original
        line number. Example structure: (1, 'root:')
        '''
        code = self.code

        root = None
        rules = {}

        for num_line, line in enumerate(code):

            if not line:
                continue
            elif is_root(line):
                root = traverse_node_tree(num_line, code)
            elif is_rule(line):
                label = get_rule_label(line)
                rules[label] = traverse_node_tree(num_line, code)

        return {'root': root, 'rules': rules}


def is_root(line):
    return line[0] not in ' #<'


def traverse_node_tree(start_line, code):
    code = code[start_line:]
    num_line = start_line + 1

    yield num_line, code[0]
    num_line += count_extra_node_height(code[0])

    for line in code[1:]:
        num_line += 1

        if not line:
            continue
        elif not is_root(line) and not is_rule(line):
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


def is_rule(line):
    return line[0] == '<'


def get_rule_label(string):
    return string.split('@')[0][1:]
