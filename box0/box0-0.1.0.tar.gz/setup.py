#
# This file is part of pyBox0.
# Copyright (C) 2014, 2015 Kuldeep Singh Dhaka <kuldeepdhaka9@gmail.com>
#
# pyBox0 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyBox0 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyBox0.  If not, see <http://www.gnu.org/licenses/>.
#

from setuptools import setup, find_packages
import os

def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
	name = "box0",
	version = "0.1.0",
	author = "Kuldeep Singh Dhaka",
	author_email = "kuldeepdhaka9@gmail.com",
	description = ("libbox0 Binding"),
	license = "GPLv3+",
	keywords = "box0 libbox0 daq",
	url = "http://madresistor.org/box0",
	long_description = read('README'),
	packages = find_packages(include='box0.*'),
	install_requires = ["cffi>=1.0.0", "numpy>=1.11.0"],
	classifiers = [
		'Development Status :: 3 - Alpha',
		'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
		'Topic :: Scientific/Engineering'
	]
)

