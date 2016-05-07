#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from pypirc3.option import *
from pypirc3.executor.creator import Creator
from pypirc3.executor.viewer import Viewer

class Pypirc(object):

    def __init__(self, action, username, password):
        path = self._build_path()

        if action == ACTION_CREATE:
            self.executor = Creator(path, username, password)
        else:
            self.executor = Viewer(path)

    def _build_path(self):
        return os.path.join(os.path.expanduser('~'), '.pypirc_test')

    def execute(self):
        return self.executor.execute()

