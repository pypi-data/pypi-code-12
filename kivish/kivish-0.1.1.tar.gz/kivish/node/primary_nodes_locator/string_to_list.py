#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
from .config import config
INDENT = config['INDENT']


def string_to_list(string):
    '''
    Rewrites given code into a list. If it contains multiline nodes,
    merges them into single logical lines.
    '''
    code = []

    multiline = {'indent': None, 'parts': []}

    for line in string.split('\n'):

        if reading_multiline_in_progress(multiline):
            finished = read_multiline(line, multiline)

            if not finished:
                continue
            else:
                code.append(finished)

        if is_multiline_label(line):
            multiline['indent'] = get_line_indent(line)
            multiline['parts'].append(get_node_label(line))
            continue

        code.append(line)

    return code


#################################


def is_multiline_label(line):
    return line.rstrip().endswith('|')


def get_line_indent(line):
    line = line.rstrip()
    return len(line) - len(line.lstrip())


def get_node_label(code):
    return code.split(':')[0] + ':'


def reading_multiline_in_progress(multiline):
    return multiline['indent'] is not None


def read_multiline(line, multiline):
    '''Returns node if finished reading, else False.'''
    if is_multiline_part(multiline['indent'], line):
        multiline['parts'].append(line)
        return False

    return merge_multiline_parts(multiline)


def is_multiline_part(multiline_indent, line):
    return multiline_indent <= get_line_indent(line) - INDENT


def merge_multiline_parts(multiline):
    indent = multiline['indent']
    merged = multiline['parts'][0] + ' '

    for part in multiline['parts'][1:]:
        merged += extract_indented_text(part, indent)

    multiline['indent'], multiline['parts'] = None, []

    return merged[:-1]


def extract_indented_text(part, indent):
    return part[indent + INDENT:].rstrip() + '\n'
