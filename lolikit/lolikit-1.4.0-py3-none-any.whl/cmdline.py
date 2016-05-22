#########################################################################
#  The MIT License (MIT)
#
#  Copyright (c) 2014~2015 CIVA LIN (林雪凡)
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files
#  (the "Software"), to deal in the Software without restriction, including
#  without limitation the rights to use, copy, modify, merge, publish,
#  distribute, sublicense, and/or sell copies of the Software, and to
#  permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#  CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#  TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##########################################################################


import argparse
import textwrap
import sys
import os

from . import info
from . import subcommandload as SCL
from . import utils


def build_parser(config, commands, light_mode=False):
    def get_parser():
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter,
            description=textwrap.fill(info.DESCRIPTION, 70))

        parser.add_argument(
            '--version', action='version', version=info.VERSION)

        parser.add_argument(
            '--cwd', dest='cwd',
            help='change current working directory')

        parser.add_argument(
            '--get-root', dest='get_root', action='store_true',
            help=argparse.SUPPRESS
            # help='get root dir of current project and exit'
            )

        return parser

    def get_subparsers(parser):
        subparsers = parser.add_subparsers(
            title='Commands', metavar=None,
            help='Use "-h" to get help messages of sub-commands.\n'
                 '(e.g., "%(prog)s find -h")',
            dest='command')
        return subparsers

    def register_subcommands(subparsers, commands):
        for cmd in commands:
            cmd.register_parser(subparsers)

    parser = get_parser()
    if not light_mode:
        subparsers = get_subparsers(parser)
        register_subcommands(subparsers, commands)
    return parser


def process(args, commands, rootdir):
    if args.get_root:
        print(str(rootdir) if rootdir else '')
        return

    for cmd in commands:
        if args.command == cmd.get_name():
            cmd.run(args)


def main():
    def generate_init_obj(cwd):
        os.chdir(cwd)
        no_rootdir_config = utils.get_config(None)
        rootdir = utils.get_rootdir(no_rootdir_config)
        config = utils.get_config(rootdir)
        commands = SCL.get_commands_list(config, rootdir)
        parser = build_parser(config, commands)
        return parser, commands, rootdir

    utils.register_signal_handler()
    parser, commands, rootdir = generate_init_obj(os.getcwd())
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    else:
        args = parser.parse_args()
        if args.cwd and args.cwd != os.getcwd():
            args, commands, rootdir = generate_init_obj(args.cwd)
        return process(args, commands, rootdir)
