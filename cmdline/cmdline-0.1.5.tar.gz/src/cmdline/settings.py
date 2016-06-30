from __future__ import absolute_import

import logging
import os

from collections import defaultdict
from importlib import import_module

import yaml

from . import BaseCommand
from .config import get_config_paths
from .exceptions import SettingsError


class Settings(object):
    """
    Compiles settings by traversing the config paths returned by get_config_paths()
    """
    def __init__(self):
        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        self.paths = []

        # after the first settings file is processed, new setting names are 
        # not allowed to be injected; only the values of existing names can
        # be overridden.  this is to avoid silly typos in override settings
        # and the default settings file distributed with the code should be
        # the comprehensive list of all settings
        self._compiled_settings = None

    def get_settings_from_file(self, settings_path):
        if os.path.exists(settings_path):
            self.paths.append(settings_path)

            with open(settings_path, 'r') as fh:
                data = yaml.load(fh)

                return data

    def run(self):
        # look for all config paths on the filesystem
        for settings_path in get_config_paths(filename='settings.yml'):
            self.logger.debug('trying {}'.format(settings_path))

            _settings = self.get_settings_from_file(settings_path)
            if not _settings:
                continue

            for k, i in _settings.items():
                if k.startswith('_'):
                    continue

                v = i.get('default')

                self.logger.debug('k={}, v={}'.format(k, v))

                if self._compiled_settings and k not in self._compiled_settings:
                    raise ValueError('setting {} not in {}'.format(k, self.paths[0]))

                setattr(self, k, v)

            self._compiled_settings = self._compiled_settings or _settings

        if not self._compiled_settings:
            raise SettingsError('Settings config not found')

        # look for environment variables that match settings keys
        for k in self._compiled_settings:
            if k in os.environ:
                v = os.environ[k]

                self.logger.debug('env k={}, v={}'.format(k, v))
                setattr(self, k, v)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, str(self.paths))


class SettingsParser(BaseCommand):
    """
    Produces an ArgumentParser instance that provides arguments
    for all settings found by the .settings.Settings class
    """
    settings = Settings()

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))

        super(SettingsParser, self).__init__(*args, **kwargs)

    @classmethod
    def compile_settings(cls, *args, **kwargs):
        if cls.settings._compiled_settings is None:
            cls.settings.run()

            settings_parser = SettingsParser(*args, **kwargs)
            settings_parser.run()

        return cls.settings

    def run(self):
        args = self.parse_args()

        for item in dir(args):
            if item.startswith('_'):
                continue
            elif item == 'subcommand':
                continue

            v = getattr(args, item)

            k = item.upper().replace('-', '_')
            if v != getattr(self.settings, k):
                self.logger.debug('cmdline k={}, v={}'.format(k, v))

                setattr(self.settings, k, v)

        subcommand = getattr(args, 'subcommand', None)
        self.settings._SUBCOMMAND = subcommand

        return self.settings

    def setup_parser(self):
        args = self.settings._compiled_settings
        parser = self.parser

        self.parse(args, parser)

        command_info = args.get('_COMMANDS', {})
        for k, v in command_info.get('_main', {}).items():
            setattr(parser, k, v)

    def parse(self, args, parser):
        subcommands = defaultdict(dict)

        for key, info in args.items():
            if key.startswith('_'):
                continue

            subcommand = info.pop('_subcommand', None)
            if subcommand:
                # handle a setting being applied to multiple subcommands
                if not isinstance(subcommand, list):
                    subcommand = [subcommand]

                for item in subcommand:
                    subcommands[item][key] = info

                continue

            _info = info.copy()

            # get the current value
            _val = getattr(self.settings, key, None)
            if _val:
                _info['default'] = _val

            if _info.pop('_positional', False):
                dashes = ''
            else:
                dashes = '--'

            arg = '{}{}'.format(dashes, key.lower().replace('_', '-'))
            if 'type' in _info:
                _type = _info['type']
                if '.' not in _type:
                    func = __builtins__[_type]
                else:
                    module_name, attr = _type.rsplit('.', 1)

                    module = import_module(module_name)

                    func = getattr(module, attr)
                    
                _info['type'] = func

            parser.add_argument(arg, **_info)

        command_info = args.get('_COMMANDS', {})

        if subcommands or command_info:
            self.subparsers = parser.add_subparsers(help='sub-commands')

        # go through all the args found for subcommands and create a subparser for them
        for subcommand, args in subcommands.items():
            kwargs = command_info.get(subcommand, {})
            subcommand_parser = self.subparsers.add_parser(subcommand, **kwargs)

            self.parse(args=args, parser=subcommand_parser)

            subcommand_parser.set_defaults(subcommand=subcommand)

        # check for any commands listed in command_info without additional settings
        for subcommand in set(command_info.keys()) - set(subcommands.keys()):
            kwargs = command_info[subcommand]
            subcommand_parser = self.subparsers.add_parser(subcommand, **kwargs)

            subcommand_parser.set_defaults(subcommand=subcommand)
