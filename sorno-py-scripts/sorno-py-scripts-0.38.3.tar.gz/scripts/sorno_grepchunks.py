#!/usr/bin/env python
"""sorno_grepchunks greps chunks for a regex.

Oftenly, you want to treat multiple lines as one chunk and see if it matches a
regex. If it does, you want to print out the whole chunk instead of the only
line that matches the regex. sorno_grepchunks lets you define what a chunk
is by giving a chunk starting regex, that is, all the lines starting from the
line that matches the regex and before the next match are treated as one
chunk. You can then apply another regex to match against it.

Examples:

    Setup:
        $ printf "chunk1\napple\nboy\nchunk2dog\n" > /tmp/sample

    The first chunk has a 'e', followed by a newline, then a 'b', so:
        $ sorno_grepchunks.py --chunk-starting-regex chunk "e.b" /tmp/sample
        chunk1
        apple
        boy

    Grep for "o" which appears in all two chunks:

        $ python scripts/sorno_grepchunks.py --chunk-starting-regex chunk "o" /tmp/sample
        chunk1
        apple
        boy
        chunk2dog

    Gre for "og" which appears only in the second chunk:
        $ python scripts/sorno_grepchunks.py --chunk-starting-regex chunk "og" /tmp/sample
        chunk2dog
        $


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
import logging
import re
import sys

from sorno import loggingutil


_log = logging.getLogger()
_plain_logger = None  # will be created in main()
_plain_error_logger = None  # will be created in main()


class GrepChunksApp(object):
    """A console application to do work"""
    def __init__(
        self,
        args,
    ):
        """
        Args:
            args (argparse.Namespace): The flags for the script.
        """
        self.args = args
        self._partial_chunk = ""
        self._regex = re.compile(args.regex, re.DOTALL)

    def run(self):
        chunk_starting_regex = re.compile(self.args.chunk_starting_regex)
        for f in self.args.file:
            # Read the whole file and if a chunk is closed, grep it
            with open(f) as fh:
                for line in fh:
                    s = self._grep_if_exists(
                        self._feed(line, chunk_starting_regex)
                    )
                    if s is not None:
                        print(s, end="")

            s = self._grep_if_exists(self._close_partial_chunk())
            if s is not None:
                print(s, end="")

        return 0

    def _feed(self, line, chunk_starting_regex):
        chunk = None
        if chunk_starting_regex.search(line):
            chunk = self._close_partial_chunk()

        self._partial_chunk += line
        return chunk

    def _close_partial_chunk(self):
        if self._partial_chunk:
            chunk = self._partial_chunk
            self._partial_chunk = ""
            return chunk

        return None

    def _grep_if_exists(self, chunk):
        if chunk is not None:
            if self._regex.search(chunk):
                return chunk

        return None


def parse_args(cmd_args):
    description = __doc__.split("Copyright 2016")[0].strip()

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
    )
    parser.add_argument(
        "--chunk-starting-regex",
        help="The regex that matches the starting of a chunk. The ending of a"
        " chunk is defined as the end of a file or the line before the"
        " starting of another chunk."
    )
    parser.add_argument(
        "regex",
        help="Any chunks matching the regex are printed."
    )
    parser.add_argument(
        "file",
        nargs="+",
    )

    args = parser.parse_args(cmd_args)
    return args


def main():
    global _plain_logger, _plain_error_logger

    args = parse_args(sys.argv[1:])

    loggingutil.setup_logger(_log, debug=args.debug)
    _plain_logger = loggingutil.create_plain_logger(
        "PLAIN",
        debug=args.debug,
    )
    _plain_error_logger = loggingutil.create_plain_logger(
        "PLAIN_ERROR",
        debug=args.debug,
        stdout=False,
    )

    app = GrepChunksApp(
        args,
    )
    sys.exit(app.run())


if __name__ == '__main__':
    main()
