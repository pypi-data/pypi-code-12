#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
from .config import config
INDENT = config['INDENT']

from kivish.utils import error


def is_rule_root(line):
    return line[0] == '<'


def get_node_label(line):
    if '@' in line.split(':')[0]:
        return line.split('@')[1].split('>')[0]
    return line.split(':')[0].split()[0].lstrip()


def add_to_tree(node, created_nodes):
    if not created_nodes:
        created_nodes.append(node)
    else:
        add_to_parent(node, created_nodes)


def add_to_parent(new_node, created_nodes):
    '''
    Add the new node as a child of a previously created
    node, which has smaller indentation by one level.
    '''
    for node in reversed(created_nodes):
        if indentation_matches(node, new_node):
            result = is_duplicated_attribute_node(node, new_node)
            if result:
                merge_nodes(result, new_node)
            else:
                node.add_child(new_node)
                created_nodes.append(new_node)
            return

    msg = 'no parent for node "{%s}"' % new_node.label
    error.report(msg, new_node.num_line)


def indentation_matches(node, new_node):
    return node.indent == new_node.indent - INDENT


def is_duplicated_attribute_node(parent, node):
    if node.label[0] == '*':
        for child in parent.children:
            if child.label == node.label:
                return child
    return False


def merge_nodes(parent, new_node):
    if 'class' in new_node.label:
        parent.value += ' ' + new_node.value
    elif 'style' in new_node.label:
        parent.value += '; ' + new_node.value


def bump_indent(node, extra_indent):
    '''
    Used to bump indent of rule nodes to match indent of nodes,
    which use them.
    '''
    node.indent += extra_indent
    for child in node.children:
        bump_indent(child, extra_indent)
