#!/usr/bin/env python
"""sorno_attach_realdate.py attaches the actual time in human readable format
for timestamps found in coming lines.

Example:

    $ cat /tmp/abc
    once upon a time 1455225387 there is
    1455225387 something called blah
    and 1455225387
    then foo

    $ cat /tmp/abc |python scripts/sorno_attach_realdate.py
    once upon a time 1455225387(2016-02-11 13:16:27) there is
    1455225387(2016-02-11 13:16:27) something called blah
    and 1455225387(2016-02-11 13:16:27)
    then foo


    Copyright 2016 Heung Ming Tai

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
import fileinput
import re
import sys

from sorno import datetimeutil


_datetime_format = "%Y-%m-%d %H:%M:%S"
_non_timestamp_chars_regex = re.compile("[^-_0-9a-zA-Z:]")


class AttachRealDateApp(object):
    def __init__(self, args):
        self.args = args

    def run(self):
        for line in fileinput.input([]):
            sys.stdout.write(self._process(line))
        return 0

    def _process(self, line):
        newline = datetimeutil.TIMESTAMP_REGEX.sub(self._repl, line)
        if newline == line:
            newline = self._aggressive_process(line)

        return newline

    def _aggressive_process(self, line):
        words = []
        for word in line.split(' '):
            # We only parse date time strings, so at least
            # YYYYMMDDHHmmss 14 characters
            if len(word) >= 14:
                w = _non_timestamp_chars_regex.sub("", word)
                if len(w) >= 14:
                    try:
                        dt = datetimeutil.guess_local_datetime(w)
                        # We want to attach a local datetime before trailing
                        # newlines or other whitespaces for this word
                        m = re.match(r"(.*)(\s+)", word)
                        if m:
                            word = m.group(1)
                            trailing_spaces = m.group(2)
                        else:
                            trailing_spaces = ""

                        word = "%s(%s)%s" % (
                            word,
                            dt.strftime(self.args.datetime_format),
                            trailing_spaces,
                        )
                    except ValueError as ex:
                        pass

            words.append(word)

        return " ".join(words)

    def _repl(self, match):
        potential_ts = match.group()
        num = int(potential_ts)
        try:
            dt, unit = datetimeutil.number_to_local_datetime(num)
        except ValueError:
            return potential_ts

        return "%s(%s)" % (
            potential_ts,
            dt.strftime(self.args.datetime_format),
        )


def parse_args(cmd_args):
    description = __doc__.split("Copyright 2016")[0].strip()

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--datetime-format",
        help="The string to format datetime. Use the formats"
        " supported by strftime. Default: \"%(default)s\".",
        default=_datetime_format,
    )

    args = parser.parse_args(cmd_args)
    return args


def main():
    args = parse_args(sys.argv[1:])

    app = AttachRealDateApp(args)
    sys.exit(app.run())


if __name__ == '__main__':
    main()
