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
from box0.module import ModuleInstance
from box0.property import Ref, Count, Capab, Label

class Pin:
	def __init__(self, module, index):
		self.module = module
		self.index = index

	@property
	def value(self):
		"""pin value"""
		return self.module.value_get(self.index)

	@value.setter
	def value(self, value):
		self.module.value_set(self.index, value)

	@property
	def dir(self):
		"""pin direction"""
		return self.module.dir_get(self.index)

	@dir.setter
	def dir(self, value):
		self.module.dir_set(self.index, value)

	@property
	def hiz(self):
		"""pin High Impedence"""
		return self.module.hiz_get(self.index)

	@hiz.setter
	def hiz(self, value):
		self.module.hiz_set(self.index, value)

	def toggle(self):
		"""toggle pin"""
		self.module.value_toggle(self.index)

	def input(self):
		"""
		pin into input direction
		same as `<pin>.dir = Dio.INPUT`
		"""
		self.dir = self.module.INPUT

	def output(self):
		"""
		pin into output directon
		same as `<pin>.dir = Dio.OUTPUT`
		"""
		self.dir = self.module.OUTPUT

	def high(self):
		"""
		pin value to high
		same as `<pin>.value = Dio.HIGH`
		"""
		self.value = self.module.HIGH

	def low(self):
		"""
		pin value to low
		same as `<pin>.value = Dio.LOW`
		"""
		self.value = self.module.LOW

	def enable(self):
		"""
		Enable pin for use
		same as `<pin>.hiz = Dio.DISABLE`
		"""
		self.hiz = self.module.DISABLE

	def disable(self):
		"""
		Disable the pin
		same as `<pin>.hiz = Dio.ENABLE`
		"""
		self.hiz = self.module.ENABLE

#TODO: multiple and all pin methods

