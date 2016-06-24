# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from os import path
from poort.utils import environ_from_dict
import yaml

HERE = path.abspath(path.dirname(__file__))


def _load_environ(name):
    with open(path.join(HERE, 'environs', name + '.yaml')) as stream:
        return yaml.safe_load(stream)


def get_environ(name):
    if name == 'base':
        environ = _load_environ('base')
    else:
        environ = _load_environ('base')
        environ.update(_load_environ(name))

    return environ_from_dict(environ)
