# This file is part of the Online Services test tools
#
# Copyright 2013, 2014, 2015 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3, as published by the
# Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
# SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

import setuptools
import sys


import olstests


def get_scripts():
    if sys.version_info < (3,):
        return ['ols-run-tests2']
    else:
        return ['ols-run-tests']


setuptools.setup(
    name='olstests',
    version='.'.join(str(c) for c in olstests.__version__[0:3]),
    description=('Online Services test tools.'),
    author='Vincent Ladeuil',
    author_email='vila+ols@canonical.com',
    url='https://launchpad.net/ols-tests',
    license='GPLv3',
    install_requires=['pep8', 'pyflakes', 'python-subunit', 'testtools'],
    packages=['olstests', 'olstests.tests'],
    scripts=get_scripts(),
)
