#!/usr/bin/env python
"""
 Licensed to the Apache Software Foundation (ASF) under one
 or more contributor license agreements.  See the NOTICE file
 distributed with this work for additional information
 regarding copyright ownership.  The ASF licenses this file
 to you under the Apache License, Version 2.0 (the
 "License"); you may not use this file except in compliance
 with the License.  You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
 Unless required by applicable law or agreed to in writing,
 software distributed under the License is distributed on an
 "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 KIND, either express or implied.  See the License for the
 specific language governing permissions and limitations
 under the License.
"""

# coding:utf-8
# Copyright (C) Alibaba Group


import edsd
from setuptools import setup, Command, find_packages

install_requires = [
    'termcolor==1.1.0'
]


def main():
    setup(
        name='edsd',
        description='A running environment detecting command line for aliyun EDAS',
        version=edsd.__version__,
        long_description=open("README.rst").read(),
        url='https://help.aliyun.com/document_detail/edas/quick-start/quick-start.html',
        packages=find_packages(),
        platforms=['unix', 'linux', 'osx', 'win64'],
        install_requires=install_requires,
        author='Thomas Li',
        author_email='yanliang.lyl@alibaba-inc.com',
        entry_points={
            'console_scripts': [
                'edsd = edsd.edsdmain:main_shell',
                'edsd-collect = edsd.edsdmain:collect'
            ]
        }
        # the following should be enabled for release
    )


if __name__ == '__main__':
    main()
