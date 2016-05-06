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

from box0._binding import libbox0, ffi, string_converter

class ResultException(Exception):
	"""
	Convert libbox0 result code in Exception.

	In libbox0, all result code which are less than 0 are failure code.
	and everything else is success code.

	.. code-block:: python

		import box0
		try:
			# try to open any supported device attached on USB
			dev = box0.usb.open_supported()
		except box0.ResultException, e:
			print("unable to get any supported device")
			print("name: " + e.name())
			print("explain: " + e.explain())
	"""

	value = None
	"""result code"""

	_name = libbox0.b0_result_name
	_explain = libbox0.b0_result_explain

	def __init__(self, value):
		self.value  = value

	def name(self):
		"""
		Result code name

		:return: name of the result code
		:rtype: str
		"""
		return string_converter(self._name(self.value))

	def explain(self):
		"""
		result code Explanation

		:return: explanation containing the meaning the result code
		:rtype: str
		"""
		return string_converter(self._explain(self.value))

	def __str__(self):
		"""same as :method: name()"""
		return self.name() + ": " + self.explain()

	@staticmethod
	def act(r):
		"""
		Act on libbox0 result code.
		This is intended for internal use.

		:param int r: libbox0 result code
		:raise ResultException: if result code *r* is less than 0 (failure)
		"""
		if r < 0: raise ResultException(r)
