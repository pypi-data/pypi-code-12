"""
Reading 454 .sff files (flowgram file format)
(c) Sven Rahmann, 2011
see: http://www.ncbi.nlm.nih.gov/Traces/trace.cgi?cmd=show&f=formats&m=doc&s=format
"""
__author__ = 'Sven Rahmann'

from struct import calcsize, unpack
from collections import namedtuple

class FormatError(Exception):
	pass


class SFFFile():
	_MAGIC = 0x2E736666

	def __init__(self, filename):
		self.filename = filename
		with open(filename, mode="rb") as f:
			self._set_info_from_header(f)

	def _process_padding(self, f, p):
		if not (0 <= p < 8):
			raise FormatError("Padding mismatch, padding=" + str(p))
		padder = f.read(p)
		if padder.count(b'\0') != p:
			raise FormatError("Padding seems to contain data")

	def _fread(self, f, fmt):
		b = calcsize(fmt)
		data = f.read(b)
		if len(data) < b:
			raise FormatError("chunk for " + fmt + " too short: " + str(len(data)) + "/" + str(b))
		return unpack(fmt, data)


	def _set_info_from_header(self, f):
		"""read the sff header and store its information in self"""
		_FIXEDLEN = 31
		# Read file header (constant part), length 31 bytes, 9 fields
		# big endian encdoing        >
		# magic_number               I  == _MAGIC
		# version                    4B == (0,0,0,1)
		# index_offset               Q
		# index_length               I
		# number_of_reads            I
		# header_length              H  divisble by 8
		# key_length                 H
		# number_of_flows_per_read   H
		# flowgram_format_code       B == 1
		headerformat = '>I4BQIIHHHB'
		assert calcsize(headerformat) == _FIXEDLEN
		(magic_number,
			ver0, ver1, ver2, ver3,
			index_offset, index_length,
			number_of_reads,
			header_length,
			key_length,
			number_of_flows_per_read,
			flowgram_format_code) = self._fread(f, headerformat)
		if magic_number != SFFFile._MAGIC:
			raise FormatError("Magic number is {} instead of {}").format(magic_number, SFFFile._MAGIC)
		if (ver0, ver1, ver2, ver3) != (0, 0, 0, 1):
			raise FormatError("Unsupported .sff version ({}.{}.{}.{})".format(ver0, ver1, ver2, ver3))
		if (index_offset != 0) ^ (index_length != 0):
			raise FormatError("Index offset is {}, but length is {}".format(index_offset, index_length))
		if (index_offset % 8 != 0) or (index_length % 8 != 0):
			#raise FormatError("Index (offset, length) must be divisible by 8"+str(index_offset)+","+str(index_length))
			pass
		if header_length % 8 != 0:
			raise FormatError("Header length must be divisible by 8, but is {}".format(header_length))
		if flowgram_format_code != 1:
			raise FormatError("Flowgram format code {} not supported".format(flowgram_format_code))
		# Read variable part of header:
		# flow_chars     {number_of_flows_per_read}s
		# key_sequence   {key_length}s
		flow_chars = f.read(number_of_flows_per_read)
		key_sequence = f.read(key_length)
		# padding        *B
		padding = header_length - number_of_flows_per_read - key_length - _FIXEDLEN
		self._process_padding(f, padding)
		# set attributes:
		self.magic_number = magic_number
		self.version = (ver0, ver1, ver2, ver3)
		self.has_index = (index_offset != 0) and (index_length != 0)
		self.index_offset = index_offset
		self.index_length = index_length
		self.number_of_reads = number_of_reads
		self.header_length = header_length
		#self.key_length   = key_length  #  == len(key_sequence)
		self.key_sequence = key_sequence
		self.number_of_flows_per_read = number_of_flows_per_read
		self.flow_chars = flow_chars
		self.flowgram_format_code = flowgram_format_code

	# generator function to iterate over all reads
	def reads(self):
		"""yields each read in this .sff file as a Read object."""
		header_length = self.header_length
		with open(self.filename, mode="rb") as f:
			f.read(header_length)
			fpos = header_length
			checkindex = self.has_index
			for r in range(self.number_of_reads):
				assert fpos % 8 == 0, "file position {} not divisible by 8".format(fpos)
				if checkindex and fpos == self.index_offset:
					f.read(index_length)
					fpos += index.length
					checkindex = False
				read = self._next_read(f, r)
				yield read

	def __iter__(self):
		return self.reads()

	def _next_read(self, f, readindex):
		"""reads the next read record from an open .sff file f"""
		# Read fixed part of read header, 7 fields
		# read_header_length     H
		# name_length            H
		# seq_len                I
		# clip_qual_left         H
		# clip_qual_right        H
		# clip_adapter_left      H
		# clip_adapter_right     H
		header_fmt = ">HHIHHHH"
		(read_header_length,
		name_length,
		seq_len,
		clip_qual_left, clip_qual_right,
		clip_adapter_left, clip_adapter_right) = self._fread(f, header_fmt)
		# check format
		expected = ((16 + name_length + 7) // 8) * 8
		if read_header_length != expected:
			raise FormatError("read header length should be 16 + name length, rounded up mod 8")
		# name                 c * name_length
		# padding              B * [to fill]
		name_fmt = ">" + str(name_length) + "s"
		(namebytes,) = self._fread(f, name_fmt)
		name = namebytes.decode()
		padding = read_header_length - (16 + name_length)
		self._process_padding(f, padding)
		# flowgram_values      H * nflows  [type may differ with future formats]
		# flow_index_per_base  B * seq_len
		# bases                c * seq_len
		# quality_scores       B * seq_len
		# padding              B * [to fill]
		datatypes = ".H"
		flow_fmt = ">" + str(self.number_of_flows_per_read) + datatypes[self.flowgram_format_code]
		byte_fmt = ">" + str(seq_len) + "B"
		char_fmt = ">" + str(seq_len) + "s"
		flowgram_values = self._fread(f, flow_fmt)
		flow_index_per_base = self._fread(f, byte_fmt)
		if seq_len > 0:
			flow_index_per_base = (flow_index_per_base[0] - 1,) + flow_index_per_base[1:] # convert to 0-based index
		(bases,) = self._fread(f, char_fmt)
		quality_scores = self._fread(f, byte_fmt)
		datalen = sum(map(calcsize, (flow_fmt, byte_fmt, char_fmt, byte_fmt)))
		padding = (-datalen) % 8
		self._process_padding(f, padding)
		r = Read(readindex, name, self, # self is the current sff file
				clip_qual_left, clip_qual_right, clip_adapter_left, clip_adapter_right,
				flowgram_values, bases, flow_index_per_base, quality_scores)
		return r


# TODO move the Flow and Flowgram class into some other module?
class Flow(namedtuple('Flow', ['char', 'intensity'])):
	def __str__(self):
		return '{}{:.2f}'.format(chr(self.char), self.intensity)


class Flowgram:
	"""
	A flowgram is mathematically defined to be a list of (char, intensity) pairs,
	but this implementation stores two lists, one with chars and one
	with intensities. Indexed access and iteration are supported, however, and result in
	(char, intensity) pairs.
	"""
	def __init__(self, flowchars, intensities):
		if len(flowchars) != len(intensities):
			raise ValueError("lengths of flowchars and intensities must be equal")
		self.flowchars = flowchars
		self.intensities = intensities

	def __iter__(self):
		return (Flow(*flow) for flow in zip(self.flowchars, self.intensities))

	def __len__(self):
		return len(self.flowchars)

	def __str__(self):
		return ' '.join(str(flow) for flow in self)


class Read(Flowgram):
	"""
	Represent a flowgram read by the following attributes:
	- index: int, 0-based running number of the read in the sff file
	- name: bytes, a unique id for the read
	- sff: SFFFile, from which the read was obtained
	- flowvalues: tuple of ints
	- flowchars:  bytes, usually  b'TACG' * n for some n
	- qual: tuple of ints, quality values (10log10-representation)
	- clip: 4-tuple with clipping information
	- key: bytes, the key sequence (usually b'TCAG')
	- bases: bytes, the 454-converted sequence representation of the flowvalues
	- flow_index_per_base: tuple of ints
	"""
	def __init__(self, index, name, sff_origin,
				clip_qual_left, clip_qual_right, clip_adapter_left, clip_adapter_right,
				flowgram_values, bases, flow_index_per_base, quality_scores):
		self.index = index
		self.name = name
		self.sff = sff_origin
		self.clip = dict(ql=clip_qual_left, qr=clip_qual_right,
						al=clip_adapter_left, ar=clip_adapter_right)
		self.flowchars = sff_origin.flow_chars
		self.flowvalues = flowgram_values
		self.intensities = [ v / 100.0 for v in flowgram_values ]
		self.key = sff_origin.key_sequence
		self.bases = bases
		self.flow_index_per_base = flow_index_per_base
		self.qual = quality_scores

		self.insert_start = max(1, max(self.clip['ql'], self.clip['al'])) - 1
		self.insert_stop = min(len(bases) if self.clip['qr'] == 0 else self.clip['qr'],
			len(bases) if self.clip['ar'] == 0 else self.clip['ar'])


class ClippedRead(Flowgram):
	"""
	A read in which both the bases and the flowgram (flowchars and intensities) are
	clipped to the insert region.

	A ClippedRead also has a base_to_flow attribute which maps base
	indices to flow indices.
	"""

	def __init__(self, read, start=0, stop=None):
		"""
		read is a Read object.
		start and stop specify additional offsets within the insert region.
		start and stop are interpreted as in slice notation (negative values
		and None are allowed).
		"""
		self._read = read
		self.name = read.name
		# _fl prefix: index into flowgram
		# _b  prefix: index into bases
		insert_start_b = max(1, max(read.clip['ql'], read.clip['al'])) - 1
		insert_stop_b = min(len(read.bases) if read.clip['qr'] == 0 else read.clip['qr'],
			len(read.bases) if read.clip['ar'] == 0 else read.clip['ar'])
		start_b, stop_b, _ = slice(start, stop).indices(insert_stop_b - insert_start_b)
		start_b += insert_start_b
		stop_b += insert_start_b
		b2fl = self._compute_base_to_flow()
		start_fl = b2fl[start_b]
		stop_fl = b2fl[stop_b]

		self.bases = read.bases[start_b:stop_b]
		self.intensities = read.intensities[start_fl:stop_fl]
		self.flowchars = read.flowchars[start_fl:stop_fl]
		self.base_to_flow = [ index_fl - start_fl for index_fl in b2fl[start_b:stop_b] ]
		assert len(self.bases) == len(self.base_to_flow)

	def _compute_base_to_flow(self):
		"""
		map a base index to a flow index
		"""
		m = []
		v = 0
		for index in self._read.flow_index_per_base:
			v += index
			m.append(v)
		assert v < len(self._read.intensities)
		m.append(len(self._read.intensities))
		return m
