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

from box0._binding import libbox0, ffi
from box0.driver.driver import Driver
from box0.module import I2c
from box0.exceptions import ResultException

class Adxl345(Driver):
	"""
	ADXL345 (Accelerometer) Driver
	"""

	_power_up = libbox0.b0_adxl345_power_up
	_info = libbox0.b0_adxl345_info
	_read = libbox0.b0_adxl345_read
	_close = libbox0.b0_adxl345_close
	_open_i2c = libbox0.b0_adxl345_open_i2c

	def __init__(self, module, ALT_ADDRESS=False):
		func = {
			I2c: self._open_i2c,
		}.get(type(module))

		if func is None:
			raise Exception("Not a supported module [only I2C currently]")

		drv = ffi.new("b0_adxl345 **")
		ResultException.act(func(module._pointer, drv, bool(ALT_ADDRESS)))

		"""Cache the objects"""
		Driver.__init__(self, drv[0], module)

	def power_up(self):
		ResultException.act(self._power_up(self._pointer))

	def read(self):
		arr = ffi.new("double [3]")
		ResultException.act(self._read(self._pointer, arr+0 , arr+1, arr+2))
		return (arr[0], arr[1], arr[2])
