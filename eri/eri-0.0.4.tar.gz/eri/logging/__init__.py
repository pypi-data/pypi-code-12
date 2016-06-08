#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
module: eri.logging
author: Zach Lamberty
created: 2016-03-08

Description:
    Basically, I always want to have my logger set up to be colorized. Here I am
    just monkeypatching logger.getLogger (from the std library) to have a
    default colorized formatter by default. Everything beyond that should behave
    just like the std logging module

Usage:
    import eri.logging as logging

    logger = logging.getLogger(__name__)
    logging.configure()

    for level in logging._LEVELS:
        getattr(logger, level)(level)

"""

import logging.config as _lconfig
import os as _os
import yaml as _yaml

from logging import *


_LEVELS = ['debug', 'info', 'warning', 'error', 'critical']
_YAML_FILE = _os.path.dirname(_os.path.realpath(__file__)) + "/default.yaml"


def configure():
    """load the dict config yaml file"""
    try:
        with open(_YAML_FILE, 'rb') as f:
            _lconfig.dictConfig(config=_yaml.load(f.read()))
    except IOError:
        print('failure to load logging config {}'.format(_YAML_FILE))
        raise
