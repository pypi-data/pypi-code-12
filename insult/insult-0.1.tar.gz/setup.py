#!/usr/bin/env python
#
# Copyright (C) 2016 Mattia Basaglia
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from distutils.core import setup

setup(
    name="insult",
    version="0.1",
    description="Python bindings to LibInsult",
    #long_description="",
    author="Mattia Basaglia",
    author_email="mattia.basaglia@gmail.com",
    url="http://mattbas.org/insult",
    package_dir = {'': 'lib'},
    py_modules=["insult"],
    scripts=["bin/insult"],
    license="GPLv3+",
    platforms=["any"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Topic :: Communications :: Chat",
        "Topic :: Utilities",
        "Operating System :: OS Independent",
    ],
)
