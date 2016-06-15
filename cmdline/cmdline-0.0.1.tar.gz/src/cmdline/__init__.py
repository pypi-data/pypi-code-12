from __future__ import absolute_import

from .logconfig import setup_logging
setup_logging()

import argparse
import logging
import os
import sys

import yaml

from collections import defaultdict

from .exceptions import CommandError
from .settings import Settings

settings = Settings()


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


class SettingsCommand(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(SettingsCommand, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))

    def run(self):
        args = self.parser.parse_args()

        for item in dir(args):
            if item.startswith('_'):
                continue
            elif item == 'subcommand':
                continue

            v = getattr(args, item)

            k = item.upper().replace('-', '_')
            if v != settings.settings[k]['default']:
                self.logger.debug('cmdline k={}, v={}'.format(k, v))

                setattr(settings, k, v)

    def setup_parser(self, args=None, parser=None):
        subcommands = defaultdict(dict)
        args = args or settings.settings
        parser = parser or self.parser

        for key, info in args.items():
            subcommand = info.pop('subcommand', None)
            if subcommand:
                subcommands[subcommand][key] = info
                continue

            _info = info.copy()

            arg = '--{}'.format(key.lower().replace('_', '-'))
            if 'type' in _info:
                _info['type'] = __builtins__[_info['type']]

            parser.add_argument(arg, **_info)

        if subcommands:
            self.subparsers = parser.add_subparsers(help='sub-commands')

        for subcommand, args in subcommands.items():
            subcommand_parser = self.subparsers.add_parser(subcommand)

            # instantiate the command to fill the parser
            self.setup_parser(args=args, parser=subcommand_parser)

            subcommand_parser.set_defaults(subcommand=subcommand)
