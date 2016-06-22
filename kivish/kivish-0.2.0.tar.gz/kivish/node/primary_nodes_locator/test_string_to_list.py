#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
from .string_to_list import string_to_list


def test_single_multiline():
    code = '''
root: |
    selector {
        color: red
    }
'''
    code_list = string_to_list(code)
    assert code_list[1] == 'root: selector {\n    color: red\n}'


def test_many_nodes_and_multiline():
    code = '''
root:
    node1: |
        hello
        world
    node2
'''
    code_list = string_to_list(code)
    assert code_list[0] == ''
    assert code_list[1] == 'root:'
    assert code_list[2] == '    node1: hello\nworld'
    assert code_list[3] == '    node2'
    assert code_list[4] == ''
