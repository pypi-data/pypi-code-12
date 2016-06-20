#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
from .main import Analyzer


def test_no_code():
    should_fail([], 'no code')


def should_fail(code, text):
    try:
        Analyzer(code).check()
    except SyntaxError:
        return
    raise SyntaxError(text)


def test_deny_no_root():
    should_fail('    line', 'no root')
    should_fail('<line@x>', 'no root')


def test_lines():
    code = '''
line
    '''
    Analyzer(code).check()


def test_accept_multiline():
    code = '''
line
    line
    line'''
    Analyzer(code).check()


def test_deny_multiple_root():
    code = '''
root
root'''
    should_fail(code, 'multiple root')


def test_deny_bad_indent():
    code = '''
line
   line'''
    should_fail(code, 'bad indent')


def test_accept_comment():
    code = '''
line
#'''
    Analyzer(code).check()


def test_accept_poorly_indented_comment():
    code = '''
line
 #'''
    Analyzer(code).check()


def test_accept_rule():
    code = '''
root
<rule@x>'''
    Analyzer(code).check()


def test_deny_indented_rule():
    code = '''
root
    <rule@x>'''
    should_fail(code, 'indented rule')
