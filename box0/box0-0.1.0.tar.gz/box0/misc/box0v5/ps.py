#
# This file is part of pyBox0.
# Copyright (C) 2015, 2016 Kuldeep Singh Dhaka <kuldeepdhaka9@gmail.com>
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

_en_set = libbox0.b0_box0v5_ps_en_set
_en_get = libbox0.b0_box0v5_ps_en_get
_oc_get = libbox0.b0_box0v5_ps_oc_get
_oc_ack = libbox0.b0_box0v5_ps_oc_ack

# Power supply return libusb codes. (libbox0 result code api is not used)
class Problem(Exception):
	def __init__(self, ec, msg):
		self.error_code = ec
		Exception.__init__(self, msg)

	@staticmethod
	def act(ec, fn):
		if ec < 0: raise Problem(ec, "box0-v5 %s() failed" % fn)

PM5 = libbox0.B0_BOX0V5_PS_PM5
P3 = libbox0.B0_BOX0V5_PS_P3

ANALOG = PM5
DIGITAL = P3

def en_set(usbdh, mask, value):
	Problem.act(_en_set(usbdh, mask, value), "en_set")

def en_get(usbdh):
	val_ptr = ffi.new("uint8_t*")
	Problem.act(_en_get(usbdh, val_ptr), "en_get")
	return val_ptr[0]

def oc_get(usbdh):
	val_ptr = ffi.new("uint8_t*")
	Problem.act(_oc_get(usbdh, mask, val_ptr), "oc_get")
	return val_ptr[0]

def oc_ack(usbdh, mask):
	Problem.act(_oc_ack(usbdh, mask), "oc_ack")
