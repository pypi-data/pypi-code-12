# Copyright (c) 2013-2016, Philippe Bordron <philippe.bordron+ufx@gmail.com>
# -*- encoding: utf-8 -*-
# This file is part of UFx.
#
# UFx is free software: you can redistribute it and/or modify
# it under the terms of the GNU LESSER GENERAL PUBLIC LICENSE as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# UFx is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU LESSER GENERAL PUBLIC LICENSE for more details.
#
# You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
# along with UFx.  If not, see <http://www.gnu.org/licenses/>

from setuptools import setup
from setuptools import find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='UFx',
    version='1.0',
    description='UFx is a pure python library that implements the disjoint-set data structure which allows the union-find operations.',
    long_description=readme(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Operating System :: OS Independent',
    ],
    author='Philippe Bordron',
    license='LGPL',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    zip_safe=False)
