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
from box0.module import Dio
from box0.exceptions import ResultException

class HBridge(Driver):
	"""
	Half Bridge Driver
	"""

	_open = libbox0.b0_hbridge_open
	_close = libbox0.b0_hbridge_close
	_info = libbox0.b0_hbridge_info
	_set = libbox0.b0_hbridge_set

	def __init__(self, module, EN=0, A1=1, A2=2):
		assert(type(module) is Dio)
		drv = ffi.new("b0_hbridge **")
		ResultException.act(self._open(module._pointer, drv, EN, A1, A2))
		Driver.__init__(self, drv[0], module)

	EN = libbox0.B0_HBRIDGE_EN
	"""EN pin mask"""

	A1 = libbox0.B0_HBRIDGE_A1
	"""A1 pin mask"""

	A2 = libbox0.B0_HBRIDGE_A2
	"""A2 pin mask"""

	DISABLE = libbox0.B0_HBRIDGE_DISABLE
	"""Operation: Disable"""

	FORWARD = libbox0.B0_HBRIDGE_FORWARD
	"""Operation: Forward"""

	BACKWARD = libbox0.B0_HBRIDGE_BACKWARD
	"""Operation: Backward"""

	def set(self, value):
		ResultException.act(self._set(self._pointer, value))

	def disable(self):
		self.set(self.DISABLE)

	def forward(self):
		self.set(self.FORWARD)

	def backward(self):
		self.set(self.BACKWARD)
