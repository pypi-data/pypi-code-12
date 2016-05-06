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
from box0.property import Property, WithValues, GetSetUInt8

class I2cVersion(Property, WithValues, GetSetUInt8):
	_info = libbox0.b0_i2c_version_info
	_cache_flush = libbox0.b0_i2c_version_cache_flush

	_get = libbox0.b0_i2c_version_get
	_set = libbox0.b0_i2c_version_set

	SM = libbox0.B0_I2C_VERSION_SM
	FM = libbox0.B0_I2C_VERSION_FM
	HS = libbox0.B0_I2C_VERSION_HS
	HS_CLEANUP1= libbox0.B0_I2C_VERSION_HS_CLEANUP1
	FMPLUS = libbox0.B0_I2C_VERSION_FMPLUS
	UFM = libbox0.B0_I2C_VERSION_UFM
	VER5 = libbox0.B0_I2C_VERSION_VER5
	VER6 = libbox0.B0_I2C_VERSION_VER6

	def __init__(self, prop):
		Property.__init__(self, prop)
		WithValues.__init__(self)
		GetSetUInt8.__init__(self)
