"""
CIGAR operations.

There are two ways to represent a CIGAR string:
- as a string, such as "17M1D5M4S"
- as a list of (operator, length) pairs, as used by pysam:
[ (0, 17), (1, 2), (0, 5), (0, 4) ]

The naming convention in this module uses cigar and cigar_string to
distinguish both types.

The mapping of CIGAR operators to numbers is:
MIDNSHPX= => 012345678
"""
import sys
from itertools import repeat, chain

__author__ = 'Marcel Martin'

# constants
M = 0  # match or mismatch
I = 1  # insertion
D = 2  # deletion
N = 3  # skipped reference region
S = 4  # soft clipping
H = 5  # hard clipping
P = 6  # padding
X = 7  # mismatch
EQ = 8 # match

# use this as a sequence to map an encoded operation to the appropriate
# character
OPERATORS = 'MIDNSHPX='
DECODE = OPERATORS

# this dictionary maps operations to their integer encodings
_ENCODE = dict( (c,i) for (i, c) in enumerate(DECODE) )


def _assert_at_end(i):
	"""Assert that the iterator i is at its end"""
	if __debug__:
		try:
			next(i)
			assert False
		except StopIteration:
			pass


def alignment_iter(read, ref, cigar, gap='-'):
	"""
	Yield triples (read_char, reference_char, cigar_char) that
	fully describe the alignment betwen read and ref according to cigar.

	If the cigar operation is a 'M', the cigar_char is set to either
	'=' or 'X' depending on whether read_char matches reference_char
	or not.

	At gaps in the alignment, either read_char or reference_char are
	set to the given gap character.

	read -- an iterable representing the read
	ref -- an iterable representing the reference sequence
	cigar -- a list of (operator, length) pairs
	"""
	i = iter(read)
	j = iter(ref)
	for op in decoded_ops(cigar):
		if op == 'S':
			ci = next(i)
		elif op == 'M':
			ci = next(i)
			cj = next(j)
			yield (ci, cj, '=' if ci == cj else 'X')
		elif op == 'I':
			yield (next(i), gap, 'I')
		elif op == 'D':
			yield (gap, next(j), 'D')
		else:
			raise ValueError("CIGAR operator {} not supported".format(op))
	_assert_at_end(i)
	_assert_at_end(j)


def print_alignment(read, ref, cigar, file=sys.stdout):
	"""
	Print an alignment between read and ref according to a CIGAR.
	This uses the alignment_iter() function from above.

	cigar -- a list of (operator, length) pairs
	"""
	row1 = ''
	row2 = ''
	align = ''
	for read_char, reference_char, op in alignment_iter(read, ref, cigar):
		row1 += read_char
		align += op
		row2 += reference_char
	print(row1, align, row2, sep='\n', file=file)


def unclipped_region(cigar):
	"""
	Return tuple (cigar, start, stop), where cigar is the given cigar without soft clipping
	and (start, stop) is the interval in which the read is *not* soft-clipped.
	"""
	if cigar[0][0] == S:
		start = cigar[0][1]
		cigar = cigar[1:]
	else:
		start = 0
	if cigar[-1][0] == S:
		stop = -cigar[-1][1]
		cigar = cigar[:-1]
	else:
		stop = None
	return (cigar, start, stop)


def reference_to_query_length(cig, reference_bases):
	"""
	Given a prefix of length reference_bases relative to the reference,
	how long is the prefix of the read?

	If the position is within an insertion, then the number of bases up to

	Hard- and soft-clipped bases are always included in the resulting coordinate.
	"""
	rpos = 0
	qpos = 0
	for op, length in cig:
		if op == S or op == H:
			qpos += length
		elif op == M:
			rpos += length
			qpos += length
			if rpos >= reference_bases:
				return qpos + reference_bases - rpos
		elif op == D:
			rpos += length
			if rpos >= reference_bases:
				return qpos
		elif op == I:
			qpos += length
		else:
			raise ValueError('CIGAR operator {!r} not supported, yet'.format(op))
	return None


