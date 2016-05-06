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
from box0.property import Ref, I2cVersion, Label, Buffer
import numpy as np

class I2c(ModuleInstance, Bus):
	_info = libbox0.b0_i2c_info
	_open = libbox0.b0_i2c_open
	_close = libbox0.b0_i2c_close
	_cache_flush = libbox0.b0_i2c_cache_flush

	_read = libbox0.b0_i2c_read
	_write = libbox0.b0_i2c_write
	_write8_read = libbox0.b0_i2c_write8_read
	_slave_id = libbox0.b0_i2c_slave_id
	_slave_detect = libbox0.b0_i2c_slave_detect
	_start = libbox0.b0_i2c_start
	_start_out = libbox0.b0_i2c_start_out
	_stop = libbox0.b0_i2c_stop

	def __init__(self, dev, index):
		ModuleInstance.__init__(self, dev, index, "b0_i2c**")
		self.ref = Ref(self._pointer.ref)
		self.version = I2cVersion(self._pointer.version)
		self.label = Label(self._pointer.label)
		self.buffer = Buffer(self._pointer.buffer)

	def slave_id(self, slaveAddress):
		"""
		return (manufacturer, part, revision)
		"""
		manuf = ffi.new("uint16_t*")
		part = ffi.new("uint16_t*")
		rev = ffi.new("uint8_t*")
		ResultException.act(self._slave_id(self._pointer, slaveAddress, manuf, part, rev))
		return manuf[0], part[0], rev[0]
