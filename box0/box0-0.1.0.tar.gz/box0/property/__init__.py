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

from box0.property.property import Property, GetSet, GetSetUInt32, GetSetUInt8, WithValue, WithValues
from box0.property.bitsize import Bitsize
from box0.property.buffer import Buffer
from box0.property.chan_seq import ChanSeq
from box0.property.count import Count
from box0.property.ref import Ref
from box0.property.i2c_version import I2cVersion
from box0.property.label import Label
from box0.property.repeat import Repeat
from box0.property.speed import Speed
from box0.property.stream import Stream
from box0.property.chan_config import ChanConfig
from box0.property.capab import Capab

__all__ = [
	"Property",
	"PropertyGetSet",
	"PropertyGetSetUInt32",
	"PropertyGetSetUInt8",

	"Bitsize",
	"Buffer",
	"ChanSeq",
	"Count",
	"Ref",
	"I2cVersion",
	"Label",
	"Repeat",
	"Speed",
	"Stream",
	"Capab",
	"ChanConfig"
]