class Cigar:
	"""
	Representation of an alignment in the form of a CIGAR string.

	TODO
	- Rename .cigar attribute to .ops/.opslist/.operations?
	- What should len(Cigar(...)) return? Length of .cigar attribute?
	- Length of alignment on reference
	- What should __iter__ do? Should it be .elements()?
	"""
	def __init__(self, cigar):
		"""
		cigar -- either a string such as '3M2I2M' or a list of
		         (operator, length) tuples.
		"""
		if isinstance(cigar, str):
			self.cigar = self.parse(cigar)
		# TODO
		# elif isinstance(cigar, Cigar): self.cigar = cigar.cigar
		else:
			self.cigar = cigar

	def __eq__(self, other):
		return self.cigar == other.cigar

	def __ne__(self, other):
		return self.cigar != other.cigar

	def __getitem__(self, key):
		return Cigar(self.cigar[key])

	def _as_string(self, join_by=''):
		"""
		Format the CIGAR string.

		join_by is an optional separator.

		>>> Cigar('3M2S')._as_string(join_by=' ')
		'3M 2S'
		"""
		return join_by.join(
			'{}{}'.format(l, DECODE[op]) for op, l in self.cigar)

	def __format__(self, format_spec):
		if format_spec in ('', ' '):
			return self._as_string(join_by=format_spec)
		else:
			raise ValueError(
				"Format specification '{}' not supported".format(format_spec))

	def __str__(self):
		return self._as_string()

	def __repr__(self):
		return "Cigar('{}')".format(str(self))

	@staticmethod
	def parse(cigar_string):
		"""
		Parse a CIGAR string and return a list of (operator, length) pairs.
		Spaces are ignored.

		>>> parse("3S17M8D4M9I3H")
		[(4, 3), (0, 17), (2, 8), (0, 4), (1, 9), (5, 3)]

		>>> parse("3S 17M")
		[(4, 3), (0, 17)]
		"""
		cigar = []
		n = ''  # This is a string to which digits are appended
		for c in cigar_string:
			if c.isdigit():
				n += c
			elif c in _ENCODE:
				if n == '':
					raise ValueError("CIGAR string should start with a number.")
				cigar.append( (_ENCODE[c], int(n)) )
				n = ''
			elif c == ' ':
				continue
			else:
				raise ValueError(
					'Character "{}" unexpected in CIGAR string.'.format(c))
		if n != '':
			raise ValueError("Unexpected end of CIGAR string.")
		return cigar

	def __add__(self, other):
		"""
		Return the concatenation of this CIGAR and another one.

		>>> Cigar('2S1M') + Cigar('3M4S'))
		Cigar('2S4M4S')
		"""
		if len(other.cigar) == 0:
			return Cigar(self.cigar)
		if len(self.cigar) == 0:
			return Cigar(other.cigar)
		self_last = self.cigar[-1]
		other_first = other.cigar[0]
		# same operation?
		if self_last[0] == other_first[0]:
			return Cigar(
				self.cigar[:-1] +
				[(self_last[0], self_last[1] + other_first[1])] +
				other.cigar[1:])
		return Cigar(self.cigar + other.cigar)

	def elements(self, numbers=False):
		"""
		Yield all operations one by one.

		If numbers is set to True, the operations are returned numerically.

		>>> ''.join(Cigar("3S2I3M").elements())
		"SSSIIMMM"

		>>> list(Cigar("3S2I3M").elements(numbers=True))
		[4, 4, 4, 1, 1, 0, 0, 0]
		"""
		if numbers:
			return chain.from_iterable(repeat(op, l) for (op, l) in self.cigar)
		else:
			return chain.from_iterable(
				repeat(DECODE[op], l) for (op, l) in self.cigar)

	def alignment_length(self):
		"""
		Return the number of bases of the read that are used in the alignment.
		This counts all matches, mismatches and insertions. Clipped bases are
		not counted.
		"""
		return sum(l for op, l in self.cigar if op in (M, I, EQ, X))

	def query_length(self, count_clipped='soft'):
		"""
		Return the length of the query sequence deduced from the
		length of the operations used in this CIGAR string.
		Matches, mismatches and insertions are counted (M, I, =, X operators).

		The count_clipped parameter determines whether hard- or soft-clipped
		bases are counted (H and S operators). It can be set to None, 'soft' or
		'hard'.

		- None: Do not count any clipped bases. Only the bases actually
			aligned to the reference are counted.

		- 'soft': Count also soft-clipped bases. The returned length should be
			identical to the length of the SEQ field in a SAM file that
			follows the specification. From the spec: 'sum of lengths of the
			M/I/S/=/X operations shall equal the length of SEQ'.

		- 'hard': Count both soft- and hard-clipped bases. The returned length
			is the same as the length of the original read.
		"""
		if count_clipped is None:
			ops_to_count = (M, I, EQ, X)
		elif count_clipped == 'soft':
			ops_to_count = (M, I, EQ, X, S)
		elif count_clipped == 'hard':
			ops_to_count = (M, I, EQ, X, S, H)
		else:
			raise ValueError(
				"count_clipped must be either None, 'soft' or 'hard'")

		return sum(length for op, length in self.cigar if op in ops_to_count)

	def reference_length(self):
		"""
		Return the length of the reference sequence deduced from the length of
		the operations used in the CIGAR string. This counts the M, D, N, X, =
		operations.
		"""
		return sum(length for op, length in self.cigar if op in
			 (M, D, EQ, X, N))

	def _clipping_length(self, where, op):
		"""
		where == 0: beginning
		where == -1: end
		"""
		if not self.cigar:
			return 0
		elem = self.cigar[where]
		if elem[0] == op:
			return elem[1]
		return 0

	@staticmethod
	def _clipping_length_both(elements):
		if not elements:
			return 0
		n = 0
		for op, length in elements:
			if op == H or op == S:
				n += length
			else:
				break
		return n

	@property
	def soft_clipping_left(self):
		"""
		Return length of soft-clipping in the beginning of the alignment.
		If the alignment is hard-clipped, return 0.
		"""
		return self._clipping_length(0, S)

	@property
	def soft_clipping_right(self):
		"""
		Return length of soft-clipping in the end of the alignment.
		If the alignment is hard-clipped, return 0.
		"""
		return self._clipping_length(-1, S)

	@property
	def hard_clipping_left(self):
		"""
		Return length of hard-clipping in the beginning of the alignment.
		"""
		return self._clipping_length(0, H)

	@property
	def hard_clipping_right(self):
		"""
		Return length of hard-clipping in the end of the alignment.
		"""
		return self._clipping_length(-1, H)

	@property
	def clipping_left(self):
		"""
		Return the length of soft- and hard-clipping in the beginning of the alignment
		"""
		return self._clipping_length_both(self.cigar)

	@property
	def clipping_right(self):
		"""
		Return the length of soft- and hard-clipping in the end of the alignment
		"""
		return self._clipping_length_both(self.cigar[::-1])


# deprecated functions that have become methods of the Cigar class

def decoded_ops(cigar):
	return Cigar(cigar).elements()


def ops(cigar):
	return Cigar(cigar).elements(numbers=True)


def as_string(cigar, join_by=''):
	return str(Cigar(cigar))


def parse(cigar_string):
	return Cigar.parse(cigar_string)


def concat(left, right):
	return Cigar(left) + Cigar(right)


def aligned_bases(cigar):
	return Cigar(cigar).query_length(count_clipped=None)


def seq_length(cigar):
	return Cigar(cigar).query_length(count_clipped='soft')


def read_length(cigar):
	return Cigar(cigar).query_length(count_clipped='hard')
