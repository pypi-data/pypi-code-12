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

from box0.module import ModuleInstance
from box0.exceptions import ResultException
from box0.property import Speed, Bitsize, Ref, Capab, Count, Label
from box0._binding import libbox0, ffi

class Width(object):
	"""
	A static class for reading writing width values
	as well as for iterating
	"""

	def __init__(self, mod):
		if not isinstance(mod, Pwm):
			raise Exception("not a Pwm type module")

		self._mod = mod

	def __getitem__(self, index):
		return self._mod._width_getter(index)

	def __setitem__(self, index, value):
		return self._mod._width_setter(index, value)

class Pwm(ModuleInstance):
	_cache_flush = libbox0.b0_pwm_cache_flush
	_info = libbox0.b0_pwm_info
	_close = libbox0.b0_pwm_close
	_open = libbox0.b0_pwm_open
	_width_get = libbox0.b0_pwm_width_get
	_width_set = libbox0.b0_pwm_width_set
	_period_set = libbox0.b0_pwm_period_set
	_period_get = libbox0.b0_pwm_period_get
	_set = libbox0.b0_pwm_set
	_calc = libbox0.b0_pwm_calc
	_start = libbox0.b0_pwm_start
	_stop = libbox0.b0_pwm_stop

	def __init__(self, dev, index):
		ModuleInstance.__init__(self, dev, index, "b0_pwm**")

		self.speed = Speed(self._pointer.speed)
		self.bitsize = Bitsize(self._pointer.bitsize)
		self.ref = Ref(self._pointer.ref)
		self.capab = Capab(self._pointer.capab)
		self.count = Count(self._pointer.count)
		self.label = Label(self._pointer.label)

	def set(self, ch, freq, duty_cycle = 50.0, error = 100.0):
		freq_ptr = ffi.new("double*")
		freq_ptr[0] = freq

		duty_cycle_ptr = ffi.new("double*")
		duty_cycle_ptr[0] = duty_cycle

		error_ptr = ffi.new("double*")
		error_ptr[0] = error

		result = self._set(self._pointer, ch, freq_ptr, duty_cycle_ptr, error_ptr)
		ResultException.act(result)

		# return (calc-freq, duty-cycle, calc-error)
		return (freq_ptr[0], duty_cycle_ptr[0], error_ptr[0])

	def calc(self, freq, error = 100.0):
		speed_ptr = ffi.new("uint32_t*")
		period_ptr = ffi.new("b0_pwm_reg*")

		result = self._calc(self._pointer, freq, error, speed_ptr, period_ptr)
		ResultException.act(result)

		return (speed_ptr[0], period_ptr[0])

	def start(self):
		ResultException.act(self._start(self._pointer))

	def stop(self):
		ResultException.act(self._stop(self._pointer))

	@property
	def period(self):
		val_ptr = ffi.new("b0_pwm_reg*")
		ResultException.act(self._stream_start(self._pointer, val_ptr))
		return val_ptr[0]

	@period.setter
	def period(self, value):
		ResultException.act(self._period_set(self._pointer, value))

	@property
	def width(self):
		return Width(self)

	def _width_setter(self, index, value):
		ResultException.act(self._width_set(self._pointer, index, value))

	def _width_getter(self, index):
		val_ptr = ffi.new("b0_pwm_reg*")
		ResultException.act(self._width_get(self._pointer, index, val_ptr))
		return val_ptr[0]

	@staticmethod
	def calc_width(period, duty_cycle):
		"""
		Calculate width value from period and duty cycle.
		:param period: Period
		:param duty_cycle: Duty Cycle (duty_cycle <
		:return: Width value
		"""
		assert(0 < duty_cycle < 100)
		return (float(period) * float(duty_cycle)) / 100.0

	@staticmethod
	def calc_freq(speed, period):
		"""
		Calculate frequency from period and speed
		:param speed: Speed
		:param period: Period
		:return: Frequency
		"""
		return float(speed) / float(period)

	@staticmethod
	def calc_freq_err(required_freq, calc_freq):
		"""
		Calculate error.
		:param required_freq: Required frequency (user need)
		:param calc_freq: Calculated frequency (user can have)
		:return: Error (in percentage)
		.. note::
			*Relative error*
		"""
		assert(calc_freq > 0)
		assert(required_freq > 0)
		calc_freq = float(calc_freq)
		required_freq = float(required_freq)
		dev = abs(calc_freq - required_freq)
		return (dev * 100.0) / required_freq
