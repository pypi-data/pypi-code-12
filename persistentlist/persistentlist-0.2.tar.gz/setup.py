# -*- coding: utf-8 -*-
# Copyright © 2016 Carl Chenet <carl.chenet@ohmytux.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

# Setup for persistentlist
'''Setup for persistentlist'''

# 3rd party libraries imports
from setuptools import setup

CLASSIFIERS = [
    'Intended Audience :: Developers',
    'Environment :: Console',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 3.4'
]

setup(
    name='persistentlist',
    version='0.2',
    license='GNU GPL v3',
    description='library providing a persistent list of n object',
    long_description='library providing a persistent list of n object, each n+1 object removing the first object in the list',
    classifiers=CLASSIFIERS,
    author='Carl Chenet',
    author_email='chaica@ohmytux.com',
    url='https://github.com/chaica/persistentlist',
    download_url='https://github.com/chaica/persistentlist',
    packages=['persistentlist']
)
