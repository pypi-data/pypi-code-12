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

from box0._binding import libbox0, ffi
from box0.property import Property

class Ref(Property):
	_info = libbox0.b0_ref_info
	_cache_flush = libbox0.b0_ref_cache_flush

	VOLTAGE = libbox0.B0_REF_VOLTAGE
	"""Reference type: Voltage"""

	CURRENT = libbox0.B0_REF_CURRENT
	"""Reference type: Current"""

	type = None
	"""Reference type"""

	low = None
	"""Reference low"""

	high = None
	"""Reference high"""

	def __init__(self, prop):
		Property.__init__(self, prop)
		self.type = prop.type
		self.low = prop.low
		self.high = prop.high
