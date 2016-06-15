from __future__ import absolute_import

import logging
import os
import sys

import yaml

from .config import get_config_paths


class Settings(object):
    def __init__(self):
        self.logger = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        self.paths = []

        # after the first settings file is processed, new setting names are 
        # not allowed to be injected; only the values of existing names can
        # be overridden.  this is to avoid silly typos in override settings
        # and the default settings file distributed with the code should be
        # the comprehensive list of all settings
        self.settings = None

        # look for all config paths on the filesystem
        for settings_path in get_config_paths(filename='settings.yml'):
            if os.path.exists(settings_path):
                self.paths.append(settings_path)

                with open(settings_path, 'r') as fh:
                    data = yaml.load(fh)
                    if not data:
                        continue

                    for k, i in data.items():
                        v = i['default']

                        self.logger.debug('k={}, v={}'.format(k, v))

                        if self.settings and k not in self.settings:
                            raise ValueError('setting {} not in {}'.format(k, self.paths[0]))

                        setattr(self, k, v)

                self.settings = self.settings or data

        # look for environment variables that match settings keys
        for k in self.settings:
            if k in os.environ:
                v = os.environ[k]

                self.logger.debug('env k={}, v={}'.format(k, v))
                setattr(self, k, v)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, str(self.paths))
