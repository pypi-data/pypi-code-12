#!/usr/bin/env python
# coding: utf-8
# File Name: setup.py
# Author: cissoid
# Created At: 2016-06-28T12:03:51+0800
# Last Modified: 2016-06-28T16:44:53+0800
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

import psychopass

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_requirements(requirement_file):
    requirements = []
    with open(os.path.join(ROOT_DIR, requirement_file), 'rb') as fp:
        for line in fp:
            line = line.strip()
            line and requirements.append(line.decode('utf8'))
    return requirements


class Tox(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox
        sys.exit(tox.cmdline(self.test_args))


setup(
    name='psychopass',
    version=psychopass.__version__,
    description='A Python password generator inspired by flowerpassword',
    long_description=open('README.rst').read(),
    url='https://github.com/cissoid/psychopass-python',
    author='cissoid',
    license='MIT',
    packages=['psychopass'],
    install_requires=get_requirements('requirements.txt'),
    tests_require=get_requirements('test_requirements.txt'),
    cmdclass={'test': Tox},
    entry_points={
        'console_scripts': [
            'psychopass = psychopass.psychopass:main',
        ],
    },
    classifiers=[
        # 'Development Status :: 2 - Pre-Alpha',
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Security',
        'Topic :: Security :: Cryptography',
        'Topic :: Terminals',
        'Topic :: Utilities',
    ]
)
