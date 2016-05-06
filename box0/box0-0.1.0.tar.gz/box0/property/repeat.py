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

from box0._binding import libbox0, ffi
from box0.property import Property, GetSetUInt32

class Repeat(Property, GetSetUInt32):
	"""
	Note: iteration return value that give the device supported count
			repeat infinite (0)
			arbitary(1) [uint32_t value is supported]
	whereas current get, set will set the values to device
	"""
	_info = libbox0.b0_repeat_info
	_cache_flush = libbox0.b0_repeat_cache_flush

	_set = libbox0.b0_repeat_set
	_get = libbox0.b0_repeat_get

	def __init__(self, prop):
		Property.__init__(self, prop)
		GetSetUInt32.__init__(self)
