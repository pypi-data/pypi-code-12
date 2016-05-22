# -*- coding: utf-8 -*-
# :Project:   metapensiero.tool.tinject -- Automate creation of sources
# :Created:   Wed 13 Apr 2016 11:22:34 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
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
    name="metapensiero.tool.tinject",
    version=VERSION,
    url="https://bitbucket.org/lele/metapensiero.tool.tinject",

    description="Automate creation of sources",
    long_description=README + u'\n\n' + CHANGES,

    author="Lele Gaifax",
    author_email="lele@metapensiero.it",

    license="GPLv3+",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Utilities",
        ],
    keywords="YAML, Jinja2, scaffolding, skeleton",

    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['metapensiero', 'metapensiero.tool'],

    install_requires=[
        'inquirer >= 2.1.7',
        'jinja2',
        'jinja2-time',
        'pyyaml',
        'setuptools',
    ],
    extras_require={'dev': ['metapensiero.tool.bump_version', 'readme']},

    entry_points="""\
    [console_scripts]
    tinject = metapensiero.tool.tinject.__main__:main
    """,
)
