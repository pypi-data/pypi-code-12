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

from box0._binding import ffi, libbox0
from box0.exceptions import ResultException
import numpy as np

class Slave(object):
	def __init__(self, address, mod):
		self.address = address
		self.mod = mod

	def detect(self):
		return self.mod.detectSlave(self.address)

	def read(self, read):
		return self.mod.read(self.address, read)

	def write(self, write):
		return self.mod.read(self.address, write)

	def write8_read(self, write_byte, read):
		return self.mod.write8_read(self, self.address, write_byte, read)

	def __str__(self):
		return "Slave Address: " + hex(self.address)

#class Transaction(object):
#	def __init__(self):
#		"""
#		([read/write], [slave-address], [parameter])
#		"""
#		self.transaction = []
#
#	"""
#	return a token value that can be used in TransactionResult to read
#	the returned data
#	"""
#	def read(self, slaveAddress, nbytes):
#		self.transaction.append((true, slaveAddress, nbytes))
#		return self
#
#	"""
#	return nothing
#	"""
#	def write(self, slaveAddress, write):
#		self.transaction.append((false, slaveAddress, write))
#
#	def start(self, mod):
#		pass
#

class Bus(object):
	_read = None
	_write = None
	_write8_read = None
	_slave_detect = None
	_start = None
	_start_out = None

	def start(self, send, recv = None, allowPartial=True):
		"""
		send, recv should be numpy array
		if recv is None, no read is performed (use start_out)
		if allowPartial is True, no error is raised if partial data received.
		   also, the number of actual bytes readed is returned
		"""
		# select between start and start_out
		if recv is None:
			if self.start_out is None:
				raise Exception("bus do not support start_out")
			send_ptr = ffi.cast("void *", send.ctypes.data)
			result = self._start_out(self._pointer, send_ptr, send.nbytes)
			ResultException.act(result)
		else:
			if self.start is None:
				raise Exception("bus do not support start")
			send_ptr = ffi.cast("void *", send.ctypes.data)
			readed = ffi.new("size_t *") if allowPartial else ffi.NULL
			recv_ptr = ffi.cast("void *", recv.ctypes.data)
			result = self._start(self._pointer,
				send_ptr, send.nbytes, recv_ptr, recv.nbytes, readed)
			ResultException.act(result)
			if allowPartial:
				return readed[0]

	def stop(self):
		if self.stop is None:
			raise Exception("bus do not support stop")

		ResultException.act(self._stop(self._pointer))

	def slaveDetect(self, slaveAddress):
		if self._slave_detect is None:
			raise Exception("bus do not support slave detection")

		detected = ffi.new("bool*")
		ResultException.act(self._slave_detect(self._pointer, slaveAddress, detected))
		return (detected[0] != 0)

	"""
	read can be a number [no of bytes to read]
	or a numpy array, that contain no of bytes to read

	return the readed array
	"""
	def write8_read(self, slaveAddress, write_byte, read):
		if self._write8_read is None:
			raise Exception("bus dont support write8_read")

		if not isinstance(read, np.ndarray):
			read = int(read)
			assert (read > 0)
			read = np.empty(read, dtype=np.uint8)

		read_buf = ffi.cast("uint8_t *", read.ctypes.data)
		result = self._write8_read(self._pointer, slaveAddress, write_byte, read_buf, read.nbytes)
		ResultException.act(result)
		return read

	def write(self, slaveAddress, write):
		"""
		`write' is assumed to be a numpy array
		"""
		if self._write is None:
			raise Exception("bus dont support write")

		write_ptr = ffi.cast("uint8_t *", write.ctypes.data)
		result = self._write(self._pointer, slaveAddress, write_ptr, write.nbytes)
		ResultException.act(result)

	def read(self, slaveAddress, read):
		"""
		`read' can be a number [no of bytes to read]
		or a numpy array
		"""
		if self._read is None:
			raise Exception("bus dont support read")

		if not isinstance(read, np.ndarray):
			read = int(read)
			assert (read > 0)
			read = np.empty(read, dtype=np.uint8)

		data_ptr = ffi.cast("uint8_t *", read.ctypes.data)
		result = self._read(self._pointer, slaveAddress, data_ptr, read.nbytes)
		ResultException.act(result)
		return read

	def slave(self, slaveAddress):
		"""
		construct a Slave Object
		modX.slave(slaveAddress) => Slave(slaveAddress, modX)
		"""
		return Slave(slaveAddress, self)
