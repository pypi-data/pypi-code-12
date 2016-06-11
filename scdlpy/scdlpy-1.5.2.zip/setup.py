#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages

import scdl

setup(
    name='scdlpy',
    version=scdl.__version__,
    packages=find_packages(),
    author='DarkArtek',
    author_email='darkartek@gmail.com',
    description='Download Music from Souncloud',
    install_requires=[
        'docopt',
        'mutagen',
        'termcolor',
        'requests',
        'clint'
    ],
    url='https://bitbucket.org/DarkArtek/scdl',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet',
        'Topic :: Multimedia :: Sound/Audio',
    ],
    entry_points={
        'console_scripts': [
            'scdl = scdl.scdl:main',
        ],
    },
)
