import argparse
import sys

from .exceptions import CommandError


class BaseCommand(object):
    def __init__(self, parser=None, args=None, sys_argv=None):
        self.parser = parser or argparse.ArgumentParser()
        self.subparsers = None

        self.sys_argv = sys_argv or sys.argv[1:]

        # already parsed arguments, i.e. do not call self.parser.parse_args()
        self.args = args

        self.setup_parser()

    def parse_args(self):
        if self.args:
            raise CommandError('args are already parsed')

        self.args = self.parser.parse_args(self.sys_argv)

    def run(self):
        if not self.args:
            self.parse_args()

    def setup_parser(self):
        pass

