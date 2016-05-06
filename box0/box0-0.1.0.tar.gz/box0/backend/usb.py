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
from box0.exceptions import ResultException
from box0.device import Device

_open_vid_pid = libbox0.b0_usb_open_vid_pid
_open_supported = libbox0.b0_usb_open_supported
_libusb_context = libbox0.b0_usb_libusb_context
_libusb_device = libbox0.b0_usb_libusb_device
_libusb_device_handle = libbox0.b0_usb_libusb_device_handle

_device_bulk_timeout = libbox0.b0_usb_device_bulk_timeout
_device_ctrlreq_timeout = libbox0.b0_usb_device_ctrlreq_timeout
_ain_iso_test = libbox0.b0_usb_ain_iso_test
_ain_iso_delay = libbox0.b0_usb_ain_iso_delay
_aout_iso_test = libbox0.b0_usb_aout_iso_test
_aout_iso_pending = libbox0.b0_usb_aout_iso_pending

def open_supported():
	"""
	Open any supported device
	return None if none is found
	"""
	dev_ptr = ffi.new("b0_device **")
	ResultException.act(_open_supported(dev_ptr))
	return Device(dev_ptr[0])

def open_vid_pid(vid, pid):
	"""
	Open a device using vid, pid
	"""
	dev_ptr = ffi.new("b0_device **")
	ResultException.act(_open_vid_pid(dev_ptr, vid, pid))
	return Device(dev_ptr[0])

def __libusb_get(dev, type_ptr, fn):
	ptr = ffi.new(type_ptr)
	ResultException.act(fn(dev._pointer, ptr))
	return ptr[0]

def libusb_context(dev):
	return __libusb_get(dev, "libusb_context **", _libusb_context)

def libusb_device(dev):
	return __libusb_get(dev, "libusb_device **", _libusb_device)

def libusb_device_handle(dev):
	return __libusb_get(dev, "libusb_device_handle **", _libusb_device_handle)

def device_bulk_timeout(dev, timeout):
	ResultException.act(_device_bulk_timeout(dev._pointer, timeout))

def device_ctrlreq_timeout(dev, timeout):
	ResultException.act(_device_ctrlreq_timeout(dev._pointer, timeout))

def ain_iso_test(mod, enable):
	ResultException.act(_ain_iso_test(mod._pointer, enable))

def ain_iso_delay(mod, delay):
	ResultException.act(_ain_iso_delay(mod._pointer, delay))

def aout_iso_test(mod, enable):
	ResultException.act(_aout_iso_test(mod._pointer, enable))

def aout_iso_pending(mod, pending):
	ResultException.act(_aout_iso_pending(mod._pointer, pending))
