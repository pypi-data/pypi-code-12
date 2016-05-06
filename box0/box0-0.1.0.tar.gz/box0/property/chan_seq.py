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
from box0.exceptions import ResultException
from box0.property import Property

class ChanSeq(Property):
	_info = libbox0.b0_chan_seq_info
	_cache_flush = libbox0.b0_chan_seq_cache_flush

	_get = libbox0.b0_chan_seq_get
	_set = libbox0.b0_chan_seq_set

	def __init__(self, prop):
		Property.__init__(self, prop)

	def get(self):
		data = numpy.empty(255, dtype=uint8)
		byte_len_ptr = ffi.new("size_t *")
		byte_len_ptr[0] = data.nbytes

		data_ptr = ffi.cast("uint8_t *", data.ctypes.data)
		ResultException.act(self._get(self._pointer, data_ptr, byte_len_ptr))

		byte_len = byte_len_ptr[0]
		assert(byte_len > 0)
		data.resize(byte_len)
		return data

	def set(self, value):
		buf = ffi.new("uint8_t []", value)
		ResultException.act(self._set(self._pointer, buf, len(value)))

	current = property(get, set)
