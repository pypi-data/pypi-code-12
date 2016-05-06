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
from box0.module import Spi
from box0.exceptions import ResultException

class Ads1220(Driver):
	"""
	ADS1220 (24bit Sigma Delta ADC) Driver
	"""

	_open = libbox0.b0_ads1220_open
	_close = libbox0.b0_ads1220_close
	_info = libbox0.b0_ads1220_info
	_read = libbox0.b0_ads1220_read

	_reset = libbox0.b0_ads1220_reset
	_start = libbox0.b0_ads1220_start
	_power_down = libbox0.b0_ads1220_power_down
	_gain_set = libbox0.b0_ads1220_gain_set
	_pga_bypass = libbox0.b0_ads1220_pga_bypass_set
	_vref_set = libbox0.b0_ads1220_vref_set
	_filter_set = libbox0.b0_ads1220_filter_set

	FILTER_NONE = libbox0.B0_ADS1220_FILTER_NONE
	FILTER_50HZ = libbox0.B0_ADS1220_FILTER_50HZ
	FILTER_60HZ = libbox0.B0_ADS1220_FILTER_60HZ
	FILTER_50HZ_60HZ = libbox0.B0_ADS1220_FILTER_50HZ_60HZ

	VREF_INTERNAL = libbox0.B0_ADS1220_VREF_INTERNAL
	VREF_REFP0_REFN0 = libbox0.B0_ADS1220_VREF_REFP0_REFN0
	VREF_REFP1_REFN1 = libbox0.B0_ADS1220_VREF_REFP1_REFN1
	VREF_AVDD_AVSS = libbox0.B0_ADS1220_VREF_AVDD_AVSS

	GAIN_1 = libbox0.B0_ADS1220_GAIN_1
	GAIN_2 = libbox0.B0_ADS1220_GAIN_2
	GAIN_4 = libbox0.B0_ADS1220_GAIN_4
	GAIN_8 = libbox0.B0_ADS1220_GAIN_8
	GAIN_16 = libbox0.B0_ADS1220_GAIN_16
	GAIN_32 = libbox0.B0_ADS1220_GAIN_32
	GAIN_64 = libbox0.B0_ADS1220_GAIN_64
	GAIN_128 = libbox0.B0_ADS1220_GAIN_128

	def __init__(self, module, bSS):
		assert(type(module) is Spi)
		drv = ffi.new("b0_ads1220 **")
		ResultException.act(self._open(module._pointer, drv, bSS))

		"""Cache the objects"""
		Driver.__init__(self, drv[0], module)

	def read(self):
		val = ffi.new("double [1]")
		ResultException.act(self._read(self._pointer, val))
		return val[0]

	def reset(self):
		ResultException.act(self._reset(self._pointer))

	def start(self):
		ResultException.act(self._start(self._pointer))

	def power_down(self):
		ResultException.act(self._start(self._pointer))

	@property
	def gain(self):
		raise Exception("Not implemented yet!")

	@gain.setter
	def gain(self, value):
		ResultException.act(self._gain_set(self._pointer, value))

	@property
	def pga_bypass(self):
		raise Exception("Not implemented yet!")

	@pga_bypass.setter
	def pga_bypass(self, value):
		ResultException.act(self._pga_bypass(self._pointer, value))

	@property
	def filter(self):
		raise Exception("Not implemented yet!")

	@pga_bypass.setter
	def filter(self, value):
		ResultException.act(self._filter_set(self._pointer, value))

	def _vref_getter(self):
		raise Exception("read Not implemented yet!")

	def _vref_setter(self, source, low=None, high=None):
		if source != self.VREF_INTERNAL and (low is None or high is None):
			raise Exception("low and high is required for external reference")

		ResultException.act(self._vref_set(self._pointer, source, low, high))

	def vref(self, source=None, low=None, high=None):
		if source is None: self._vref_getter()
		else: self._vref_setter(source, low, high)
