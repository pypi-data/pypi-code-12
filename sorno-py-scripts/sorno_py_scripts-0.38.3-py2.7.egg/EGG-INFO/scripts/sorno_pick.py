#!/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python
"""A script to prompt for choosing items generated from different sources, then
print those items out. You can then use those items for other shell commands.

Examples:

    If you have a script to generate common directories that you use, e.g.
    gen-fav-dir.sh, you can put the following in your .bashrc, assuming
    sorno_pick.py and gen-fav-dir.sh are in your PATH:

        $ alias cdf='cd $(sorno_pick.py -c gen-fav-dir.sh)'

    Then you can just type:

        $ cdf

    And you will be given a list of directories to "cd" to.

    P.S. You probably want to set the alias to the following:

        $ alias cdf='tmp="cd $(sorno_pick.py -c gen-fav-dir.sh)";history -s \\
            "$tmp";$tmp'

    This ensures the history is inserted in a useful way, e.g. when you run
    "history" or press the "up" key, you see the actual command "cd xxx" instead
    of just "cdf".

    I personally have a few template files, so I have a file to store the
    directories containing my template files, then I put the following
    function in my bashrc file:

        function copy-from-paths() {
          local dest_file=$1
          shift
          cp $(sorno_pick.py --filepaths-from-file \\
              ~/path/to/copy-from-paths.txt "$@") "$dest_file"
        }

    Notice the use of "$@", that allows me to add options to sorno_pick.py,
    e.g. -r '\\.py$' to only get template files for python. The whole coomand
    is:

        copy-from-paths /tmp/tmpfile -r '\.py$'

    Similarily, I have the following function for vim:

        function vic {
          local tmp="vim -O $(sorno_pick.py -c generate_files.py \\
            --output-delimiter ' ' $@)"
          history -s "$tmp"
          $tmp
        }


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
import logging
import os
import re
import sys
import subprocess


from sorno import loggingutil
from sorno import consoleutil


_LOG = logging.getLogger(__name__)


class PickerApp(object):
    def __init__(
        self,
        commands=None,
        filepaths=None,
        filepaths_from_filepaths=None,
        regexes=None,
        exclude_regexes=None,
        output_delimiter=os.linesep,
        output_items_with_path_expansions=False,
        enumerate_items=True,
        list_only=False,
        is_lucky=False
    ):
        self.commands = commands
        self.filepaths = filepaths
        self.filepaths_from_filepaths = filepaths_from_filepaths
        self.regexes = regexes
        self.exclude_regexes = exclude_regexes
        self.output_delimiter = output_delimiter
        self.output_items_with_path_expansions = (
            output_items_with_path_expansions
        )
        self.enumerate_items = enumerate_items
        self.list_only = list_only
        self.is_lucky = is_lucky

    def run(self):
        items = []
        items.extend(self.get_items_from_commands())
        items.extend(self.get_items_from_filepaths())
        items.extend(self.get_items_from_filepaths_from_filepaths())

        items = self.filter_out_items(items)

        chosen_items = self.pick_items(items)
        self.print_chosen_items(chosen_items)

    def pick_items(self, items):
        items = list(set(items))
        items.sort()

        if self.enumerate_items:
            for i, item in enumerate(items, 1):
                print("%d)" % i, item, file=sys.stderr)
        else:
            for item in items:
                print(item, file=sys.stderr)

        if self.list_only:
            return []

        if self.is_lucky:
            if items:
                return [items[0]]
            else:
                return []

        reply = consoleutil.input("Please choose:", file=sys.stderr)

        num_strs = [s.strip() for s in reply.split(',')]
        nums = []
        for s in num_strs:
            nums.extend(self.num_str_to_nums(s))

        chosens = [items[num - 1] for num in nums]
        return chosens

    def num_str_to_nums(self, num_str):
        if num_str:
            return [int(num_str)]
        else:
            return []

    def print_chosen_items(self, chosen_items):
        if self.output_items_with_path_expansions:
            _LOG.debug("Items are expanded with path expansions")
            chosen_items = [
                self.expand_path(item)
                for item in chosen_items
            ]

        if chosen_items:
            print(self.output_delimiter.join(chosen_items))

    def filter_out_items(self, items):
        if not self.regexes and not self.exclude_regexes:
            return items


        if self.regexes:
            remaining_items = []
            for item in items:
                matched = True
                for regex in self.regexes:
                    if not re.search(regex, item):
                        _LOG.debug(
                            "Item [%s] does not match the regex [%s]",
                            item,
                            regex,
                        )
                        matched = False
                        break

                if matched:
                    remaining_items.append(item)

            items = remaining_items

        if self.exclude_regexes:
            remaining_items = []
            regex = "|".join(["(" + r + ")" for r in self.exclude_regexes])
            _LOG.debug("Regex to be used for exclusion: %s", regex)

            for item in items:
                if re.search(regex, item):
                    _LOG.debug("Item [%s] is excluded", item)
                else:
                    remaining_items.append(item)

            items = remaining_items

        return items

    def get_items_from_commands(self):
        items = []
        if not self.commands:
            return items

        for command in self.commands:
            _LOG.debug("Execute command [%s] to get items", command)
            output = subprocess.check_output(command, shell=True)
            for line in output.split(os.linesep):
                line = line.rstrip(os.linesep)
                if line:
                    items.append(line)

        return items

    def get_items_from_filepaths(self):
        items = []
        if not self.filepaths:
            return items

        for filepath in self.filepaths:
            _LOG.debug("Read items from file [%s]", filepath)
            with open(filepath) as f:
                for line in f:
                    items.append(line.strip())

        return items

    def get_items_from_filepaths_from_filepaths(self):
        items = []
        if not self.filepaths_from_filepaths:
            return items

        for filepath in self.filepaths_from_filepaths:
            _LOG.debug("Read filepaths from file [%s]", filepath)
            with open(filepath) as f:
                for line in f:
                    items.extend(
                        self.retrieve_filepaths(self.expand_path(line.strip()))
                    )

        return items

    def retrieve_filepaths(self, filepath):
        filepaths = []
        if os.path.exists(filepath):
            if os.path.isdir(filepath):
                for root, dirs, files in os.walk(filepath):
                    for filename in files:
                        filepaths.append(os.path.join(root, filename))
            else:
                filepaths.append(filepath)

        return filepaths

    def expand_path(self, path):
        return os.path.expandvars(os.path.expanduser(path))


def parse_args(cmd_args):
    description = __doc__.split("Copyright 2014")[0].rstrip()
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--debug",
        action="store_true",
    )

    item_sources_options = parser.add_argument_group('Item sources')
    item_sources_options.add_argument(
        "-c", "--command",
        help="Shell commands to generate items to be picked from."
            + " The commands are invoked in a subshell and should print out"
            + " one item per line. Empty lines are filtered out",
        action="append",
    )
    item_sources_options.add_argument(
        "-f", "--file",
        help="Files that contain items to be picked from. Each line of the"
            + " file contains one item. Leading and trailing spaces are"
            + " removed and empty lines are filtered out.",
        action="append",
    )
    item_sources_options.add_argument(
        "--filepaths-from-file",
        help="Treat each item of a file as a filepath or a directory path."
            + " If it's a filepath, it's listed to be picked as is if the"
            + " file exists. If it's"
            + " a directory path, the files inside the directory are used"
            + " instead of the directory path, recursively.",
        action="append",
    )
    item_sources_options.add_argument(
        "-e", "--exclude-regex",
        help=re.sub(r"\s+", " ", """
            Items matching the regex are not shown in the list to be picked.
        """),
        action="append",
    )
    item_sources_options.add_argument(
        "-r", "--regex",
        help=re.sub(r"\s+", " ", """
            Only items matching the regex are shown in the list to be picked.
        """),
        action="append",
    )

    output_options = parser.add_argument_group("Output options")

    output_options.add_argument(
        "--output-delimiter",
        default=os.linesep,
        help="The delimiter for the choosen items printed out. By default,"
            + "the OS specific line separating character(s) is used.",
    )
    output_options.add_argument(
        "--output-items-with-path-expansions",
        help="When printing out the items, treats them as paths with"
        + " shell-like path expansion. This includes: \"~\", \"~user\", and "
        + " environment variables denoted by \"$var\" or \"${var}\"",
        action="store_true",
    )
    output_options.add_argument(
        "--no-enumerate",
        help="Not enumerating the items.",
        dest="enumerate_items",
        action="store_false",
        default=True,
    )

    parser.add_argument(
        "-l", "--list-only",
        help="Not prompting for choosing items. Only listing them.",
        action="store_true",
    )

    parser.add_argument(
        "--lucky",
        action="store_true",
        help="Choose the first choice without prompting",
    )

    args = parser.parse_args(cmd_args)
    return args


def main():
    args = parse_args(sys.argv[1:])

    loggingutil.setup_logger(_LOG, debug=args.debug)

    app = PickerApp(
        commands=args.command,
        filepaths=args.file,
        filepaths_from_filepaths=args.filepaths_from_file,
        regexes=args.regex,
        exclude_regexes=args.exclude_regex,
        output_delimiter=args.output_delimiter,
        output_items_with_path_expansions=(
            args.output_items_with_path_expansions
        ),
        enumerate_items=args.enumerate_items,
        list_only=args.list_only,
        is_lucky=args.lucky,
    )
    app.run()


if __name__ == '__main__':
    main()
