#!/usr/bin/env python
"""Prints a summary of the code file.

It makes the layout of the code to be read easily. Currently it only supports
python files.

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


class CodeFileSummarizer(object):
    def run(self, filepath):
        with open(filepath) as f:
            content = f.read()

        PythonFileSummarizer().summarize(content)

class PythonFileSummarizer(object):
    def summarize(self, code_in_text):
        lines = code_in_text.split('\n')
        for line in lines:
            if re.match(r"def [^ ]+\(.*\):$", line.lstrip()):
                print(line)
            elif re.match(r"def [^ ]+\($", line.lstrip()):
                # print a funciton def which spans multiple lines
                print(line + "...)")
            elif re.match(r"class [^ ]+:$", line.lstrip()):
                print(line)


def parse_args(cmd_args):
    description = """
Print a summary of the code, so the layout of the code can be read easily.
    """
    parser = argparse.ArgumentParser(
        description=description,
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

    app = CodeFileSummarizer()
    app.run(args.file)


if __name__ == '__main__':
    main()
