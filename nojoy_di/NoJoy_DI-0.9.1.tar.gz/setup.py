#!/usr/bin/python
# -*- coding: utf-8 -*-
# NoJoy_DI (c) 2016 by Andre Karlsson<andre.karlsson@protractus.se>
#
# This file is part of NoJoy_DI.
#
#    NoJoy_DI is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    NoJoy_DI is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with NoJoy_DI.  If not, see <http://www.gnu.org/licenses/>.
#
#
# Filename: setup by: andrek
# Timesamp: 2016-05-26 :: 11:00
import os
from setuptools import setup
import re
import os
import sys

root_dir = os.path.realpath(os.path.dirname(__file__))
with open("%s/NoJoy_DI/__init__.py" % root_dir, "rt") as f:
    _version = re.search(r'__version__\s*=\s*"([^"]+)"', f.read()).group(1)

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "NoJoy_DI",
	version = _version,
	author = "Andre Karlsson",
	author_email = "andre@sess.se",
	description = "A simple and feature full Dependency Injector for python",
	license = "GPLv3",
	keywords = "DI dependency injection ioc",
	url = "https://github.com/joyider/NoJoy_DI",
	packages = ['NoJoy_DI'],
	long_description = read('README.md'),
	classifiers = [
		"Development Status :: 4 - Beta",
		"Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
		"Programming Language :: Python",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: 3.3",
		"Programming Language :: Python :: 3.4",
		"Programming Language :: Python :: 3.5",
	],
)