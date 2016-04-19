# -*- coding: utf-8 -*-
# :Project:   metapensiero.sphinx.patchdb
# :Created:   sab 22 ago 2009 17:26:36 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2009, 2010, 2012, 2013, 2014, 2015, 2016 Lele Gaifax
#

from io import open
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst'), encoding='utf-8') as f:
    CHANGES = f.read()
with open(os.path.join(here, 'version.txt'), encoding='utf-8') as f:
    VERSION = f.read().strip()

setup(
    name='metapensiero.sphinx.patchdb',
    version=VERSION,
    description="Extract scripts from a reST document and apply them in order.",
    long_description=README + '\n\n' + CHANGES,

    author='Lele Gaifax',
    author_email='lele@metapensiero.it',
    url="https://bitbucket.org/lele/metapensiero.sphinx.patchdb",

    license="GPLv3+",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved ::"
        " GNU General Public License v3 or later (GPLv3+)",
        "Topic :: Database",
        "Framework :: Sphinx :: Extension",
        ],

    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['metapensiero', 'metapensiero.sphinx'],

    install_requires=[
        'PyYAML',
        'setuptools',
        'sqlalchemy',
        ],
    extras_require={'dev': ['readme', 'pygments', 'sphinx']},

    tests_require=[
        'docutils',
        'pytest',
        'pygments',
        'sphinx',
    ],
    test_suite='py.test',

    entry_points="""\
    [console_scripts]
    patchdb = metapensiero.sphinx.patchdb.pup:main
    patchdb-states = metapensiero.sphinx.patchdb.states:main
    """,
)
