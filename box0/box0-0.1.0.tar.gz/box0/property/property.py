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

from box0.exceptions import ResultException
from box0._binding import ffi
from box0.generic import Box0, Cache, Info

"""
Abstract class
just, to keep out common code of property

Note:
it is expected that, self._{info, cache_flush, property}
	attributes will be added by sub class
"""

class Property(Box0, Cache, Info):
	def __init__(self, prop):
		Box0.__init__(self, prop)

class WithValue(object):
	@property
	def value(self):
		return self._pointer.value

class ValuesIterator(object):
	def __init__(self, prop):
		self._property = prop
		self._index = 0

	def __iter__(self):
		return ValuesIterator(self._property)

	def __next__(self):
		try: mod = self._property.values[self._index]
		except IndexError: raise StopIteration
		self._index += 1
		return mod

	# python2 compatibility
	def next(self):
		return self.__next__()

class Values(object):
	def __init__(self, prop):
		self._property = prop

	@staticmethod
	def _get_from_c(values, index):
		return values[index]

	def __getitem__(self, index):
		try: index = int(index)
		# something that we cannot convert to int (for indexing)
		except: raise TypeError

		if (index >= 0) and (index < self._property._pointer.values_len):
			return self._get_from_c(self._property._pointer.values, index)
		raise IndexError

	def __len__(self):
		return self._property._pointer.values_len

class WithValues(object):
	def __init__(self):
		self.values = Values(self)

	def __iter__(self):
		return ValuesIterator(self)

"""
Abstract class for reading get set values and iterating over values
"""
class GetSet(object):
	_value_type = None
	_get = None
	_set = None

	def set(self, value):
		ResultException.act(self._set(self._pointer, value))

	def get(self):
		value_ptr = ffi.new("%s *" % self._value_type)
		ResultException.act(self._get(self._pointer, value_ptr))
		return value_ptr[0]

	current = property(get, set)

class GetSetUInt8(GetSet):
	_value_type = "uint8_t"

class GetSetUInt32(GetSet):
	_value_type = "uint32_t"
