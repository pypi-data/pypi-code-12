# -*- coding: utf-8 -*-
# Guix Import Debian --- Import helper for GNU Guix
# Copyright © 2016 Hartmut Goebel <h.goebel@crazy-compilers.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages

version = "0.1"

with open('README.rst') as fh:
    long_description = fh.read()

setup(
    name="guix-import-debian",
    version=version,
    description="""Helper for converting Debian packages into Guix package definitions""",
    long_description=long_description,
    author="Hartmut Goebel",
    author_email='h.goebel@crazy-compilers.com',
    license="GPLv3+",
    packages=find_packages(),
    include_package_data=True,
    install_requires=['python-debian', 'numconv', 'requests',
                      'chardet', # required by python-debian but not declared there
                  ],
    url="https://gitlab.com/htgoebel/guix-import-debian",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        ],
    entry_points = {
        "console_scripts": [
            "guix-import-debian = guix_import_debian.__main__:debian",
        ],
    },
    )
