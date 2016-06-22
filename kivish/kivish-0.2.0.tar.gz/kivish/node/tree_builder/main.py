#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
from .. import Node
from .helpers import (
    is_rule_root,
    get_node_label,
    add_to_tree,
    bump_indent
)
from kivish.utils import LineInfo, error
import copy


class TreeBuilder:
    '''
    Builds a node tree for the given code.
    The code must be a list of tuples, featuring num_lines and strings.
    '''

    def __init__(self, root_tree, rules):
        self._root_tree = root_tree
        self._rules = rules

        self._built_rules = {}
        self._previous_walk = {
            'indent': None,
            'inline_attrs': None,
            'value': None
        }
        self._value_stack = []
        self._attr_stack = []
        self._num_line = None

    def go(self):
        '''Returns root node of the code.'''
        root, x = self._traverse_node_tree(self._root_tree)
        return root

    def _traverse_node_tree(self, tree, previous_walk=None):
        self._previous_walk = previous_walk

        root = self._get_tree_root(tree)

        if previous_walk:
            bump_indent(root, previous_walk['indent'])

        return root, self._built_rules

    def _get_tree_root(self, tree):
        created_nodes = []

        for num_line, line in tree:
            self._num_line = num_line

            if not line:
                continue

            node = self._get_node(line, num_line)
            add_to_tree(node, created_nodes)

        return created_nodes[0]

    def _get_node(self, line, num_line):
        if self._node_label_among_rules(line):
            return self._get_or_create_rule(line)
        else:
            return self._create_node(line, num_line)

    def _node_label_among_rules(self, line):
        return get_node_label(line) in self._rules.keys()

    def _get_or_create_rule(self, line):
        info = LineInfo(line)
        current_walk = {
            'inline_attrs': info.inline_attrs,
            'indent': info.indent,
            'value': info.value
        }

        node_label = get_node_label(line)

        if self._rule_already_built(node_label):
            indent = current_walk['indent']
            value = current_walk['value']
            return self._use_existing_rule(node_label, value, indent)
        else:
            return self._create_rule(node_label, current_walk)

    def _use_existing_rule(self, label, value, indent):
        rule = copy.deepcopy(self._built_rules[label])
        rule.value = value
        rule.indent = indent
        return rule

    def _raw_root_rule_node(self, line):
        raw_node = get_node_label(line)

        self._validate_rule_declaration(line)

        if self._attr_stack:
            attrs = attrs_to_string(self._attr_stack)
            raw_node += ' ' + attrs
            self._attr_stack = []

        if self._value_stack:
            raw_node += ': ' + self._value_stack[0]
            self._value_stack = []

        return raw_node

    def _validate_rule_declaration(self, line):
        if len(line.split()) > 1:
            error.report('bad node declaration', self._num_line)

    def _create_node(self, line, num_line):
        if is_rule_root(line):
            raw_node = self._raw_root_rule_node(line)
            return Node(raw_node, num_line)
        else:
            return Node(line, num_line)

    def _rule_already_built(self, line):
        return line in self._built_rules.keys()

    def _create_rule(self, node_label, current_walk):

        if current_walk['value']:
            self._value_stack.append(current_walk['value'])
        if current_walk['inline_attrs']:
            self._attr_stack.append(current_walk['inline_attrs'])

        node, new_built_rules = self._traverse_node_tree(
            self._rules[node_label], current_walk)

        self._built_rules[node_label] = node
        for label, root in new_built_rules.items():
            self._built_rules[label] = root

        return node


def attrs_to_string(attrs_list):

    def get_attrs(attr_set):
        string = ''

        if attr_set['id']:
            string += '#' + attr_set['id']

        class_string = ''
        for class_ in attr_set['classes']:
            class_string += '.' + class_ + ' '
        string += class_string

        return string.rstrip()

    string = ''
    for attr_set in attrs_list:
        string += get_attrs(attr_set)
    return string
