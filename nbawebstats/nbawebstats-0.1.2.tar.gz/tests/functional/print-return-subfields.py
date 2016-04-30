#!/usr/bin/env python

import sys
import pickle


def lineify_strings(strings, line_len,  delimiter):
    string_sets = []
    current_string_set = []
    current_string_set_len = 0
    for string in strings:
        if len(string) > line_len:
            raise ValueError("String '{0}' exceeds line length of {1}."
                             .format(string, line_len))

        if current_string_set_len + len(string) + len(delimiter) > line_len:
            string_sets.append(current_string_set)
            current_string_set = []
            current_string_set_len = 0

        current_string_set.append(string)
        current_string_set_len += len(string) + len(delimiter)

    return [delimiter.join(x) for x in string_sets]


def build_return_lines(field_name, subfields):
    prefix = ' ' * 21 + '"'
    postfix = '",'
    delimiter = '", "'

    line_len = 79 - len(prefix) - len(postfix)

    raw_lines = lineify_strings(subfields, line_len, delimiter)
    if len(raw_lines) > 1:
        bookended_lines = [prefix + x + postfix for x in raw_lines]
        bookended_lines[0] = bookended_lines[0][:20] + '[' + bookended_lines[0][21:]
        bookended_lines[-1] = bookended_lines[-1][:-1] + ']],'
    elif len(raw_lines) == 1:
        bookended_lines = [prefix[:-1] + '[' + raw_lines[0] + postfix]
    else:
        bookended_lines = []

    lines = ['                ["{0}",'.format(field_name)]
    lines.extend(bookended_lines)

    return '\n'.join(lines)


def print_request(rname, rdata):
    print(rname + ':')
    try:
        for fname, fdata in rdata['response'].items():
            if fdata:
                print(build_return_lines(fname, list(fdata[0].keys())))
    except KeyError:
        pass


if __name__ == '__main__':
    with open('test-results.pickle', 'rb') as f:
        a = pickle.load(f)

    if len(sys.argv) == 2:
        rname = sys.argv[1]
        print_request(rname, a[rname])
    elif len(sys.argv) > 2:
        for rname in sys.argv[1:]:
            print('')
            print_request(rname, a[rname])
    else:
        for rname, rdata in sorted(list(a.items())):
            print('')
            print_request(rname, rdata)
