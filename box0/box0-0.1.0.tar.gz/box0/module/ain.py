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
from box0.module import ModuleInstance, np_dtype_map
from box0.property import Ref, Bitsize, Speed, \
			ChanConfig, ChanSeq, Count, Buffer, \
		Capab, Label, Stream

class Ain(ModuleInstance):
	"""
	.. uml::
	   [*] -d-> Opened : Ain()
	   Opened -d-> Closed : close()
	   Closed -d-> [*]

	   Opened -r-> Stream
	   Stream -l-> Opened

	   Opened -l-> Static
	   Static -r-> Opened

	   state Stream {
	      state "Prepared" as StreamPrepared
	      state "Running" as StreamRunning
	      state "Stopped" as StreamStopped

	      [*] -d-> StreamPrepared : stream_prepare()

	      StreamPrepared -d-> StreamRunning : stream_start()
	      StreamStopped -u-> StreamRunning : stream_start()
	      StreamRunning -d-> StreamStopped : stream_stop()
	      StreamStopped --> [*]

	      StreamPrepared -u-> StreamPrepared : chan_seq.value

	      StreamRunning: data read using stream_read()
	   }

	   state Static {
	      state "Running" as StaticRunning
	      state "Stopped" as StaticStopped

	      [*] -d-> StaticStopped : static_prepare()
	      StaticStopped -d-> StaticRunning : static_start()
	      StaticRunning -u-> StaticStopped : static_stop(), [Acquisition complete]
	      StaticStopped --> [*]

	      StaticStopped -u-> StaticStopped : speed.value, bitsize.value, chan_seq.value
	   }
	"""
	_open = libbox0.b0_ain_open
	_close = libbox0.b0_ain_close
	_cache_flush = libbox0.b0_ain_cache_flush
	_info = libbox0.b0_ain_info

	_stream_prepare = libbox0.b0_ain_stream_prepare
	_stream_start = libbox0.b0_ain_stream_start
	_stream_read = libbox0.b0_ain_stream_read
	_stream_read_double = libbox0.b0_ain_stream_read_double
	_stream_read_float = libbox0.b0_ain_stream_read_float
	_stream_stop = libbox0.b0_ain_stream_stop

	_static_prepare = libbox0.b0_ain_static_prepare
	_static_start = libbox0.b0_ain_static_start
	_static_start_double = libbox0.b0_ain_static_start_double
	_static_start_float = libbox0.b0_ain_static_start_float
	_static_stop = libbox0.b0_ain_static_stop

	ref = None
	"""Reference :class:`box0.property.Ref`"""

	bitsize = None
	"""Bitsize :class:`box0.property.bitsize`"""

	speed = None
	"""speed in static mode :class:`box0.property.speed`"""

	chan_config = None
	"""Channel Configuration :class:`box0.ChanConfig.`"""

	chan_seq = None
	"""Channel Sequence :class:`box0.property.ChanSeq`"""

	count = None
	"""Number of channels :class:`box0.property.Count`"""

	capab = None
	"""Capabilities :class:`box0.property.Capab`"""

	label = None
	"""label of channel :class:`box0.property.Label`"""

	stream = None
	"""Streaming mode values :class:`box0.property.Stream`"""

	buffer = None
	"""Static mode buffer :class:`box0.property.Buffer`"""

	def __init__(self, dev, index):
		ModuleInstance.__init__(self, dev, index, "b0_ain**")
		self.ref = Ref(self._pointer.ref)
		self.bitsize = Bitsize(self._pointer.bitsize)
		self.speed = Speed(self._pointer.speed)
		self.chan_config = ChanConfig(self._pointer.chan_config)
		self.chan_seq = ChanSeq(self._pointer.chan_seq)
		self.count = Count(self._pointer.count)
		self.capab = Capab(self._pointer.capab)
		self.label = Label(self._pointer.label)
		self.stream = Stream(self._pointer.stream)
		self.buffer = Buffer(self._pointer.buffer)

	def static_prepare(self):
		"""
		Prepare for Static mode
		:raises ResultException: if libbox0 return negative result code
		"""
		ResultException.act(self._static_prepare(self._pointer))

	def static_start(self, data):
		"""
		Get data in static mode

		:param numpy.ndarray data: NumPy array to store readed value
		:raises ResultException: if libbox0 return negative result code

		.. warning::

			This function is blocking and will not return until acquire all data
		"""
		sel = np_dtype_map(data.dtype,
			void = ("void *", self._static_start),
			float32 = ("float *", self._static_start_float),
			float64 = ("double *", self._static_start_double))
		data_ptr = ffi.cast(sel[0], data.ctypes.data)
		ResultException.act(sel[1](self._pointer, data_ptr, data.size))

	def static_stop(self):
		"""
		Stop an ongoing static acquisition

		:raises ResultException: if libbox0 return negative result code
		"""
		ResultException.act(self._static_stop(self._pointer))

	def stream_prepare(self, stream_value):
		"""
		Prepare for streaming mode

		:param box0.property.Stream.Value stream_value: Stream value, see `box0.module.Ain.stream`
		:raises ResultException: if libbox0 return negative result code
		"""
		ssv = stream_value._pointer
		ResultException.act(self._stream_prepare(self._pointer, ssv))

	def stream_start(self):
		"""
		Start streaming

		:raises ResultException: if libbox0 return negative result code
		"""
		ResultException.act(self._stream_start(self._pointer))


	def stream_read(self, data, allowPartial=False):
		"""
		Read data from stream

		:param numpy.ndarray data: Store readed data
		:param bool allowPartial: if False, return only after reading total requested samples
		:rtype: int
		:return: number of samples readed

		:raises ResultException: if libbox0 return negative result code

		.. note::

			This function can work in two modes.

			blocking: if `allowPartial is False`, block until all data is readed

			non-blocking: if `allowPartial is True`, try to read as much as requested data and return
		"""
		sel = np_dtype_map(data.dtype,
			void = ("void *", self._stream_read),
			float32 = ("float *", self._stream_read_float),
			float64 = ("double *", self._stream_read_double))
		data_ptr = ffi.cast(sel[0], data.ctypes.data)
		actual_readed = ffi.new("size_t *") if allowPartial else ffi.NULL
		ResultException.act(sel[1](self._pointer, data_ptr, data.size, actual_readed))
		return actual_readed[0] if allowPartial else data.size

	def stream_stop(self):
		"""
		Stop streaming

		:raises ResultException: if libbox0 return negative result code
		"""
		ResultException.act(self._stream_stop(self._pointer))
