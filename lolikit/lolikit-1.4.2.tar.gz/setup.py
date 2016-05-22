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
import os

from setuptools import setup
from setuptools.command.install import install as _install
from pkg_resources import Requirement, resource_filename

import src.lolikit.info as info

if not sys.version_info >= (3, 4, 0):
    print("ERROR: You cannot install because python version < 3.4")
    sys.exit(1)


def _post_install(dir):
    if sys.platform.startswith('linux'):
        src_path = resource_filename(
            Requirement.parse(info.PROJECT_NAME),
            os.path.join(info.PROJECT_NAME,
                         "data", "completion", "lolikit.bash-completion"))
        dst_path = os.path.join(
            '/etc', 'bash_completion.d', 'lolikit.bash-completion')
        if os.path.exists(dst_path):
            os.remove(dst_path)
            try:
                os.symlink(src_path, dst_path)
            except:
                pass


class install(_install):
    def run(self):
        _install.run(self)
        self.execute(_post_install, (self.install_lib,),
                     msg="Running post install task")

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
    entry_points={
        'console_scripts': ['loli = lolikit.cmdline:main'],
        'setuptools.installation': ['eggsecutable = lolikit.cmdline:main']
        },
    keywords='notes-manager',
    cmdclass={'install': install},
)
