#
# This file is part of pyBox0.
# Copyright (C) 2016 Kuldeep Singh Dhaka <kuldeepdhaka9@gmail.com>
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

from box0.generic import *

class Driver(Box0, Close, Info):
	"""
	Box0 Driver

	.. warning::
	Do not instanciate this class directly, instead go for a driver like ADXL345
	"""

	_info = None
	_close = None

	def __init__(self, pointer, module):
		Box0.__init__(self, pointer)
		self._module = module

	@property
	def module(self):
		return self._module

	def close(self):
		Close.close(self)
		self._module = None
