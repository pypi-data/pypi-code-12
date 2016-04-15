#!/usr/bin/env python3
#
# The MIT License (MIT)
#
# Copyright (c) 2016 Philippe Proulx <pproulx@efficios.com>
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

from setuptools import setup
import sys


def _check_python3():
  # make sure we run Python 3+ here
  v = sys.version_info

  if v.major < 3:
      sys.stderr.write('Sorry, lamiview needs Python 3\n')
      sys.exit(1)


_check_python3()


import lamiview


setup(name='lamiview',
      version=lamiview.__version__,
      description='LAMI viewer',
      author='Philippe Proulx',
      author_email='eeppeliteloop@gmail.com',
      license='MIT',
      keywords='lttng-analyses lami',
      url='https://github.com/eepp/lamiview',
      install_requires=[
          'Pygments',
          'setuptools',
      ],
      packages=[
          'lamiview',
      ],
      package_data={
          'lamiview': [
              'res/ui/*.ui',
          ]
      },
      entry_points={
          'console_scripts': [
              'lamiview = lamiview.app:run'
          ],
      })
