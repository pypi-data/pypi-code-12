#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
from .config import config
INDENT = config['INPUT_INDENT']


class ValueReader:
    '''Reads value of a given line (raw node). Is aware of multiline syntax.'''

    def __init__(self, line):
        self._line = line
        self._line_indent = get_line_indent(line)

    def read(self) -> str:
        '''Return value of the given line.'''
        line, line_indent = self._line, self._line_indent

        value = extract_value_part(line)

        if not value:
            return None

        if is_multiline_value(value):
            return merge_multiline_value(line_indent, value)
        elif has_multiline_escape(value):
            return remove_multiline_escape(value)
        else:
            return value


def extract_value_part(line):
    parts = line.split(':', 1)
    if len(parts) > 1:
        return parts[1].strip()
    else:
        return None


def is_multiline_value(value):
    first_chars = value.lstrip()[:2]
    return first_chars[0] == '|' and first_chars != r'\|'


def merge_multiline_value(node_indent, value):
    inline_value = ''

    parts = value.split('\n')[1:]

    for line in parts:

        line_indent = get_line_indent(line)
        if line_indent == node_indent + INDENT:
            inline_value += line.strip() + '\n'
        else:
            break

    return inline_value.strip()


def get_line_indent(line):
    line = line.rstrip()
    return len(line) - len(line.lstrip())


def has_multiline_escape(value):
    return value.lstrip()[0:2] == '\|'


def remove_multiline_escape(value):
    return value.lstrip()[1:]
