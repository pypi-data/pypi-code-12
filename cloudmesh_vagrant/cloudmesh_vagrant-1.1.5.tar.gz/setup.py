#!/usr/bin/env python
# ----------------------------------------------------------------------- #
# Copyright 2008-2010, Gregor von Laszewski                               #
# Copyright 2010-2013, Indiana University                                 #
# #
# Licensed under the Apache License, Version 2.0 (the "License"); you may #
# not use this file except in compliance with the License. You may obtain #
# a copy of the License at                                                #
#                                                                         #
# http://www.apache.org/licenses/LICENSE-2.0                              #
#                                                                         #
# Unless required by applicable law or agreed to in writing, software     #
# distributed under the License is distributed on an "AS IS" BASIS,       #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.#
# See the License for the specific language governing permissions and     #
# limitations under the License.                                          #
# ------------------------------------------------------------------------#
from __future__ import print_function

import setuptools
from setuptools import setup, find_packages
import os
import sys
from cloudmesh_vagrant import __version__
import platform

if sys.version_info < (2, 7, 10):
    print(70 * "#")
    print("WARNING: upgrade to python 2.7.10 or above"
          "Your version is {} not supported.".format(sys.version_info))
    print(70 * "#")

command = None
this_platform = platform.system().lower()
if this_platform in ['darwin']:
    command = "easy_install readline"
elif this_platform in ['windows']:
    command = "pip install pyreadline"

if command is not None:
    print("Install readline")
    os.system(command)

requirements = [
    'cloudmesh_client'
    ]


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


home = os.path.expanduser("~")


setup(
    version=__version__,
    name="cloudmesh_vagrant",
    description="cloudmesh_vagrant - A real simple interface to virtualbox via vagrant",
    long_description=read('README.rst'),
    license="Apache License, Version 2.0",
    author="Gregor von Laszewski",
    author_email="laszewski@gmail.com",
    url="https://github.com/cloudmesh/cloudmesh_vagrant",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.7",
        "Topic :: Scientific/Engineering",
        "Topic :: System :: Clustering",
        "Topic :: System :: Distributed Computing",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Console"
    ],
    keywords="cloud cmd commandshell plugins cloudmesh vagrant virtualbox",
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'cm-vbox = cloudmesh_vagrant.cm_vbox:main',
            'cm-authors = cloudmesh_client.common.GitInfo:print_authors',
        ],
    },
)
