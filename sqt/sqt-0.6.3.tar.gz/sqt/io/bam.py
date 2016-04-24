#!/usr/bin/env python3
from collections import namedtuple
from struct import calcsize, unpack, unpack_from
from array import array
import gzip
from itertools import chain
import sys

from ..cigar import Cigar

Reference = namedtuple('Reference', ['name', 'length'])

class FormatError:
	pass

SEQ_TRANS = bytes.maketrans(bytes(range(16)), b'=ACMGRSVTWYHKDBN')
CIGAR_OPS = 'MIDNSHP=X'
QUAL_TRANS = bytes.maketrans(bytes(range(100)), bytes(range(33, 133)))

def quality_to_ascii(qualities):
	if qualities is None:
		return '*'
	return qualities.translate(QUAL_TRANS).decode('ascii')


TAG_TYPES = {
	'A': 'c',  # character
	'c': 'b',  # signed 8-bit integer
	'C': 'B',  # unsigned 8-bit integer
	's': 'h',  # signed 16-bit integer
	'S': 'H',  # unsigned 16-bit integer
	'i': 'l',  # signed 32-bit integer
	'I': 'L',  # unsigned 32-bit integer
	'f': 'f',  # 32-bit floating point number
	#'Z': zero-terminated string
	#'H': byte array in hex format
	#'B': integer or numeric array
}

INVERSE_TAG_TYPES = dict((value, key) for (key, value) in TAG_TYPES.items())

BAM_TO_SAM_TYPES = {
	'A': 'A',
	'c': 'i',
	'C': 'i',
	's': 'i',
	'S': 'i',
	'i': 'i',
	'I': 'i',
	'f': 'f',
	'Z': 'Z',
	'B': 'B',
}

