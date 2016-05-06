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

"""
This file contain some of the generic class that will be sub classed
through out the library in order to generalize the code and behaviour

all libbox0 object in pybox0 will be represented by Box0 class.
for b0_<object>_<method> that can be generalized are placed here
 for example b0_device_info, their is a class Info that is implemented by Device
"""

from box0._binding import ffi
from box0.exceptions import ResultException

class Box0(object):
	"""
	Generic Box0 object.
	all libbox0 object contain a set of common api.
	"""

	_pointer = None
	"""CFFI pointer of the underlying libbox0 object"""

	def __init__(self, pointer):
		"""Create a Box0 object from CFFI Pointer."""
		self._pointer = pointer

	def __eq__(self, other):
		"""
		Compare two Box0 object.
		This will compare class as well as the C Memory location
		"""
		"note, self.__class__ return sub classs name"
		return (self.__class__ == other.__class__) and (self._pointer == other._pointer)

class Info(object):
	"""Method for libbox0 object that contain useful internal information"""

	_info = None

	def info(self):
		"""Print information about object"""
		ResultException.act(self._info(self._pointer))

class Cache(object):
	"""Method for libbox0 object that perform caching"""

	_cache_flush = None

	def cache_flush(self):
		"""Flush cache of object."""
		ResultException.act(self._cache_flush(self._pointer))

class Close(object):
	"""Methods for libbox0 object that are closable"""

	_close = None

	def close(self):
		"""
		Close libbox0 object.

		.. note::

			close object when ever they are not required as
			doing so return the resources back to the system.
		"""
		if self._pointer is ffi.NULL:
			raise Exception("self._pointer is NULL (already closed?)")
		ResultException.act(self._close(self._pointer))
		self._pointer = ffi.NULL

	def __del__(self):
		"""If the object is going to be deleted, but isn't closed, close it!"""
		if self._pointer not in (ffi.NULL, None) and self._close is not None:
			self._close(self._pointer)

	def __enter__(self):
		"""Able to use "with" operator with Close sub-type"""
		return self

	def __exit__(self, arg1, arg2, arg3):
		"""Able to use "with" operator with Close sub-type"""
		self.close()
