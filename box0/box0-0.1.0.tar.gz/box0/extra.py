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

class Version:
	"""
	Build a Version object from libbox0 values or custom value

	if all three [major, minor, patch] are None, data is readed from libbox0

	if all three [major, minor, patch] can be converted to int and
	and if all three [major, minor, patch] ``0 <= value <= 255``,
	use them to build a version object

	in other case ValueError is raised

	.. note::

		if you want to know the version of pyBox0, see ``box0.__version__``

	.. code-block:: python

		from box0 import Version
		if Version() == Version(0, 1, 0):
			print("Wow, you are using a the first libbox0 release :)")
		else:
			print("Oh, you are using libbox0 %s", Version())
	"""

	_version_extract = libbox0.b0_version_extract

	code = None
	"""Code (``major << 16 | minor << 8 | patch << 0``)"""

	major = None
	"""Major"""

	minor = None
	"""Minor"""

	patch = None
	"""Patch"""

	def __init__(self, major = None, minor = None, patch = None):
		if major is None and minor is None and patch is None:

			ver = ffi.new("b0_version*")
			self.code = int(self._version_extract(ver))
			self.major = int(ver.major)
			self.minor = int(ver.minor)
			self.patch = int(ver.patch)
			return

		try:
			major = int(major)
			minor = int(minor)
			patch = int(patch)
			assert(0 <= major <= 255)
			assert(0 <= minor <= 255)
			assert(0 <= patch <= 255)
			self.major = major
			self.minor = minor
			self.patch = patch
			self.code = (major << 16) | (minor << 8) | (patch << 0)
		except:
			raise ValueError("invalid value")

	def __str__(self):
		return '%i.%i.%i' % (self.major, self.minor, self.patch)

	def __lt__(self, other):
		return (self.code < other.code)

	def __gt__(self, other):
		return (self.code > other.code)

	def __eq__(self, other):
		return (self.code == other.code)

	def __le__(self, other):
		return (self.code <= other.code)

	def __ge__(self, other):
		return (self.code >= other.code)
