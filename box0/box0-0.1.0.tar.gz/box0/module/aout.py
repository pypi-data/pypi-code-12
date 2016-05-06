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
import numpy as np
from box0.module import ModuleInstance, np_dtype_map
from box0.property import Ref, Bitsize, Speed, \
				ChanConfig, ChanSeq, Count, \
				Capab, Label, Stream, Buffer, Repeat

class Aout(ModuleInstance):
	"""
	.. uml::

	   [*] -d-> Opened : Aout()
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

	      StreamPrepared -u-> StreamPrepared : chan_seq.value()

	      StreamRunning: data to be passed using stream_write()
	   }

	   state Static {
	      state "Running" as StaticRunning
	      state "Stopped" as StaticStopped

	      [*] -d-> StaticStopped : static_prepare()
	      StaticStopped -d-> StaticRunning : static_start()
	      StaticRunning -u-> StaticStopped : static_stop(), [Repeat complete]
	      StaticStopped --> [*]

	      StaticStopped -u-> StaticStopped : speed.value, bitsize.value, chan_seq.value, repeat.value
	   }
	"""

	_open = libbox0.b0_aout_open
	_close = libbox0.b0_aout_close
	_cache_flush = libbox0.b0_aout_cache_flush
	_info = libbox0.b0_aout_info

	_stream_prepare = libbox0.b0_aout_stream_prepare
	_stream_write = libbox0.b0_aout_stream_write
	_stream_write_double = libbox0.b0_aout_stream_write_double
	_stream_write_float = libbox0.b0_aout_stream_write_float
	_stream_start = libbox0.b0_aout_stream_start
	_stream_stop = libbox0.b0_aout_stream_stop

	_static_prepare = libbox0.b0_aout_static_prepare
	_static_start = libbox0.b0_aout_static_start
	_static_start_double = libbox0.b0_aout_static_start_double
	_static_start_float = libbox0.b0_aout_static_start_float
	_static_stop = libbox0.b0_aout_static_stop
	_static_calc = libbox0.b0_aout_static_calc

	ref = None
	"""Reference :class:`box0.property.Ref`"""

	bitsize = None
	"""Bitsize :class:`box0.property.bitsize`"""

	count = None
	"""Number of channels :class:`box0.property.Count`"""

	capab = None
	"""Capabilities :class:`box0.property.Capab`"""

	chan_config = None
	"""Channel Configuration :class:`box0.ChanConfig.`"""

	chan_seq = None
	"""Channel Sequence :class:`box0.property.ChanSeq`"""

	repeat = None
	"""Pattern repeat :class:`box0.property.Repeat`"""

	buffer = None
	"""Static mode buffer :class:`box0.property.Buffer`"""

	speed = None
	"""speed in static mode :class:`box0.property.speed`"""

	stream = None
	"""Streaming mode values :class:`box0.property.Stream`"""

	label = None
	"""label of channel :class:`box0.property.Label`"""

	def __init__(self, dev, index):
		ModuleInstance.__init__(self, dev, index, "b0_aout**")
		self.ref = Ref(self._pointer.ref)
		self.bitsize = Bitsize(self._pointer.bitsize)
		self.count = Count(self._pointer.count)
		self.capab = Capab(self._pointer.capab)
		self.chan_config = ChanConfig(self._pointer.chan_config)
		self.chan_seq = ChanSeq(self._pointer.chan_seq)
		self.repeat = Repeat(self._pointer.repeat)
		self.buffer = Buffer(self._pointer.buffer)
		self.speed = Speed(self._pointer.speed)
		self.stream = Stream(self._pointer.stream)
		self.label = Label(self._pointer.label)

	def stream_prepare(self, stream_value):
		"""
		Prepare for streaming mode

		:param box0.property.Stream.Value stream_value: Stream value, see `box0.module.Ain.stream`
		:raises ResultException: if libbox0 return negative result code
		"""
		ssv = stream_value._pointer
		ResultException.act(self._stream_prepare(self._pointer, ssv))

	"""
	currently double only supported
	data is numpy array
	"""
	def stream_write(self, data):
		"""
		wrtie data to stream

		:param numpy.ndarray data: Store readed data
		:raises ResultException: if libbox0 return negative result code
		"""
		sel = np_dtype_map(data.dtype,
			void = ("void *", self._stream_write),
			float32 = ("float *", self._stream_write_float),
			float64 = ("double *", self._stream_write_double))
		data_ptr = ffi.cast(sel[0], data.ctypes.data)
		ResultException.act(sel[1](self._pointer, data_ptr, data.size))

	def stream_start(self):
		"""
		Start streaming

		:raises ResultException: if libbox0 return negative result code
		"""
		ResultException.act(self._stream_start(self._pointer))

	def stream_stop(self):
		"""
		Stop streaming

		:raises ResultException: if libbox0 return negative result code
		"""
		ResultException.act(self._stream_stop(self._pointer))

	def static_prepare(self):
		"""
		Prepare for Static mode
		:raises ResultException: if libbox0 return negative result code
		"""
		ResultException.act(self._static_prepare(self._pointer))

	def static_start(self, data):
		"""
		Get data in static mode

		:param numpy.ndarray data: NumPy array to output
		:raises ResultException: if libbox0 return negative result code
		"""
		sel = np_dtype_map(data.dtype,
			void = ("void *", self._static_start),
			float32 = ("float *", self._static_start_float),
			float64 = ("double *", self._static_start_double))
		data_ptr = ffi.cast(sel[0], data.ctypes.data)
		ResultException.act(sel[1](self._pointer, data_ptr, data.size))

	def static_stop(self):
		"""
		Stop static output

		:raises ResultException: if libbox0 return negative result code
		"""
		ResultException.act(self._static_stop(self._pointer))

	def static_calc(self, freq, bitsize = None):
		"""
		Calculate best speed and count for a given frequency
		:return: count, speed
		:raises ResultException: if libbox0 return negative result code
		"""
		# get current bitsize if not provided
		if bitsize is None:
			bitsize = self.bitsize.current

		count = ffi.new("size_t *")
		speed = ffi.new("uint32_t *")
		ResultException.act(self._static_calc(self._pointer,
				freq, bitsize, count, speed))
		return count[0], speed[0]