class BamAlignment:
	def __init__(self, data, references):
		self.references = references
		align = '<iiIIiiii'
		(
			self.reference_id,
			self.position,
			bin_mq_nl,
			flag_nc,
			l_seq,
			self.next_reference_id,
			self.next_position,
			self.insert_length
		) = unpack_from(align, data)
		#bin = bin_mq_nl >> 16

		self.mapping_quality = (bin_mq_nl & 0xFF00) >> 8
		self.flags = flag_nc >> 16
		n = calcsize(align)

		# Query name
		query_name_length = bin_mq_nl & 0xFF
		self.query_name = data[n: n + query_name_length - 1].decode('ascii') # NULL-terminated
		if self.query_name == '*':
			self.query_name = None
		offset = n + query_name_length

		# CIGAR
		n_cigar_op = flag_nc & 0xFFFF
		cigar_codes = unpack_from('<{}I'.format(n_cigar_op), data, offset=offset)
		if not cigar_codes:
			self.cigar = None
		else:
			self.cigar = Cigar((code & 0xF, code >> 4) for code in cigar_codes)
		offset += 4 * n_cigar_op

		# Sequence
		encoded_seq = data[offset:offset + (l_seq + 1) // 2]
		sequence = bytes(chain(*[(v>>4, v&0xF) for v in encoded_seq]))
		sequence = sequence.translate(SEQ_TRANS).decode('ascii')
		if l_seq & 1 == 1:  # if odd
			sequence = sequence[:l_seq]
		self.sequence = sequence
		offset += (l_seq + 1) // 2

		# Qualities
		qualities = data[offset:offset + l_seq]
		if l_seq == 0 or qualities[0] == 255:
			qualities = None
		self.qualities = qualities
		offset += l_seq

		self.tags = self._parse_tags(data, offset)

	def _parse_tags(self, data, offset):
		tags = []
		while offset < len(data):
			assert offset <= len(data) - 4
			tag_name = data[offset:offset+2].decode('ascii')
			tag_type = chr(data[offset+2])
			assert tag_type in 'AcCsSiIfZHB'
			if tag_type == 'A':
				tag_value = chr(data[offset+3])
				offset += 4
			elif tag_type == 'Z':
				i = data.index(0, offset+3)
				tag_value = data[offset+3:i].decode('ascii')
				offset = i + 1
			elif tag_type == 'H':
				raise NotImplementedError("Tag type H not implemented")
			elif tag_type == 'B':
				array_type = chr(data[offset+3])
				assert array_type in 'cCsSiIf'
				length = unpack_from('<I', data, offset+4)[0]
				byte_length = length * calcsize(TAG_TYPES[array_type])
				assert offset + 8 + byte_length <= len(data)
				tag_value = array(TAG_TYPES[array_type], data[offset+8:offset+8+byte_length])
				offset += 8 + byte_length
			else:
				tag_value = unpack_from(TAG_TYPES[tag_type], data, offset + 3)[0]
				offset += 3 + calcsize(TAG_TYPES[tag_type])
			tags.append((tag_name, tag_type, tag_value))
		return tags

	@property
	def qualities_string(self):
		if self.qualities is None:
			return None
		return self.qualities.translate(QUAL_TRANS).decode('ascii')

	def _id_to_reference_name(self, id):
		assert id < len(self.references)
		if id >= 0:
			return self.references[id].name
		else:
			return None

	@property
	def reference_name(self):
		return self._id_to_reference_name(self.reference_id)

	@property
	def next_reference_name(self):
		return self._id_to_reference_name(self.next_reference_id)

	def __str__(self):
		"""Return SAM-formatted representation of this record"""
		refname = self.reference_name
		if self.next_reference_id == self.reference_id and self.reference_id >= 0:
			nextrefname = '='
		else:
			nextrefname = self.next_reference_name

		def format_value(type, v):
			if type == 'f':
				return '{:g}'.format(v)
			elif type == 'B':
				tc = INVERSE_TAG_TYPES[v.typecode]
				s  = tc + ','
				s += ','.join(format_value(tc, x) for x in v)
				return s
			else:
				return str(v)

		def asterisk(v):
			return '*' if v is None else v

		tags = '\t'.join(':'.join((name, BAM_TO_SAM_TYPES[type], format_value(type, value))) for name, type, value in self.tags)
		fields = [
			asterisk(self.query_name),
			self.flags,
			asterisk(refname),
			self.position + 1,
			self.mapping_quality,
			asterisk(self.cigar),
			asterisk(nextrefname),
			self.next_position + 1,
			self.insert_length,
			self.sequence if self.sequence else '*',
			quality_to_ascii(self.qualities)
		]
		if tags:
			# Avoid printing the tab character at the end of the line if there are no tags
			fields.append(tags)
		return '\t'.join(str(f) for f in fields)


class BamReader:
	MAGIC = b'BAM\1'

	def __init__(self, file):
		"""
		open the file, read the header
		"""
		file = gzip.GzipFile(file, 'rb')
		data = file.read(4)
		if data != self.MAGIC:
			raise FormatError("magic bytes 'BAM\\1' not found, is this a BAM file?")
		# header in SAM text format
		header_length = unpack('<i', file.read(4))[0]
		self.header = file.read(header_length).decode('ascii')
		# BAM header with reference sequence names and lengths
		n = unpack('<i', file.read(4))[0]
		refs = []
		for i in range(n):
			ref_name_length = unpack('<i', file.read(4))[0]
			ref_name = file.read(ref_name_length)[:-1].decode('ascii') # NULL-terminated
			ref_length = unpack('<i', file.read(4))[0]
			refs.append(Reference(ref_name, ref_length))
		self.references = refs
		self.file = file

	def __iter__(self):
		while True:
			data = self.file.read(4)
			if len(data) < 4:
				break
			block_size = unpack('<i', data)[0]
			data = self.file.read(block_size)
			yield BamAlignment(data, self.references)


def main():
	reader = BamReader(sys.argv[1])
	print(reader.header, end='')
	for alignment in reader:
		try:
			print(alignment)
		except BrokenPipeError:
			break


if __name__ == '__main__':
	main()
