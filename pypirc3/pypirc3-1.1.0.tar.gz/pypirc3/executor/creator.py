#!/usr/bin/env python
# -*- coding: utf-8 -*-

from configparser import ConfigParser
from collections import OrderedDict

class Creator(object):

    def __init__(self, path, username, password):
        self.path     = path
        self.username = username
        self.password = password

    def execute(self):
        msg = ''
        result = 0
        if self._is_empty():
            msg = 'error: username and password are required!'
            result = 1
            return (result, msg)

        config = self._build_config()
        with open(self.path, 'w') as f:
            config.write(f)
        msg = 'Created ~/.pypirc successfully!'
        return (result, msg)

    def _is_empty(self):
        return True if not (self.username and self.password) else False

    def _build_config(self):
        config = ConfigParser()
        config['distutils'] = {'index-servers': 'pypi'}
        config['pypi'] = OrderedDict((
            ('repository', 'https://pypi.python.org/pypi'),
            ('username', self.username),
            ('password', self.password),
        ))
        return config
