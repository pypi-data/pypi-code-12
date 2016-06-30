# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from threading import local

_local = local()


class Gate(object):
    def __init__(self):
        self.local = local()

    def setup(self, *args, **kwargs):
        if hasattr(self.local, 'gate_registered_names'):
            raise RuntimeError('Gate already started.')

        self.local.gate_registered_names = set()

    def teardown(self):
        if not hasattr(self.local, 'gate_registered_names'):
            raise RuntimeError('Gate not started.')

        for name in self.local.gate_registered_names:
            delattr(self.local, name)
        delattr(self.local, 'gate_registered_names')

    def __call__(self, *args, **kwargs):
        self.setup(*args, **kwargs)
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.teardown()

    def attach(self, name, value):
        self.local.gate_registered_names.add(name)
        setattr(self.local, name, value)

    def contains(self, name):
        return name in self.local.gate_registered_names

    def retrieve(self, name):
        if not self.contains(name):
            raise ValueError('Property `{:s}` is not attached.'.format(
                name))
        return getattr(self.local, name)

    def release(self, name):
        self.local.gate_registered_names.remove(name)
        delattr(self.local, name)
