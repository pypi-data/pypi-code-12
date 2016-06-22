#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
from .main import Node


def test_no_colon():
    node = Node('Root-node-1', 0)
    assert node.label == 'Root-node-1'
    assert node.value is None


def test_colon_in_value():
    node = Node('root: hello:world:', 0)
    assert node.value == 'hello:world:'


def test_multiline_value():
    code = '''root: |
    long multiline
    text
    '''
    node = Node(code, 0)
    assert node.value == 'long multiline\ntext'


def test_multiline_escape():
    node = Node('root: \|hello\|', 0)
    assert node.value == '|hello\|'


def test_quoted_value():
    node = Node('root: "hello world"', 0)
    assert node.value == '"hello world"'
    node = Node("root: 'hello world'", 0)
    assert node.value == "'hello world'"


def test_attribute_node():
    node = Node('*node:', 0)
    assert node.label == '*node'


def test_deny_bad_label():
    try:
        Node('spaced node:', 0)
        Node('$node:', 0)
        Node('node_:', 0)
        raise Exception('bad name accepted')
    except SyntaxError:
        pass


def test_inline_attribute():
    node = Node('node #id-x .class-x .class-y', 0)
    expected_values = ('id-x', 'class-x class-y')

    assert False if len(node.children) == 0 else True
    for child in node.children:
        assert child.value in expected_values
