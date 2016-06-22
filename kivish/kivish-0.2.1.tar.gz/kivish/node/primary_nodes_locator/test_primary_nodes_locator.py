#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
from .main import PrimaryNodesLocator


def test_locate_single_root_line():
    code = PrimaryNodesLocator('root').locate()

    num_line, line = next(code['root'])
    assert num_line == 1
    assert line == 'root'


def test_deny_bad_indent():
    code = '''
root:
 node'''
    code = PrimaryNodesLocator(code).locate()
    try:
        next(code['root'])
        next(code['root'])
        raise Exception('accepted bad indent')
    except SyntaxError:
        pass


def test_deny_multiroot():
    code = '''
node
node'''
    try:
        PrimaryNodesLocator(code).locate()
        raise Exception('accepted multiroot')
    except SyntaxError:
        pass


def test_multiline():
    code = '''
root: |
    hello
    world
'''
    code = PrimaryNodesLocator(code).locate()

    for num_line, line in code['root']:
        if num_line == 2:
            assert line == 'root: hello\nworld'
        elif num_line < 2 or num_line > 2:
            error(num_line, line)


def error(num_line, line):
    raise AssertionError('{}:{}'.format(num_line, line))


def test_locate_multiline_root_and_rules():
    code = '''
root:
    node1
    node2
<rule1@x>:
    node3
<rule2@x>:
    node4:
        node5
'''
    code = PrimaryNodesLocator(code).locate()
    check_root(code)
    check_first_rule(code)
    check_second_rule(code)


def check_root(code):
    for num_line, line in code['root']:
        if num_line == 2:
            assert line == 'root:'
        elif num_line == 3:
            assert line == '    node1'
        elif num_line == 4:
            assert line == '    node2'
        elif num_line < 2 or num_line > 4:
            error(num_line, line)


def check_first_rule(code):
    for num_line, line in code['rules']['rule1']:
        if num_line == 5:
            assert line == '<rule1@x>:'
        elif num_line == 6:
            assert line == '    node3'
        elif num_line < 5 or num_line > 6:
            error(num_line, line)


def check_second_rule(code):
    for num_line, line in code['rules']['rule2']:
        if num_line == 7:
            assert line == '<rule2@x>:'
        elif num_line == 8:
            assert line == '    node4:'
        elif num_line == 9:
            assert line == '        node5'
        elif num_line < 7 or num_line > 9:
            error(num_line, line)


def test_ignore_comment():
    code = '''
node
    #comment_1
# comment_2
 #comment_3'''
    code = PrimaryNodesLocator(code).locate()

    i = 0
    for a, b in code['root']:
        i += 1
    assert i == 1


def test_raw_text():
    code = PrimaryNodesLocator('## raw text').locate()
    num_line, line = code['raw'][0]
    assert num_line == 1
    assert line == 'raw text'
