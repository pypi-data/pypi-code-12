#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import os

this_dir = os.path.dirname(__file__)
with open(os.path.join(this_dir, 'eatme/__init__.py'), 'r') as fd:
    PACKAGE_VERSION = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                                fd.read(), re.MULTILINE).group(1)

if not PACKAGE_VERSION:
    raise RuntimeError('Cannot find version information')

this_dir = os.path.dirname(__file__)
readme_filename = os.path.join(this_dir, 'README.rst')
requirements_filename = os.path.join(this_dir, 'requirements.txt')

PACKAGE_LONG_DESCRIPTION = ''
if os.path.exists(readme_filename):
    with open(readme_filename) as f:
        PACKAGE_LONG_DESCRIPTION = f.read()

with open(requirements_filename) as f:
    # Игнорируем комментарии,
    # пустые строки и пакеты из репозиториев (-e)
    PACKAGE_INSTALL_REQUIRES = [
        line.strip('\n') for line in f
        if not line.startswith('#') and not line.startswith('-e') and line.strip()
        ]

setup(
    name='eatme',
    version=PACKAGE_VERSION,
    author='Taras Drapalyuk',
    author_email='taras@drapalyuk.com',
    description='EatMe Utility',
    url='https://github.com/kulapard/eatme',
    long_description=PACKAGE_LONG_DESCRIPTION,
    packages=[
        'eatme',
    ],
    entry_points={
        'console_scripts': [
            'eatme = eatme.cli:EatMe.run',
        ],
    },
    install_requires=PACKAGE_INSTALL_REQUIRES,
)
