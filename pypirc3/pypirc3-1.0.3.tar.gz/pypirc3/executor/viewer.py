#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

class Viewer(object):

    def __init__(self, path):
        self.path = path

    def execute(self):
        msg = ''
        result = 0
        if not self._is_exists():
            msg = "Don't exists ~/.pypirc! See pypirc3 help, and create ~/.pypirc with pypirc3"
            return (result, msg)

        with open(self.path, 'r') as f:
            for line in f.readlines():
                msg += line
        return (result, msg)

    def _is_exists(self):
        return os.path.exists(self.path)
