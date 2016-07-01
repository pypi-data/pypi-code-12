#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module: bootstrap.py
Author: zlamberty
Created: 2016-01-20

Description:
    a collection of bootstrap commands

Usage:
    <usage>

"""

import argparse as _argparse
import os as _os
import yaml as _yaml

# ----------------------------- #
#   Module Constants            #
# ----------------------------- #

_HERE = _os.path.realpath(_os.path.dirname(__file__))
_FCONF = _os.path.join(_HERE, 'config', 'eriproj.yaml')


# ----------------------------- #
#   Main routine                #
# ----------------------------- #

def _load_dirstruct(fconfig=_FCONF):
    with open(fconfig, 'rb') as f:
        return _yaml.load(f)


def _touch_init(path):
    initpath = _os.path.join(path, '__init__.py')
    print(initpath)
    with open(initpath, 'a') as f:
        _os.utime(initpath, None)

def _makedirz(d):
    try:
        _os.makedirs(d)
    except OSError:
        pass
    except:
        raise


def _makedir_from_node(node, root, withInit=False):
    if isinstance(node, str):
        d = _os.path.join(root, node)
        _makedirz(d)

        if withInit:
            _touch_init(d)
    elif isinstance(node, list):
        for subnode in node:
            _makedir_from_node(subnode, root, withInit)
    elif isinstance(node, dict):
        for (subdir, subnode) in node.items():
            _makedir_from_node(subdir, root, withInit)
            _makedir_from_node(subnode, _os.path.join(root, subdir), withInit)


def eri_pyproj(rootdirname, fconfig=_FCONF, withInit=False):
    """ set up an ERI project according to the pre-set template """
    dirstruct = _load_dirstruct(fconfig)
    _makedir_from_node(dirstruct, rootdirname, withInit)


def main():
    args = _parse_args()
    eri_pyproj(
        rootdirname=args.root,
        fconfig=args.fconfig,
        withInit=args.withinit,
    )


# ----------------------------- #
#   Command line                #
# ----------------------------- #

def _parse_args():
    """ Take a log file from the commmand line """
    parser = _argparse.ArgumentParser()

    root = "the root directory in which you plan on building your ERI project"
    parser.add_argument("-r", "--root", help=root, default=_os.getcwd())

    fconf = "yaml config file indicating what the dir structure should be"
    parser.add_argument("-f", "--fconf", help=fconf, default=_FCONF)

    withinit = "touch __init__.py files (for python projects)"
    parser.add_argument("-i", "--withinit", help=withinit, action='store_true')

    args = parser.parse_args()

    return args


if __name__ == '__main__':
    main()
