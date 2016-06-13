#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    bagel.py
    -------

    :copyright: (c) 2016 by Adam Schwartz

    Evaluate template code and render file(s)

    1. Read template as string from stdin or source_file(s)
    2. Extract code from the template
    3. Evaluate with subprocess call
    4. Substitute code back into the template
    5. Return the page as string to stdout or target_file(s)
"""

import sys
import os
import re
import subprocess
import argparse
from glob import iglob
from itertools import count


def eval_match(match):
    """Execute template match as a shell process"""

    command = match + "; exit 0"  # always return success.
    result = subprocess.check_output(command,
                                     cwd=os.getcwd(),
                                     stderr=subprocess.STDOUT,
                                     shell=True).decode("utf-8")
    return result.rstrip('\r\n')


def render_page(template):
    """Given a template, return a rendered page

    Notes:
    flags=re.DOTALL matches newlines
    n[3:-3] returns the match without curly braces
    errors are passed back into the template
    """

    token = "{{\ .*?\ }}"
    matches = re.findall(token, template, re.DOTALL)
    results = [eval_match(n[3:-3]) for n in matches]
    page = re.sub(token,
                  lambda x, y=count(0): results[next(y)],
                  template,
                  flags=re.DOTALL)
    return page


def render_file(source, target_file):
    """Render a template from a source file and write it to target file"""

    with open(source, "r") as t:
        t_string = t.read()
        with open(target_file, "w") as p:
            p.write(render_page(t_string))


def render_to_location(source, target, file_extension="*"):
    """Render all templates in a source directory matching a given file
    extension then write them to the target directory

    Cases:
(1) `source` is a directory: Render all files matching the
    `file_extension` and write them to the target directory
    If no `file_extension` is specified, render all files
(2) `source` is a file, but `target` is a directory:
    Render `source` into `target`
(3) `source` is a file: Read template from file and write to target
    """

    # Handles case (1)
    if os.path.isdir(source):
        # Create `target` directory if it doesn't already exist
        try:
            os.mkdir(target)
        except:
            if not os.path.isdir(target):
                raise

        # Create generator object for all matching files in `source`
        source_glob = "*." + file_extension.lower()
        templates = iglob(os.path.join(source, source_glob))

        # render all files to target directory
        for tmpl in templates:
            target_file = target + '/' + os.path.basename(tmpl)
            render_file(tmpl, target_file)

    else:
        if os.path.isdir(target):
            # Handles case (2)
            target_file = target + '/' + os.path.basename(source)
        else:
            target_file = target  # Handles case (3)

        render_file(source, target_file)  # Finally render the file


def main():
    """Define command line line operation"""

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Evaluate template code and render file(s)")
    parser.add_argument("-t", "--file-type", action="store", dest="file_type",
                        help="file extension for templates (ex: html)")
    parser.add_argument("source", type=str,
                        help="input path", nargs="?")
    parser.add_argument("target", type=str,
                        help="output path", nargs="?")
    args = parser.parse_args()

    # Read from stdin and write to stdout if no files are specified
    if (args.source is None and args.target is None):
        try:
            template = sys.stdin.read()
            sys.stdout.write(render_page(template))
        except KeyboardInterrupt:
            sys.stdout.write("\r\n")
            pass
    else:
        render_to_location(args.source, args.target, args.file_type)


if __name__ == "__main__":
    main()
