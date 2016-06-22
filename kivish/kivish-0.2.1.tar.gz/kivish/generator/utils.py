#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
from .config import config
INPUT_INDENT = config['INPUT_INDENT']
OUTPUT_INDENT = config['OUTPUT_INDENT']

from kivish.utils import error


def is_inline_node(node):
    return node.label[0] == '/'


def get_spaces(indent: int) -> str:
    if indent == 0:
        return ''
    else:
        num_tabs = int(indent / INPUT_INDENT)
        return ' ' * (OUTPUT_INDENT * num_tabs)


def is_attribute_node(node):
    if node.label[0] == '*':
        if node.children:
            msg = 'attribute node cannot have children'
            error.report(msg, node.num_line)
        return True


def get_attribute(child):
    if child.value:
        child.value = child.value.replace('\n', ' ')
        return ' ' + child.label[1:] + '="' + child.value + '"'
    else:
        return ' ' + child.label[1:]


def bump_attribute_nodes(children):
    '''Move attribute nodes to the top of children list.'''
    que = []

    for child in children:
        if child.label[0] == '*':
            yield child
        else:
            que.append(child)

    for child in que:
        yield child


def embed_attribute(child, string):
    string = string[:-2]
    if child.value:
        child.value = child.value.replace('\n', ' ')
        string += ' ' + child.label[1:] + '="' + child.value + '">\n'
    else:
        string += ' ' + child.label[1:] + '>\n'
    return string


def add_value(string, node, spaces):
    if node.value:

        parts = node.value.split('\n')
        for part in parts:
            string += spaces + ' ' * OUTPUT_INDENT + part + '\n'

    return string


def is_raw_text_node(node):
    return node.label == '--RAW'


def create_raw_text_node(node):
    return get_spaces(node.indent) + node.value + '\n'
