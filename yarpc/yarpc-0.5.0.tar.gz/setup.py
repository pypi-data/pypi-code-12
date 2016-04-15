# Copyright (c) 2016 Uber Technologies, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import re

from setuptools import find_packages, setup

version = None
version_file = 'yarpc/__init__.py'

with open(version_file, 'r') as f:
    for line in f:
        m = re.match(r'^__version__\s*=\s*(["\'])([^"\']+)\1', line)
        if m:
            version = m.group(2)
            break

if not version:
    raise Exception(
        "Could not determine version number from %s" % version_file
    )

with open('README.md') as f:
    long_description = f.read()

setup(
    name='yarpc',
    version=version,
    description=(
        'YARPC for Python',
    ),
    long_description=long_description,
    author='Grayson Koonce',
    author_email='grayson@uber.com',
    url='https://github.com/yarpc/yarpc-python',
    packages=find_packages(exclude=['tests', 'tests.*']),
    license='MIT',
    install_requires=[
        'tornado>=4.2,<5',
        'thriftrw>=1.1,<2',
    ],
    extras_require={
        'sync': ['futures', 'threadloop>=1,<2'],
        'tchannel': ['tchannel>=0.21,<0.22'],
    }
)
