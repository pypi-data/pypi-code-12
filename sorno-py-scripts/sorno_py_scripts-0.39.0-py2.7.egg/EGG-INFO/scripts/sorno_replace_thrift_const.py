#!/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python
"""Replaces constants with literal values for a thrift file except for the
declaration. This is mainly for thrift compilers which cannot handle constants
within lists or other collection structures.


    Copyright 2014 Heung Ming Tai

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import argparse
import re
import sys


class ThriftConstReplacerApp(object):
    def run(self, filepath):
        replacer = ThriftConstReplacer()
        with open(filepath) as f:
            for line in f:
                print(replacer.parse_line(line), end="")


class ThriftConstReplacer(object):
    def __init__(self):
        self._consts = {}
        self._coming_line_is_for_this_const = None

    def parse_line(self, line):
        """
        Parse a line, then replace the constants with literal values as
        needed. If a constant declaration is parsed, the constant is stored,
        so that the literal value can be used to replace other lines later.

        All constants can be retrieved using get_consts.
        """
        # 1. Check if we have to take care of previous line constant
        # declaration
        if self._coming_line_is_for_this_const:
            value = self._line_without_semicolon_stripped(line)
            self._consts[self._coming_line_is_for_this_const] = value
            self._coming_line_is_for_this_const = None
            return line

        # 2. Replace constants with the corresponding value
        tokens = self._parse_line(line)
        for token in tokens:
            if token.s in self._consts:
                token.s = self._consts[token.s]

        line = "".join([t.s for t in tokens])

        # 3. Handle constant declaration
        tokens = self._line_without_semicolon_stripped(line).split()

        # A constant declaration is like (make sure we don't store constants
        # which are collections) :
        #
        #   const string a = "abc"
        # or
        #   const string a =
        #       "long value"
        #
        # so it has at least four tokens.
        if len(tokens) >= 4:
            if tokens[0] == "const" and (
                tokens[3] == "=" and "<" not in tokens[1]
            ):
                const = tokens[2]
                if len(tokens) >= 5:
                    # there is at least one value on the right size of the
                    # equal sign, so get the value on the right side of the
                    # equal sign
                    value = self._line_without_semicolon_stripped(
                        line
                    ).split('=', 1)[1].strip()
                    self._consts[const] = value
                else:
                    # assume the next line is the value for the constant
                    self._coming_line_is_for_this_const = const

        return line

    def get_consts(self):
        return self._consts

    def _line_without_semicolon_stripped(self, line):
        return line.strip().rstrip(';').strip()

    def _parse_line(self, line):
        tokens = []

        while line:
            m = NonWord.REGEX.match(line)
            if m:
                tokens.append(NonWord(m.group(1)))
                line = NonWord.REGEX.sub("", line, count=1)
            else:
                m = Word.REGEX.match(line)
                tokens.append(Word(m.group(1)))
                line = Word.REGEX.sub("", line, count=1)

        return tokens


class Word(object):
    """
    matches any alphanumeric character and the underscore; this is equivalent
    to the set [a-zA-Z0-9_].
    """
    REGEX = re.compile(r"(\w+)")

    def __init__(self, s):
        self.s = s


class NonWord(object):
    REGEX = re.compile("(\W+)")

    def __init__(self, s):
        self.s = s


def parse_args(cmd_args):
    description = """
Replace constants with literal values for a thrift file except for the
declaration. This is mainly for thrift compilers which cannot handle constants
within lists or other collection structures.
    """
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
    )
    parser.add_argument(
        "file"
    )

    args = parser.parse_args(cmd_args)
    return args


def main():
    args = parse_args(sys.argv[1:])

    app = ThriftConstReplacerApp()
    app.run(args.file)


if __name__ == '__main__':
    main()
