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
from box0.property import Property, WithValues
from box0.exceptions import ResultException
from box0.generic import Box0

class Value(Box0):
	speed = None
	"""get speed of stream speed value"""

	bitsize = None
	"""get bitsize of stream speed value"""

	def __init__(self, val):
		Box0.__init__(self, val)
		self.speed = val.speed
		self.bitsize = val.bitsize

	def __eq__(self, other):
		"""compare"""
		"note, self.__class__ return sub classs name"
		return  (self.__class__ == other.__class__) and \
				(self._pointer.bitsize == other._pointer.bitsize) and \
				(self._pointer.speed == other._pointer.speed)

def sv_get_from_c(values, index):
	return Value(values + index)

class Stream(Property, WithValues):
	_info = libbox0.b0_stream_info
	_cache_flush = libbox0.b0_stream_cache_flush
	_search = libbox0.b0_stream_search

	def __init__(self, prop):
		Property.__init__(self, prop)
		WithValues.__init__(self)
		self.values._get_from_c = sv_get_from_c

	def search(self, speed, bitsize):
		"""
		Search for a stream speed
		:param int speed: Speed
		:param int bitsize: Bitsize
		:return: Stream value
		:rtype: :class:`box0.property.stream.Value`
		:raises ResultException: if libbox0 return negative result code (except search failed)
		"""
		value = ffi.new("b0_stream_value**")
		r = self._search(self._pointer, value, speed, bitsize)
		if r == libbox0.B0_ERR_SEARCH:
			# not found
			return None
		elif r >= libbox0.B0_OK:
			return Value(value[0])

		ResultException.act(r)
