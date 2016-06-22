#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
from .scanner import Scanner
from .generator import Generator


def compile(target):
    if not target.endswith('.kvs'):
        return print('Expected a file with .kvs extension.')

    code = read_code(target)

    try:
        r = Scanner(code).scan()
        root, raw_text = r['root'], r['raw']
    except SyntaxError as e:
        return print(e)

    try:
        html = Generator(root, raw_text).generate()
    except SyntaxError as e:
        return print(e)

    write_html(target, html)


def read_code(target):
    code = ''
    with open(target) as f:
        for line in f:
            code += line
    return code


def write_html(target, string):
    new_target = target.replace('kvs', 'html')
    with open(new_target, 'w') as f:
        f.write(string)
