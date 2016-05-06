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
from box0._binding import libbox0, ffi, string_converter
from box0.generic import Box0, Close, Info, Cache
import numpy as np

class Module(Box0, Info):
	DIO = libbox0.B0_DIO
	AOUT = libbox0.B0_AOUT
	AIN = libbox0.B0_AIN
	SPI = libbox0.B0_SPI
	I2C = libbox0.B0_I2C
	PWM = libbox0.B0_PWM
	UNIO = libbox0.B0_UNIO

	_OK = libbox0.B0_OK
	_ERR_UNAVAIL = libbox0.B0_ERR_UNAVAIL

	_info = libbox0.b0_module_info
	_openable = libbox0.b0_module_openable

	index = None
	"""Module index"""

	type = None
	"""Module type"""

	name = None
	"""Printable name of type"""

	# instance_cls is required because of import error.
	#  instance class is passed (from external), and later Module.open()
	#  use this to open the instance module
	#  if the Module is not supported instance_cls=None is passed
	def __init__(self, dev, mod, instance_cls):
		Box0.__init__(self, mod)
		self.device = dev
		if hasattr(mod, 'header'):
			mod = mod.header

		self.index = mod.index
		self.type = mod.type
		self.name = string_converter(mod.name)
		self.instance_cls = instance_cls

	def open(self):
		if self.instance_cls is None:
			raise Exception("Module not supported")
		return self.instance_cls(self.device, self.index)

	def openable(self):
		"""
		Return true if the module is openable
		:return bool: result
		:raises ResultException: if libbox0 return negative result code
		"""
		r = self._openable(self._pointer)
		if r == self._OK:
			return True
		elif r == self._ERR_UNAVAIL:
			return False

		ResultException.act(r)

	def __str__(self):
		return self.name

class ModuleInstance(Module, Close, Cache):
	"""
	Abstract class
	just, to keep out common code of modules

	Note:
	it is expected that, self._{load, unload, info, cache_flush, module}
		attributes will be added by sub class
	"""
	_open = None

	def __init__(self, dev, index, cdefstr):
		"""Construct a b0_<module> object"""
		mod_ptr = ffi.new(cdefstr)
		ResultException.act(self._open(dev._pointer, mod_ptr, index))
		mod = mod_ptr[0]
		Module.__init__(self, dev, mod, None)

	def open(self):
		raise Exception("Module is a instance")

def np_dtype_map(dtype, float32, float64, void):
	if dtype == np.float32:
		return float32
	elif dtype == np.float64:
		return float64
	elif dtype == np.void:
		return void
	raise Exception("numpy memory type not supported, (hint: numpy.void)")
