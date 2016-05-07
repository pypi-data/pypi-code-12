#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import os

from ec3.util import AttrDict
from ec3 import compat


class EnvDict(AttrDict):
    def __init__(self, defaults=None, **kwarg_defaults):
        defaults = defaults or {}
        self._defaults = {k: v for k, v in compat.iteritems(defaults)}
        self._defaults.update(kwarg_defaults)

    @staticmethod
    def _get_env(key):
        return os.getenv(key)

    def __getitem__(self, key):
        if not super(EnvDict, self).__contains__(key):
            val = self._get_env(key)
            if val is None:
                if key in self._defaults:
                    val = self._defaults[key]
                else:
                    raise KeyError(key)
            self[key] = val
        return super(EnvDict, self).__getitem__(key)

    def __contains__(self, key):
        if super(EnvDict, self).__contains__(key):
            return True
        return (key in self._defaults) or self._get_env(key) is not None
