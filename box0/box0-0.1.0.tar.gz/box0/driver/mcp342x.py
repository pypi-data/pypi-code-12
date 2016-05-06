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

class Mcp342x(Driver):
	"""
	MCP342x (Sigma Delta ADC) Driver
	"""

	_open = libbox0.b0_mcp342x_open
	_close = libbox0.b0_mcp342x_close
	_info = libbox0.b0_mcp342x_info
	_chan_set = libbox0.b0_mcp342x_chan_set
	_gain_set = libbox0.b0_mcp342x_gain_set
	_samp_rate_set = libbox0.b0_mcp342x_samp_rate_set
	_read = libbox0.b0_mcp342x_read

	# Address state pin
	LOW = libbox0.B0_MCP342X_LOW
	FLOAT = libbox0.B0_MCP342X_FLOAT
	HIGH = libbox0.B0_MCP342X_HIGH

	# Channnel
	CH1 = libbox0.B0_MCP342X_CH1
	CH2 = libbox0.B0_MCP342X_CH2
	CH3 = libbox0.B0_MCP342X_CH3
	CH4 = libbox0.B0_MCP342X_CH4

	# Gain values
	GAIN1 = libbox0.B0_MCP342X_GAIN1
	GAIN2 = libbox0.B0_MCP342X_GAIN2
	GAIN4 = libbox0.B0_MCP342X_GAIN4
	GAIN8 = libbox0.B0_MCP342X_GAIN8

	def __init__(self, module, Adr1, Adr0):
		assert(type(module) is I2c)
		drv = ffi.new("b0_mcp342x **")
		ResultException.act(self._open(module._pointer, drv, Adr1, Adr0))

		"""Cache the objects"""
		Driver.__init__(self, drv[0], module)

	@property
	def chan(self):
		raise Exception("Not implemented yet!")

	@chan.setter
	def chan(self, value):
		ResultException.act(self._chan_set(self._pointer, value))

	@property
	def gain(self):
		raise Exception("Not implemented yet!")

	@gain.setter
	def gain(self, value):
		ResultException.act(self._gain_set(self._pointer, value))

	def read(self):
		val = ffi.new("double [1]")
		ResultException.act(self._read(self._pointer, val))
		return val[0]
