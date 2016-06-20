#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
INDENT = 2

from kivish.utils import error, regex


class Generator:
    '''Creates an html file from a provided kvs root node.'''

    def __init__(self, root_node):
        self._root_node = root_node

    def generate(self):
        '''Creates an html string and returns it.'''
        html = node_to_string(self._root_node)
        return html


def node_to_string(node):
    if is_inline_node(node):
        return create_inline_node(node)
    else:
        return create_normal_node(node)


def get_spaces(indent):
    if indent == 0:
        return ''
    else:
        return ' ' * int(indent / 2)


def is_inline_node(node):
    return node.label[0] == '/'


def create_inline_node(node):
    spaces = get_spaces(node.indent)
    label = regex.pattern_label.findall(node.label)[0]

    string = spaces + '<' + label

    for child in node.children:
        if is_attribute_node(child):
            string += get_attribute(child)
        else:
            msg = 'inline node can have only attribute children'
            error.report(msg, node.num_line)

    string += '/>\n'
    return string


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


def create_normal_node(node):
    spaces = get_spaces(node.indent)
    label = regex.pattern_label.findall(node.label)[0]

    string = spaces + '<' + label + '>\n'

    for child in bump_attribute_nodes(node.children):
        if is_attribute_node(child):
            string = embed_attribute(child, string)
        else:
            string += node_to_string(child)

    string = add_value(string, node, spaces)

    string += spaces + '</' + label + '>\n'
    return string


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
            string += spaces + ' ' * INDENT + part + '\n'

    return string
