#!/usr/bin/env python
from __future__ import print_function
import sys
from subprocess import Popen, PIPE
from .version import __version__

# http://www.w3.org/TR/PNG/#5PNG-file-signature
PNG_START = b'\x89PNG\x0D\x0A\x1A\x0A'
# http://www.w3.org/TR/PNG/#11IEND
PNG_END = b'\x00\x00\x00\x00IEND\xAE\x42\x60\x82'


def handle_stream(f, callback):
    pattern_state = PNG_START
    unmatched_pattern = pattern_state
    buffer = b''

    while True:
        b = f.read(1)
        if not b:
            break

        buffer += b
        if b[0] == unmatched_pattern[0]:
            unmatched_pattern = unmatched_pattern[1:]
        else:
            unmatched_pattern = pattern_state
            if pattern_state == PNG_START:
                buffer = b''

        if len(unmatched_pattern) == 0:
            if pattern_state == PNG_START:
                pattern_state = PNG_END
            else:
                callback(buffer)
                buffer = b''
                pattern_state = PNG_START
            unmatched_pattern = pattern_state


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h']:
        print('\'eachpng\' executes command lines for each PNG from standard input ')
        print('and forwards their output to stdout.')
        print('\nUsage: eachpng command arg1 arg2...')
        print('\nVersion %s' % __version__)
        exit(0)

    def execute(buffer):
        p = Popen(" ".join(sys.argv[1:]), shell=True, stdin=PIPE, stdout=sys.stdout)
        p.communicate(buffer)
        if p.returncode != 0:
            exit(p.returncode)

    handle_stream(sys.stdin, execute)


if __name__ == '__main__':
    main()