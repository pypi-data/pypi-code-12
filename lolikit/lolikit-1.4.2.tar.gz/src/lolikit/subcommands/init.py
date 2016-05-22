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
import pathlib
import os
import sys

from .. import command
from .. import utils


class InitCommand(command.Command):
    def get_name(self):
        return 'init'

    def register_parser(self, subparsers):
        parser = subparsers.add_parser(
            self.get_name(),
            formatter_class=argparse.RawTextHelpFormatter,
            help='initialize a loli project',
            description='initialize a loli project')

        parser.add_argument(
            'path', metavar='PATH', nargs='?', type=pathlib.Path,
            default=pathlib.Path(os.getcwd()),
            help='new loli project folder\n'
                 'default = current working directory')

    def exit_if_rootdir_exists(self, path):
        def rootdirs_in_children(path):
            rootdirs = [p.parent for p in path.rglob('.loli')
                        if p.is_dir()]
            return rootdirs

        rootdir = utils.get_rootdir_from_parents(path)
        if rootdir is not None:
            print(
                'abort: the path "{}" already in a'
                ' loli project folder.'.format(str(path)))
            sys.exit(0)

        rootdirs = rootdirs_in_children(path)
        if rootdirs:
            print('about: the path "{}" has one or more sub-directories'
                  ' are loli project folder.'.format(str(path)))
            sys.exit(0)

    def run(self, args):
        self.exit_if_rootdir_exists(args.path)
        lolidir = args.path / '.loli'
        try:
            lolidir.mkdir(parents=True)
        except NotADirectoryError:
            print('about: the path "{}" already'
                  ' be occupied by a file.'.format(str(args.path)))
            sys.exit(0)
        print('Create a loli project in "{}" successful.\n'
              'Try to put some .md file into the folder or sub-folder'
              ' as your notes.'
              .format(str(args.path)))
