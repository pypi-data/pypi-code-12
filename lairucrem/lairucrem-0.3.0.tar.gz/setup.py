#! /usr/bin/env python
# Copyright (C) 2016 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/
"""Package metadata"""

from __future__ import unicode_literals
import os
import io
import re
from distutils.core import setup
try:
    import configparser
except ImportError: # python2 support
    import ConfigParser as configparser

# I do not want to document it :P
NO_SETUPTOOLS = os.environ.get('NO_SETUPTOOLS')
if not NO_SETUPTOOLS:
    import setuptools

# DRY: retrieve data from external files

def get_setup():
    """Read setup metadata from setup.cfg"""
    config = configparser.ConfigParser()
    config.read('setup.cfg')
    metadata = dict(config.items('setup'))
    metadata['keywords'] = [kw.strip()
                            for kw in re.split('[\n, ]*', metadata['keywords'])
                            if kw.strip()]
    metadata['classifiers'] = [kw.strip()
                               for kw in re.split('[\n,]*', metadata['classifiers'])
                               if kw.strip()]
    return metadata.items()


def get_descriptions():
    """Read descriptions from README"""
    config = configparser.ConfigParser()
    config.read('setup.cfg')
    with io.open(config.get('metadata', 'description-file').encode('utf-8'), 'r', encoding='utf-8') as readme:
        for line in readme:
            if line.strip() and not line.startswith(('..', '=')):
                description = line.strip()
                break
        readme.seek(0)
        long_description = readme.read()
    return [('description', description),
            ('long_description', long_description)]


def get_dependencies():
    """Read dependencies from requirements.txt"""
    install_requires = []
    if NO_SETUPTOOLS:
        return install_requires
    with open(b'requirements.txt', b'r',) as requirements:
        for line in requirements:
            line = line.strip()
            if not line or line.startswith('--'):
                continue
            install_requires.append(re.split('[<=!>]*', line)[0])
    return [('install_requires', install_requires)]


# In if statement to prevent py.test running it

if __name__ == '__main__':

    setup(
        scripts=[os.path.join(b'scripts', b'gh')],
        packages=[b'lairucrem', b'lairucrem.widgets'],
        **dict(
            get_descriptions() +
            get_dependencies() +
            get_setup()
        ))
