#!/usr/bin/env python3

import os.path
import re
import sys
import setuptools


if sys.version_info < (3, 2):
    raise RuntimeError('Python 3.2 or greater is required')


def relative_path(path):
    return os.path.join(os.path.dirname(__file__), path)


def long_description():
    with open(relative_path('README.rst')) as f:
        return f.read()


def from_init(name, default=None):
    with open(relative_path('haiker/__init__.py')) as f:
        for line in f:
            m = re.search('(^|\\s){0}\\s*=\\s*(.+)'.format(name), line)
            if m is not None:
                return eval(m.group(2))
    return default


setuptools.setup(
    name='hatena-haiker',
    version=from_init('__version__'),
    author=from_init('__author__'),
    author_email='saltcandy123+haiker@gmail.com',
    url='https://github.com/saltcandy123/hatena-haiker/',
    description='Hatena Haiku for Python 3',
    long_description=long_description(),
    license=from_init('__license__'),
    packages=['haiker'],
    install_requires=[
        'requests>=0',
        'requests-oauthlib>=0',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries',
    ],
    keywords='hatena haiku api',
)
