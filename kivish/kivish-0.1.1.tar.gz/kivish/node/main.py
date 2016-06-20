#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
from .config import config
INDENT = config['INDENT']

from kivish.utils import LineInfo


class Node:
    '''
    A node which represents one or more lines of code, which has:

    - label (string)
    - value (string)
    - num_line (number; not unique for inline attribute nodes)
    - indent (number of spaces)
    - children (child nodes)

    Raises SyntaxError if its label contains forbidden characters.
    '''

    def __init__(self, code, num_line):
        self.label = None
        self.value = None
        self.indent = None
        self.num_line = None
        self.children = []

        self.__set_pools(code, num_line)

    def __set_pools(self, code, num_line):
        code = merge_lines(code)
        info = LineInfo(code)

        self.label = info.label
        self.value = info.value
        self.indent = info.indent
        self.num_line = num_line

        info = LineInfo(code)
        attrs = info.inline_attrs

        if has_inline_attrs(code, attrs):
            indent = info.indent

            for node in get_attr_nodes(attrs, indent, num_line):
                self.add_child(node)

    def add_child(self, node):
        if node.label == '*class':
            if self._already_has_class():
                self._class_node.value += ' ' + node.value
                return

        self.children.append(node)

    def _already_has_class(self):
        return '*class' in [c.label for c in self.children]

    @property
    def _class_node(self):
        for child in self.children:
            if child.label == '*class':
                return child


def merge_lines(code):
    if isinstance(code, str):
        return code
    elif isinstance(code, list):
        return '\n'.join(code)


def has_inline_attrs(code, attrs):
    first_char = code.lstrip()[0]
    if first_char != '*':
        return attrs['classes'] or attrs['id']


def get_attr_nodes(attrs, indent, num_line):
    raw_nodes = create_raw_attribute_nodes(attrs, indent)
    for raw_node in raw_nodes:
        yield Node(raw_node, num_line)


def create_raw_attribute_nodes(attributes, indent):
    classes = attributes['classes']
    id = attributes['id']
    spaces = ' ' * (indent + INDENT)

    list = []

    for class_ in classes:
        list.append('{}*class: {}'.format(spaces, class_))

    if id:
        list.append('{}*id: {}'.format(spaces, id))

    return list
