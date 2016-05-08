#!/usr/bin/env python
"""sorno_rename.py renames files given regex for matching names of the
existing files and using backreferences for filenames to be renamed to.

Backreferences are denoted by {0}, {1}, {2}...{0} is the entire match, and {1}
is the first matching group, etc.

The script shows you all the files to be renamed and what they will be renamed
to and prompts for a confirmation before executing the renaming.

    Copyright 2015 Heung Ming Tai

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
import os
import re
import sys

from sorno import (
    consoleutil,
    loggingutil,
    stringutil,
)


_log = logging.getLogger()
_plain_logger = None  # will be created in main()
_plain_error_logger = None  # will be created in main()


class App(object):
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
        self.filenames_map = {}

    def run(self):
        r = stringutil.u(self.args.regex)
        s = stringutil.u(self.args.sub)
        if self.args.recursive:
            for dirpath, dirs, filenames in os.walk(self.args.dir):
                for fname in filenames:
                    self.process_file(r, s, dirpath, fname)
        else:
            filenames = os.listdir(self.args.dir)
            for fname in filenames:
                self.process_file(r, s, self.args.dir, fname)

        n = len(self.filenames_map)
        sn = len(str(n))

        for i, (k, v) in enumerate(self.filenames_map.iteritems()):
            print(u"%*d. %s => %s" % (sn, i + 1, k, v))

        if consoleutil.confirm("Do you want to do the rename?"):
            for i, (k, v) in enumerate(self.filenames_map.iteritems()):
                print("%*d. Rename %s to %s" % (sn, i + 1, k, v))
                os.rename(k, v)
            return 0
        else:
            print("Aborted")
            return 1

    def process_file(self, regex, sub, dirpath, filename):
        filename = stringutil.u(filename)
        m = re.match(regex, filename, re.UNICODE)
        if m:
            old = os.path.abspath(os.path.join(dirpath, filename))
            groups = (m.group(0),) + m.groups()
            new = os.path.abspath(
                os.path.join(
                    dirpath,
                    sub.format(*groups),
                )
            )
            self.filenames_map[old] = new


def parse_args(cmd_args):
    description = __doc__.split("Copyright 2015")[0].strip()

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
    )
    parser.add_argument(
        "dir",
        nargs="?",
        help=stringutil.oneline(
            """
            The directory that contains the files (default "%(default)s"). The
            script traverses all the files in the directory and
            subdirectories.
            """
        ),
        default=".",
    )
    parser.add_argument(
        "-R",
        "--recursive",
        help=stringutil.oneline(
            """
            Recursively goes to subdirectories to look for files to be renamed
            """
        ),
        action="store_true",
    )
    parser.add_argument(
        "--regex",
        help="Regex to match filenames",
        default='.*',
    )
    parser.add_argument(
        "--sub",
        help=stringutil.oneline(
            """
            The new filenames. You can use backreferences which are denoted by
            {0}, {1}, {2}...{0} is the entire match, and {1} is the first"
            matching group, etc.
            """
        ),
        default="{0}",
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

    app = App(
        args,
    )
    sys.exit(app.run())


if __name__ == '__main__':
    main()
