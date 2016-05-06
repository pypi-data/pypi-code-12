#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from configparser import ConfigParser
from collections import OrderedDict

class Pypirc(object):

    def __init__(self):
        self.path = os.path.join(os.path.expanduser('~'), '.pypirc')
        self.fh = open(self.path, 'r+')

    def create(self, username, password):
        config = self._build_config(username, password)
        config.write(self.fh)

    def get_body(self):
        body = ''
        if self.is_exists():
            for line in self.fh.readlines():
                body += line
        return body

    def is_exists(self):
        return os.path.exists(self.path)

    def _build_config(self, username, password):
        config = ConfigParser()
        config['distutils'] = {'index-servers': 'pypi'}
        config['pypi'] = OrderedDict((
            ('repository', 'https://pypi.python.org/pypi'),
            ('username', username),
            ('password', password),
        ))
        return config

    def __del__(self):
        self.fh.close()
