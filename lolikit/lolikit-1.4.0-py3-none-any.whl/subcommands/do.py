#########################################################################
#  The MIT License (MIT)
#
#  Copyright (c) 2014~2016 CIVA LIN (林雪凡)
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
import subprocess
import pathlib

from .. import command
from .. import utils


class DoCommand(command.Command):
    def get_name(self):
        return 'do'

    def register_parser(self, subparsers):
        parser = subparsers.add_parser(
            self.get_name(),
            formatter_class=argparse.RawTextHelpFormatter,
            help='do some task on a path based on project\'s root dir',
            description='do some task on a path based on project\'s root dir\n'
                        '\n'
                        'if user not assign EXECUTABLE, then default\n'
                        'editor or default file browser will be used.')

        parser.add_argument(
            'entry', metavar='ENTRY', type=pathlib.Path, nargs='?',
            default=pathlib.Path(''),
            help='file / directory path based on project root dir.\n'
                 'blank = project root directory')

        parser.add_argument(
            '-x', '--executable', dest='executable', metavar='EXECUTABLE',
            help='assign any executable can accept one path argument\n'
                 'e.g., -x vim, -x touch, -x trash')

    def run(self, args):
        self.require_rootdir()

        path = self.rootdir / args.entry

        if args.executable:
            executable = args.executable
        else:
            if path.is_dir():
                executable = self.config['selector']['file_browser']
            else:
                executable = self.config['selector']['editor']

        command = utils.get_opener_command(executable, path)

        try:
            subprocess.call(command)
        except FileNotFoundError:
            print('executable: "{}" not found. cancel.'.format(command[0]))
