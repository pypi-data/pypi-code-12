#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
from kivish.utils import error, regex
from . import utils


class Generator:
    '''Creates an html file from a provided kvs root node.'''

    def __init__(self, root_node, raw_text=None):
        self._root_node = root_node
        self._raw_text = raw_text

    def generate(self):
        '''Creates an html string and returns it.'''
        html = self._node_to_string(self._root_node)

        while self._raw_text:
            html += self._pop_raw_text()

        return html

    def _node_to_string(self, node):
        string = ''

        while self._should_put_raw_text(node):
            string += self._pop_raw_text()

        if utils.is_inline_node(node):
            string += self._create_inline_node(node)
        else:
            string += self._create_normal_node(node)

        return string

    def _should_put_raw_text(self, node):
        try:
            return node.num_line > self._raw_text[0][0]
        except:
            return False

    def _pop_raw_text(self):
        string = utils.set_raw_text_indent(self._raw_text[0][1])
        del self._raw_text[0]
        return string + '\n'

    def _create_inline_node(self, node):
        spaces = utils.get_spaces(node.indent)
        label = regex.pattern_label.findall(node.label)[0]

        string = spaces + '<' + label

        for child in node.children:
            if utils.is_attribute_node(child):
                string += utils.get_attribute(child)
            else:
                msg = 'inline node can have only attribute children'
                error.report(msg, node.num_line)

        string += '/>\n'
        return string

    def _create_normal_node(self, node):
        spaces = utils.get_spaces(node.indent)
        label = regex.pattern_label.findall(node.label)[0]

        string = spaces + '<' + label + '>\n'

        for child in utils.bump_attribute_nodes(node.children):
            if utils.is_attribute_node(child):
                string = utils.embed_attribute(child, string)
            else:
                string += self._node_to_string(child)

        string = utils.add_value(string, node, spaces)

        string += spaces + '</' + label + '>\n'
        return string
