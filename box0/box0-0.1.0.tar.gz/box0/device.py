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

from box0._binding import libbox0, ffi, string_converter
from box0.exceptions import ResultException
from box0.module import Ain, Aout, Spi, I2c, Dio, Pwm, Unio, Module
from box0.generic import *

class ModulesIterator(object):
	"""
	Iterate over :class:box0.Device modules
	"""

	def __init__(self, dev):
		self._device = dev
		self._index = 0

	def __iter__(self):
		return ModulesIterator(self._device)

	def __next__(self):
		try: mod = self._device.modules[self._index]
		except IndexError: raise StopIteration
		self._index += 1
		return mod

	# python2 compatibility
	def next(self):
		return self.__next__()

class Modules(object):
	"""
	:class:box0.Device modules
	"""

	def __init__(self, dev):
		self._device = dev

	def __getitem__(self, index):
		"""
		Get the module at index

		:param int index: iterator index of module
		:rtype: box0.module.Module
		:return: un-instantiated module
		:raises TypeError: if cannot convert to integer value
		:raises IndexError: if index is out of range
		"""
		try: index = int(index)
		except: raise TypeError

		if (index >= 0) and (index < self._device._pointer.modules_len):
			mod = self._device._pointer.modules[index]
			class_map = {
				Module.DIO: Dio,
				Module.AOUT: Aout,
				Module.AIN: Ain,
				Module.SPI: Spi,
				Module.I2C: I2c,
				Module.PWM: Pwm,
				Module.UNIO: Unio
			}
			return Module(self._device, mod, class_map.get(mod.type))
		raise IndexError

	def __len__(self):
		return self._device._pointer.values_len

# not used Enum because Enum has different behaviour on python2 and python3
class LogLevel:
	"""
	Device log level

	Log level can be overriden by enviroment variable "LIBBOX0_LOG"

	LIBBOX0_LOG accept ("0", "1", "2", "3", "4", "none", "error", "warn", "info", "debug")
	"""

	DEBUG = libbox0.B0_LOG_DEBUG
	"""Debug log + INFO"""

	INFO = libbox0.B0_LOG_INFO
	"""Informational log + WARN"""

	WARN = libbox0.B0_LOG_WARN
	"""Warning log + ERROR"""

	ERROR = libbox0.B0_LOG_ERROR
	"""Error log only"""

	NONE = libbox0.B0_LOG_NONE
	"""No log"""

class Device(Box0, Close, Info):
	"""
	Box0 Device

	.. warning::
		Do not try to instantiate :class:`box0.Device`, instead use a backend (for example :class:`box0.usb.Usb`) to get a device, see the below code.

	.. code-block:: python

		import box0
		try:
			# open device
			dev = box0.usb.open_supported()

			# device information
			printf("Name: %s" % dev.name)
			printf("Manufacturer: %s" % dev.manuf)
			printf("Serial: %s" % dev.serial)

			# contained modules information
			for m in dev:
				print("Found: %s", m.name)

			# close device
			dev.close()
		except ResultException, e:
			print("failed! (%s)" % e)
	"""

	_info = libbox0.b0_device_info
	_log = libbox0.b0_device_log
	_close = libbox0.b0_device_close

	_ping = libbox0.b0_device_ping

	name = None
	"""Printable device name"""

	manuf = None
	"""Printable manufacturer name"""

	serial = None
	"""Printable serial number"""

	modules = None
	"""
	Modules contained in the device.

	collection of :class:`box0.module.Module`

	:type: box0.device.ModuleIterator

	.. tip::
		:class:`box0.Device` is iterable and return modules one by one
	"""

	def __init__(self, dev):
		"""
		Create a Device object from b0_device

		:param dev: libbox0 device
		:type dev: b0_device*
		"""
		Box0.__init__(self, dev)
		self.name = string_converter(self._pointer.name)
		self.manuf = string_converter(self._pointer.manuf)
		self.serial = string_converter(self._pointer.serial)
		self.modules = Modules(self)

	def __iter__(self):
		"""
		Iterate over the contained module

		:return: modules
		:rtype: box0.device.ModuleIterator
		"""
		return ModulesIterator(self)

	def log(self, log_level):
		"""
		Set debug level for device

		:param LogLevel log_level: Log level of device
		:raises ResultException: if libbox0 return negative result code
		"""
		log_level = int(log_level)
		ResultException.act(self._log(self._pointer, log_level))

	def ain(self, index = 0):
		"""
		Shorthand for :class:`box0.module.Ain(this-device, index)`

		:param int index: Module index
		:return: the opened module
		:rtype: box0.module.Ain
		"""
		return Ain(self, index)

	def aout(self, index = 0):
		"""
		Shorthand for :class:`box0.module.Aout(this-device, index)`

		:param int index: Module index
		:return: the opened module
		:rtype: box0.module.Aout
		"""
		return Aout(self, index)

	def pwm(self, index = 0):
		"""
		Shorthand for :class:`box0.module.Pwm(this-device, index)`

		:param int index: Module index
		:return: the opened module
		:rtype: box0.module.Pwm
		"""
		return Pwm(self, index)

	def dio(self, index = 0):
		"""
		Shorthand for :class:`box0.module.Dio(this-device, index)`

		:param int index: Module index
		:return: the opened module
		:rtype: box0.module.Dio
		"""
		return Dio(self, index)

	def spi(self, index = 0):
		"""
		Shorthand for :class:`box0.module.Spi(this-device, index)`

		:param int index: Module index
		:return: the opened module
		:rtype: box0.module.Spi
		"""
		return Spi(self, index)

	def i2c(self, index = 0):
		"""
		Shorthand for :class:`box0.module.I2c(this-device, index)`

		:param int index: Module index
		:return: the opened module
		:rtype: box0.module.I2c
		"""
		return I2c(self, index)

	def ping(self):
		"""
		If no exceptions are raised,
		then it can be assured that the device is connected, and running properly.

		:raises ResultException: if libbox0 return negative result code
		"""
		ResultException.act(self._ping(self._pointer))

	def __str__(self):
		return self.name


#implementation note:
# instead of confusing user with dev[0] ... to get module,
# the dev object is iterable (using __next__) as well as
#      dev.module is also a iterable object  (using __getitem__)
