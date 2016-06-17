#!/usr/bin/env python
from setuptools import setup

__author__ = 'Ben Kaehler'
__copyright__ = 'Copyright 2016, Ben Kaehler'
__credits__ = ['Ben Kaehler']
__license__ = 'GPLv3 or any later version'
__maintainer__ = 'Ben Kaehler'
__email__ = 'benjamin.kaehler@anu.edu.au'
__status__ = 'Development'
__version__ = '0.0.2'

short_description = 'MPI Utilities'
long_description = '''A CLI and library for running embarrassingly parallel '''
'''tasks using MPI'''

setup(
    name='mpiutils',
    version=__version__,
    author=__author__,
    author_email=__email__,
    description=short_description,
    long_description=long_description,
    platforms=['any'],
    license=__license__,
    keywords=['parallel', 'workflow', 'MPI'],
    packages=['mpiutils'],
    install_requires=['click'],
    extras_require={'mpi': 'mpi4py'},
    entry_points={
        'console_scripts': ['mpimap=mpiutils.mpimap:mpimap']
        }
    )
