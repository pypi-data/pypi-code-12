#!/usr/bin/env python

from wrenet import __version__
from setuptools import setup, find_packages

setup(
    name='wrenet',
    version=__version__,
    description='Network configurations viewer in the Windows Registry',
    author='graypawn',
    author_email='choi.pawn' '@gmail.com',
    url='https://github.com/graypawn/wrenet',
    license='Apache License (2.0)',
    packages=find_packages(),
    install_requires = {'python-registry >= 1.0.0'},
    classifiers = ["Programming Language :: Python",
                   "Programming Language :: Python :: 3",
                   "Operating System :: POSIX :: Linux",
                   "License :: OSI Approved :: Apache Software License"],
    entry_points={
        'console_scripts': [
            'wrenet=wrenet.__main__:main'
        ]
    }
)
