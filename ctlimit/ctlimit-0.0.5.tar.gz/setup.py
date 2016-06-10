#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 Esther Kruis and Anselm Kruis
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA


# Always prefer setuptools over distutils
from setuptools import setup
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Get the version from the Sphinx configuration file
version = '0.0.0'
with open(path.join(here, 'ctlimit', '__init__.py'), encoding='utf-8') as f:
    for line in f:
        if line.startswith('__version__ = '):
            exec(line.replace("__version__", "version"))
            break

setup(
    name='ctlimit',

    # Versions should comply with PEP440.
    version=version,

    description='Computer Time Limit for Children',
    long_description=long_description,

    # The project's main homepage.
    url='https://bitbucket.org/akruis/ctlimit',

    # Author details
    author='Esther and Anselm Kruis',
    author_email='ctlimit@kruis.de',

    # Choose your license
    license='LGPLv2+',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: German',
        'Topic :: Desktop Environment',
        'Topic :: Utilities',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        # It's a daemon
        'Environment :: No Input/Output (Daemon)',
        'Operating System :: POSIX :: Linux',
    ],

    # What does your project relate to?
    keywords='desktop parental-control',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=['ctlimit', 'ctlimit.spi'],

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['pydbus >= 0.5.1', 'sdnotify >= 0.3'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': ['sphinx', 'fixtures'],
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        'ctlimit': ['ctlimit.conf', 'ctlimit_default.conf', 'ctlimit.service', 'de.kruis.ctlimit1.conf', 'logout_X11.bash'],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'ctlimitd=ctlimit:main',
            ],
    },
)
