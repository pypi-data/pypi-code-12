#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-


def report(msg, num_line=None):
    if num_line:
        raise SyntaxError('<error @ line {}> {}'.format(num_line, msg))
    else:
        raise SyntaxError('<error> {}'.format(msg))
