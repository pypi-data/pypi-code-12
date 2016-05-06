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

from box0._binding import ffi, libbox0
from box0.exceptions import ResultException
from box0.module import ModuleInstance, Bus
from box0.property import Speed, Count, Ref, Buffer, Capab, Bitsize
import numpy as np

class Spi(ModuleInstance, Bus):
	_info = libbox0.b0_spi_info
	_open = libbox0.b0_spi_open
	_close = libbox0.b0_spi_close
	_cache_flush = libbox0.b0_spi_cache_flush

	_active_state_get = libbox0.b0_spi_active_state_get
	_active_state_set = libbox0.b0_spi_active_state_set

	_start = libbox0.b0_spi_start
	_start_out = libbox0.b0_spi_start_out
	_stop = libbox0.b0_spi_stop

	def __init__(self, dev, index):
		ModuleInstance.__init__(self, dev, index, "b0_spi**")
		self.speed = Speed(self._pointer.speed)
		self.count = Count(self._pointer.count)
		self.ref = Ref(self._pointer.ref)
		self.buffer = Buffer(self._pointer.buffer)
		self.capab = Capab(self._pointer.capab)
		self.bitsize = Bitsize(self._pointer.bitsize)

	def active_state(self, ss):
		value = ffi.new("bool")
		ResultException.act(self.active_state_get(self._pointer, ss, value))
		return (value[0] != 0)

	def active_state(self, ss, value):
		ResultException.act(self.active_state_set(self._pointer, ss, value))
