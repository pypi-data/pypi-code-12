"""
Copyright 2016 Gu Zhengxiong <rectigu@gmail.com>

This file is part of IntDump.

IntDump is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

IntDump is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with IntDump.  If not, see <http://www.gnu.org/licenses/>.
"""


from sys import argv
from os.path import join, dirname

from setuptools import setup, find_packages


PROGRAM_NAME = 'IntDump'
PACKAGE_NAME = PROGRAM_NAME.lower()

__author__ = 'Gu Zhengxiong'

my_dir = dirname(argv[0])
version_file = 'version.txt'
version_path = join(my_dir, PACKAGE_NAME, version_file)
with open(version_path) as stream:
    __version__ = stream.read().strip()

with open(join(my_dir, 'requirements.txt')) as stream:
    requirements = stream.read().splitlines()


setup(
    name=PROGRAM_NAME,
    version=__version__,
    packages=find_packages(),
    package_data={'intdump': [version_file]},
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'intdump={name}.main:main'.format(name=PACKAGE_NAME)
        ]
    },

    author=__author__,
    author_email='rectigu@gmail.com',
    description='Interpret binary files in some predefined manners.',
    license='GPL-3',
    keywords='Binary File, Data Interpretation, Integer Dumping',
    url='https://github.com/NoviceLive/' + PACKAGE_NAME,

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: '
        'GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.2',
    ]
)
