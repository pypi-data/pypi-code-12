#!/usr/bin/env python
#
# Copyright (C) 2015 Martin Owens
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
import os
import sys

from setuptools import setup, find_packages

import autotest

# remove MANIFEST. distutils doesn't properly update it when the contents of directories change.
if os.path.exists('MANIFEST'): os.remove('MANIFEST')

with open('README') as fhl:
    README = fhl.read()

setup(
        name             = autotest.__pkgname__,
        version          = autotest.__version__,
        description      = autotest.__doc__,
        long_description = README,
        url              = 'https://github.com/doctormo/django-autotest',
        author           = 'Martin Owens',
        author_email     = 'doctormo@gmail.com',
        platforms        = 'linux',
        license          = 'LGPLv3',
        packages         = find_packages(),
        extras_require   = {'coverage': ['coverage>=4.0.3']},
        install_requires = [
          'django>=1.7.5',
        ],
    )

