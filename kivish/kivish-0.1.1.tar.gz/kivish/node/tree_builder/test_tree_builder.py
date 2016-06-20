#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
from .main import TreeBuilder
from ..primary_nodes_locator import PrimaryNodesLocator


def test_node_without_value():
    code = 'root:'
    node = get_root_node(code)
    assert node.label == 'root'
    assert node.value is None
    assert node.children == []


def get_root_node(code):
    data = PrimaryNodesLocator(code).locate()
    root, rules = data['root'], data['rules']
    return TreeBuilder(root, rules).go()


def test_node_with_text_value():
    code = 'root: hello world'
    node = get_root_node(code)
    assert node.value == 'hello world'


def test_many_nodes():
    code = '''
root:
    node1: hello
    node2: world
        node3: !
    node4:
'''
    node = get_root_node(code)
    assert node.children[0].label == 'node1'
    assert node.children[0].value == 'hello'
    assert node.children[1].label == 'node2'
    assert node.children[1].value == 'world'
    assert node.children[1].children[0].label == 'node3'
    assert node.children[1].children[0].value == '!'
    assert node.children[2].label == 'node4'


def test_multiline_node():
    code = '''
root: |
    some
    text
    '''
    node = get_root_node(code)
    assert node.value == 'some\ntext'


def test_multiline_nested_gaps():
    code = '''
root:
    node1: |
        a
        b
    node2: |
        c
        d
    '''
    root = get_root_node(code)
    node1 = root.children[0]
    node2 = root.children[1]
    assert node1.num_line == 3
    assert node1.value == 'a\nb'
    assert node2.num_line == 6
    assert node2.value == 'c\nd'


def test_inline_attribute():
    code = '''
root .some-class
'''
    node = get_root_node(code)
    assert node.children[0].label == '*class'
    assert node.children[0].value == 'some-class'


def test_use_rule():
    code = '''
rule
<rule@div>
'''
    node = get_root_node(code)
    assert node.label == 'div'
    assert node.value is None
    assert node.children == []


def test_deny_bad_rule_declaration():
    code = '''rule
<rule@div>: text'''
    try:
        get_root_node(code)
        raise Exception('allowed bad rule declaration')
    except SyntaxError:
        pass

    code = '''rule
<rule@div .x>'''
    try:
        get_root_node(code)
        raise Exception('allowed bad rule declaration')
    except SyntaxError:
        pass


def test_rule_with_attributes():
    code = '''
rule .some-class
    *width: 1
<rule@div>
    '''
    node = get_root_node(code)
    assert node.children[0].label == '*class'
    assert node.children[0].value == 'some-class'
    assert node.children[1].label == '*width'
    assert node.children[1].value == '1'


def test_use_nested_rules():
    code = '''
d1
    a
    d2
        d3

<d1@div>
<d2@span>
<d3@h1>
'''
    node = get_root_node(code)
    assert node.label == 'div'
    a = node.children[0]
    assert a.label == 'a'
    d2 = node.children[1]
    assert d2.label == 'span'
    d3 = d2.children[0]
    assert d3.label == 'h1'


def test_nested_rule_with_attribute():
    code = '''
node
    nested

<nested@div>:
    *test: passed
'''
    node = get_root_node(code)
    assert node.children[0].children[0].value == 'passed'


def test_rule_inheritance():
    code = '''
rule1 .a: hello world
    *style: color: blue

<rule1@rule2>
    *class: b
    test1: val_1

<rule2@div>
    *class: c
    *style: color: red
    test2: val_2
    '''
    node = get_root_node(code)
    assert node.label == 'div'
    assert node.value == 'hello world'

    vals = ('val_1', 'val_2', 'a c b', 'color: red; color: blue')
    for val in vals:
        assert val in [child.value for child in node.children]


def test_rule_used_in_many_places():
    code = '''
root:
    TheRule: hello
    div:
        TheRule: world

<TheRule@span>
'''
    root = get_root_node(code)
    assert root.children[0].value == 'hello'
    assert root.children[1].children[0].value == 'world'
