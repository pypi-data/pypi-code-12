#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
from .config import config
INPUT_INDENT = config['INPUT_INDENT']
OUTPUT_INDENT = config['OUTPUT_INDENT']

from kivish.utils import error, LineInfo


def set_raw_text_indent(string):
    indent = LineInfo(string).indent
    num_tabs = int(indent / INPUT_INDENT)
    return ' ' * (OUTPUT_INDENT * num_tabs) + string.lstrip()


def is_inline_node(node):
    return node.label[0] == '/'


def get_spaces(indent):
    if indent == 0:
        return ''
    else:
        return ' ' * int(indent / 2)


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
