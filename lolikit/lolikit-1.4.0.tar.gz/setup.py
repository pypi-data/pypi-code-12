#!/usr/bin/env python3
# coding=utf-8

#########################################################################
#  The MIT License (MIT)
#
#  Copyright (c) 2014~2015 CIVA LIN (林雪凡)
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files
#  (the "Software"), to deal in the Software without restriction, including
#  without limitation the rights to use, copy, modify, merge, publish,
#  distribute, sublicense, and/or sell copies of the Software, and to
#  permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#  CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#  TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##########################################################################

import sys

from setuptools import setup
import src.lolikit.info as info

if not sys.version_info >= (3, 4, 0):
    print("ERROR: You cannot install because python version < 3.4")
    sys.exit(1)


def get_data_files():
    if sys.platform.startswith('win'):
        return []
    else:
        return [
            ('/etc/bash_completion.d/', ['datafiles/lolikit.bash-completion'])]

setup(
    name=info.PROJECT_NAME,
    version=info.VERSION,
    author=info.AUTHOR,
    author_email=info.AUTHOR_EMAIL,
    license=info.LICENSE,
    url=info.PROJECT_URL,
    description=info.DESCRIPTION,
    long_description='''''',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Environment :: Console"],
    install_requires=['termcolor >= 1.1.0',
                      'Mako >= 1.0',
                      'bottle >= 0.12.0',
                      'CommonMark >= 0.6.4'],
    setup_requires=[],
    package_dir={'': 'src'},
    packages=['lolikit', 'lolikit.subcommands'],
    include_package_data=True,
    data_files=get_data_files(),
    entry_points={
        'console_scripts': ['loli = lolikit.cmdline:main'],
        'setuptools.installation': ['eggsecutable = lolikit.cmdline:main']
        },
    keywords='notes-manager',
)
