#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
from .line_info import LineInfo


def test_indent():
    assert LineInfo('node: ').indent == 0
    assert LineInfo('    node: ').indent == 4


def test_value():
    assert LineInfo('node: val').value == 'val'
    line = 'node: my hobbies: ski, etc.'
    assert LineInfo(line).value == 'my hobbies: ski, etc.'
    line = 'node: my hobbies: ski, etc.'
    assert LineInfo(line).value == 'my hobbies: ski, etc.'
    assert LineInfo('node: \|hi|').value == '|hi|'
    lines = '''node: |
    a
    b'''
    assert LineInfo(lines).value == 'a\nb'


def test_label():
    assert LineInfo('node').label == 'node'
    assert LineInfo('    node:').label == 'node'
    assert LineInfo('    node .x:').label == 'node'


def test_inline_attrs():
    line = 'node #id-x .class-a .class-b:'
    expected = {
        'classes': ['class-a', 'class-b'],
        'id': 'id-x'
    }
    result = LineInfo(line).inline_attrs
    assert expected == result
