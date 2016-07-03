# pypimonitor — An HTML dashboard to monitor your python packages
# Copyright (C) 2016 Louis Paternault
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Gather python packages information, and render them as an HTML page."""

import argparse
import sys
import logging

import pypimonitor

LOGGER = logging.getLogger(pypimonitor.__name__)

def commandline_parser():
    """Return a command line parser."""

    parser = argparse.ArgumentParser(
        prog="pypimonitor",
        description="Produce an HTML dashboard to monitor your PyPI packages.",
        )

    parser.add_argument(
        '--version',
        help='Show version',
        action='version',
        version='%(prog)s ' + pypimonitor.VERSION
        )

    parser.add_argument(
        '-u', '--user',
        help='A comma-separated list of users, whose packages are to be monitored.',
        action="append",
        nargs=1,
        default=[],
        )

    parser.add_argument(
        '-c', '--cell',
        help='A comma-separated list of cells to show.',
        action="append",
        nargs=1,
        default=[],
        )

    parser.add_argument(
        '-p', '--package',
        help='A comma-separated list of packages to monitor.',
        action="append",
        nargs=1,
        default=[],
        )

    parser.add_argument(
        'yaml',
        help='Configuration file.',
        nargs="?",
        default=None,
        )

    return parser

def _flatten(list_of_lists):
    """Given a list of comma-separated lists, iterate over items."""
    for llist in list_of_lists:
        for item in llist:
            yield from item.split(",")

def main():
    """Main function: called when calling this module from command line."""
    arguments = commandline_parser().parse_args()
    if (arguments.yaml is not None) and (arguments.cell or arguments.package or arguments.user):
        LOGGER.error(
            "Configuration file and --cell, --package and --user arguments are incompatible."
            )
        sys.exit(1)
    if arguments.yaml is None:
        print(pypimonitor.Renderer.from_args(
            packages=_flatten(arguments.package),
            cells=_flatten(arguments.cell),
            users=_flatten(arguments.user),
            ).render())
    else:
        print(pypimonitor.Renderer.from_yaml(arguments.yaml).render())

if __name__ == "__main__":
    main()
