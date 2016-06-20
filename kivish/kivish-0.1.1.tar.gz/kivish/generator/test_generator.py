#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
from .main import Generator
from ..node import Node
from ..scanner import Scanner
from pytest import fixture


@fixture
def simple_root():
    root = Node('html', 0)
    head = Node('    head', 1)
    body = Node('    body: hello world', 2)
    root.add_child(head)
    root.add_child(body)
    return root


def test_generate_simple_size(simple_root):
    html = Generator(simple_root).generate()

    expected = [
        '<html>',
        '  <head>',
        '  </head>',
        '  <body>',
        '    hello world',
        '  </body>',
        '</html>'
    ]
    assert_sequence(html, expected)


def assert_sequence(sequence, expected_sequence):
    sequence = sequence.split('\n')
    for i in range(len(expected_sequence)):
        assert sequence[i] == expected_sequence[i]


def test_attributes():
    node = Node('node #1 .x', 0)
    attr = Node('    *style: color: red', 0)
    node.add_child(attr)
    html = Generator(node).generate()

    expected = [
        '<node class="x" id="1" style="color: red">',
        '</node>'
    ]
    assert_sequence(html, expected)


def test_inline_node():
    node = Node('/img', 0)
    src = Node('*src: link', 0)
    node.add_child(src)
    expected = '<img src="link"/>\n'
    html = Generator(node).generate()
    assert html == expected


def test_nested_rules():
    code = '''
html
    body
        rule .a

<rule@x>
    *class: b
    /img:
        *src: link_b

<x@div>
    *class: c
    /img:
        *src: link_c
    '''
    node = Scanner(code).scan()
    html = Generator(node).generate()

    expected = [
        '<html>',
        '  <body>',
        '    <div class="a c b">',
        '      <img src="link_c"/>',
        '      <img src="link_b"/>',
        '    </div>',
        '  </body>',
        '</html>',
    ]
    assert_sequence(html, expected)


def test_deny_attribute_with_children():
    code = '''
node:
    *class:
        x:
'''
    node = Scanner(code).scan()
    try:
        Generator(node).generate()
        raise Exception('accepted bad node')
    except SyntaxError:
        pass


def test_deny_bad_inline_node():
    code = '''
/node:
    x:
'''
    node = Scanner(code).scan()
    try:
        Generator(node).generate()
        raise Exception('accepted bad inline node')
    except SyntaxError:
        pass


def test_flat_attributes():
    code = '''
node:
    *style: |
        a;
        b
'''
    node = Scanner(code).scan()
    html = Generator(node).generate()
    assert 'style="a; b"' in html


def test_attribute_without_value():
    code = '''
node:
    *flex
'''
    node = Scanner(code).scan()
    html = Generator(node).generate()
    assert '<node flex>' in html


def test_attribute_without_value_inline():
    code = '''
/node:
    *flex
'''
    node = Scanner(code).scan()
    html = Generator(node).generate()
    assert '<node flex/>\n' == html


def test_multiline_indentation():
    code = '''
node: |
    hello
    world
'''
    node = Scanner(code).scan()
    html = Generator(node).generate()
    expected = [
        '<node>',
        '  hello',
        '  world',
        '</node>'
    ]
    assert_sequence(html, expected)
