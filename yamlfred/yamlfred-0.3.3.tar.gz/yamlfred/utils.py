# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os.path
import plistlib
import datetime
import shutil
import tempfile
import contextlib
import os

import six

try:
    from collections import ChainMap
except ImportError:
    from chainmap import ChainMap


def merge_dicts(default, local):
    "merge nested dictionaries"
    return dict(ChainMap(local, default))


def remove_default(local, default):
    explicit = {}
    for key in local.keys():
        if isinstance(local[key], dict):
            if key in default:
                explicit[key] = remove_default(local[key], default[key])
            else:
                explicit[key] = local[key]
        else:
            if key in default and local[key] == default[key]:
                continue
            explicit[key] = local[key]
    return explicit


class TemporaryDirectory(object):

    def __enter__(self):
        self.name = tempfile.mkdtemp()
        return self.name

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self.name)


@contextlib.contextmanager
def cd(path):
    curdir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(curdir)


def translate_plist(obj):
    "translate plistlib objects into Python stdtypes"
    if isinstance(obj, plistlib._InternalDict):
        return {translate_plist(k): translate_plist(v)
                for k, v in obj.items()}
    elif isinstance(obj, list):
        return [translate_plist(elem) for elem in obj]
    elif isinstance(obj, datetime.datetime):
        return plistlib._dateToString(obj)
    else:
        return obj


def text_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


def text_constructor(loader, node):
    return six.text_type(loader.construct_scalar(node))


class Include(six.text_type):

    def __new__(cls, path):
        return six.text_type.__new__(cls, path)

    def __repr__(self):
        return "Include({})".format(self.path)


def include_representer(dumper, data):
    return dumper.represent_scalar('!include', '{}'.format(data))


def include_constructor(loader, node):
    filename = loader.construct_scalar(node)
    with open(filename, 'r') as f:
        data = f.read()
    return data