class Dio(ModuleInstance):
	"""

	.. code-block:: python

		# ....
		# open a device (see box0.Device)
		# ....

		try:
			# open DIO index=0
			dio0 = dev.dio()

			# prepare for static mode
			dio0.static_prepare()

			# turn pin 0 to high
			pin0 = dio0.pin(0)
			pin0.enable()
			pin0.output()
			pin0.high()

	.. todo:

		add support for multiple and all operation
	"""
	_info = libbox0.b0_dio_info
	_cache_flush = libbox0.b0_dio_cache_flush
	_close = libbox0.b0_dio_close
	_open = libbox0.b0_dio_open

	_static_prepare = libbox0.b0_dio_static_prepare

	_value_get = libbox0.b0_dio_value_get
	_value_set = libbox0.b0_dio_value_set
	_value_toggle = libbox0.b0_dio_value_toggle
	_dir_set = libbox0.b0_dio_dir_set
	_dir_get = libbox0.b0_dio_dir_get
	_hiz_set = libbox0.b0_dio_hiz_set
	_hiz_get = libbox0.b0_dio_hiz_get

	_multiple_value_set = libbox0.b0_dio_multiple_value_set
	_multiple_value_get = libbox0.b0_dio_multiple_value_get
	_multiple_value_toggle = libbox0.b0_dio_multiple_value_toggle
	_multiple_dir_set = libbox0.b0_dio_multiple_dir_set
	_multiple_dir_get = libbox0.b0_dio_multiple_dir_get
	_multiple_hiz_get = libbox0.b0_dio_multiple_hiz_get
	_multiple_hiz_set = libbox0.b0_dio_multiple_hiz_set

	_all_value_set = libbox0.b0_dio_all_value_set
	_all_value_get = libbox0.b0_dio_all_value_get
	_all_value_toggle = libbox0.b0_dio_all_value_toggle
	_all_dir_set = libbox0.b0_dio_all_dir_set
	_all_dir_get = libbox0.b0_dio_all_dir_get
	_all_hiz_get = libbox0.b0_dio_all_hiz_get
	_all_hiz_set = libbox0.b0_dio_all_hiz_set

	_LOW = libbox0.B0_DIO_LOW
	_HIGH = libbox0.B0_DIO_HIGH
	_OUTPUT = libbox0.B0_DIO_OUTPUT
	_INPUT = libbox0.B0_DIO_INPUT
	_ENABLE = libbox0.B0_DIO_ENABLE
	_DISABLE = libbox0.B0_DIO_DISABLE

	LOW = False
	"""Low (Value)"""
	HIGH = True
	"""High (Value)"""

	OUTPUT = True
	"""Output (Direction)"""
	INPUT = False
	"""Input (Direction)"""

	ENABLE = True
	"""Enable (High Impedence)"""
	DISABLE = False
	"""Disable (High Impedence)"""

	ref = None
	"""Reference :class:`box0.property.Ref`"""

	capab = None
	"""Capabilities :class:`box0.property.Capab`"""

	count = None
	"""Number of pins :class:`box0.property.Count`"""

	label = None
	"""Label for pins :class:`box0.property.Label`"""

	def static_prepare(self):
		"""
		Prepare for static mode

		:raises ResultException: if libbox0 return negative result code
		"""
		ResultException.act(self._static_prepare(self._pointer))

	def __init__(self, dev, index):
		ModuleInstance.__init__(self, dev, index, "b0_dio**")
		self.ref = Ref(self._pointer.ref)
		self.capab = Capab(self._pointer.capab)
		self.count = Count(self._pointer.count)
		self.label = Label(self._pointer.label)

	def pin(self, index):
		"""
		return a :class:`box0.module.dio.Pin`
		"""
		if (index >= 0) and (index < self._pointer.count.value):
			return Pin(self, index)
		raise IndexError

	def value_get(self, index):
		"""
		get pin *index* value

		:param int index: pin number
		:return: True for High, False for Low
		:rtype: bool
		:raises ResultException: if libbox0 return negative result code
		"""
		value_ptr = ffi.new("bool*")
		ResultException.act(self._value_get(self._pointer, index, value_ptr))
		return (value_ptr[0] != self._LOW)

	def value_set(self, index, value):
		"""
		set pin *index* value to *value*

		:param int index: pin number
		:param bool value: pin value, True for High, False for Low
		:raises ResultException: if libbox0 return negative result code
		"""
		value = self._HIGH if value else self._LOW
		ResultException.act(self._value_set(self._pointer, index, value))

	def dir_get(self, index):
		"""
		get pin *index* direction

		:param int index: pin number
		:return: True on Output, False on Input
		:raises ResultException: if libbox0 return negative result code
		"""
		dir_ptr = ffi.new("bool*")
		ResultException.act(self._dir_get(self._pointer, index, dir_ptr))
		return (dir_ptr[0] != self._INPUT)

	def dir_set(self, index, value):
		"""
		set pin *index* direction

		:param int index: pin number
		:param bool value: False = Input, True = Output
		:raises ResultException: if libbox0 return negative result code
		"""
		value = self._OUTPUT if value else self._INPUT
		ResultException.act(self._dir_set(self._pointer, index, value))

	def value_toggle(self, index):
		"""
		toggle pin *index* value

		:param int index: pin number
		:raises ResultException: if libbox0 return negative result code
		"""
		ResultException.act(self._value_toggle(self._pointer, index))

	def hiz_get(self, index):
		"""
		get pin *index* high impedence value

		:param int index: pin number
		:return: True on Enabled, False on Disabled
		:rtype: bool
		:raises ResultException: if libbox0 return negative result code
		"""
		hiz_ptr = ffi.new("bool*")
		ResultException.act(self._hiz_get(self._pointer, index, hiz_ptr))
		return (hiz_ptr[0] != self._DISABLE)

	def hiz_set(self, index, value):
		"""
		set pin *index* high impedence to *value*

		:param int index: pin number
		:param bool value: True = Enable, False = Disable
		:raises ResultException: if libbox0 return negative result code
		"""
		value = self._ENABLE if value else self._DISABLE
		ResultException.act(self._hiz_set(self._pointer, index, value))

	def multiple_value_set(self, pins, value):
		"""
		set multiple *pins* state to *value*

		:param list/tuple index: pins number
		:param bool value: True = Enable, False = Disable
		:raises ResultException: if libbox0 return negative result code
		"""
		value = self._HIGH if value else self._LOW
		ResultException.act(self._multiple_value_set(self._pointer,
			ffi.new("uint8_t []", pins), len(pins), value))

	def multiple_value_get(self, pins):
		"""
		get multiple *pins* state

		:param list/tuple index: pins number
		:return: array of value (in the pins order)
		:raises ResultException: if libbox0 return negative result code
		"""
		values = ffi.new("bool []", len(pins))
		ResultException.act(self._multiple_value_get(self._pointer,
			ffi.new("uint8_t []", pins), values, len(pins)))
		return [i != self._LOW for i in values]

	def multiple_value_toggle(self, pins):
		"""
		toggle multiple *pins* value

		:param int pins: pins number
		:raises ResultException: if libbox0 return negative result code
		"""
		ResultException.act(self._multiple_value_toggle(self._pointer,
			ffi.new("uint8_t []", pins), len(pins)))

	def multiple_dir_set(self, pins, value):
		"""
		set multiple *pins* direction to *value*

		:param list/tuple index: pins number
		:param bool value: True = Output, False = Input
		:raises ResultException: if libbox0 return negative result code
		"""
		value = self._OUTPUT if value else self._INPUT
		ResultException.act(self._multiple_dir_set(self._pointer,
			ffi.new("uint8_t []", pins), len(pins), value))

	def multiple_dir_get(self, pins):
		"""
		get multiple *pins* direction

		:param list/tuple index: pins number
		:return: array of dir (in the pins order)
		:raises ResultException: if libbox0 return negative result code
		"""
		values = ffi.new("bool []", len(pins))
		ResultException.act(self._multiple_dir_get(self._pointer,
			ffi.new("uint8_t []", pins), values, len(pins)))
		return [i != self._INPUT for i in values]

	def multiple_hiz_set(self, pins, value):
		"""
		set multiple *pins* hiz to *value*

		:param list/tuple index: pins number
		:param bool value: True = Enable, False = Disable
		:raises ResultException: if libbox0 return negative result code
		"""
		value = self._ENABLE if value else self._DISABLE
		ResultException.act(self._multiple_hiz_set(self._pointer,
			ffi.new("uint8_t []", pins), len(pins), value))

	def multiple_hiz_get(self, pins):
		"""
		get multiple *pins* hiz

		:param list/tuple index: pins number
		:return: array of hiz (in the pins order)
		:raises ResultException: if libbox0 return negative result code
		"""
		values = ffi.new("bool []", len(pins))
		ResultException.act(self._multiple_hiz_get(self._pointer,
			ffi.new("uint8_t []", pins), values, len(pins)))
		return [i != self._DISABLE for i in values]

	def all_value_set(self, value):
		"""
		set all pins value

		:param bool value: High if value = True, Low if value = False
		:raises ResultException: if libbox0 return negative result code
		"""
		value = self._HIGH if value else self._LOW
		ResultException.act(self._all_value_set(self._pointer, value))

	def all_value_get(self):
		"""
		get all pins direction

		:return: array of bool containing values
		:raises ResultException: if libbox0 return negative result code
		"""
		values = ffi.new("bool []", self.count.value)
		ResultException.act(self._all_value_get(self._pointer, values))
		return [i != self._LOW for i in values]

	def all_value_toggle(self):
		"""
		toggle all pins value

		:raises ResultException: if libbox0 return negative result code
		"""
		ResultException.act(self._all_value_toggle(self._pointer))

	def all_dir_set(self, value):
		"""
		set all pins direction

		:param bool value: Output if value = True, Input if value = False
		:raises ResultException: if libbox0 return negative result code
		"""
		value = self._OUTPUT if value else self._INPUT
		ResultException.act(self._all_dir_set(self._pointer, value))

	def all_dir_get(self):
		"""
		get all pins direction

		:return: array of bool containing directions
		:raises ResultException: if libbox0 return negative result code
		"""
		values = ffi.new("bool []", self.count.value)
		ResultException.act(self._all_dir_get(self._pointer, values))
		return [i != self._INPUT for i in values]

	def all_hiz_set(self, value):
		"""
		set all pins hiz

		:param bool value: Enable if value = True, Disable if value = False
		:raises ResultException: if libbox0 return negative result code
		"""
		value = self._ENABLE if value else self._DISABLE
		ResultException.act(self._all_hiz_set(self._pointer, value))

	def all_hiz_get(self):
		"""
		get all pins hiz

		:return: array of bool containing hiz
		:raises ResultException: if libbox0 return negative result code
		"""
		values = ffi.new("bool []", self.count.value)
		ResultException.act(self._all_hiz_get(self._pointer, values))
		return [i != self._DISABLE for i in values]
