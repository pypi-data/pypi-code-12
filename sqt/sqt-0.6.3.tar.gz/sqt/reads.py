"""
Classes that help in working with supplementary alignments.
"""
from collections import namedtuple
from .cigar import Cigar

class SupplementaryAlignment(namedtuple("SupplementaryAlignment",
	['reference_name', 'pos', 'strand', 'cigar', 'mapping_quality', 'edit_distance'])):
	@property
	def query_start(self):
		return self.cigar.clipping_left

	@property
	def query_end(self):
		return self.cigar.clipping_left + self.cigar.query_length(count_clipped=None)

	@property
	def query_length(self):
		return self.cigar.query_length(count_clipped=None)

	@property
	def reference_end(self):
		return self.pos + self.cigar.reference_length()


def parse_supplementary(sa):
	"""
	Parse supplementary alignments given by the SA:Z: tag in a SAM record.

	Return a list of SupplementaryAlignment objects.
	"""
	fields = sa.split(';')
	assert fields[-1] == ''  # sa must end with a ';'
	alignments = []
	for field in fields[:-1]:
		ref, pos, strand, cig, mapq, edit_dist = field.split(',')
		pos = int(pos) - 1
		cig = Cigar(cig)

		# All information in the BAM file is relative to the reference.
		# Since we are interested in information relative to the read,
		# the CIGAR string needs to be reversed when the strand is '-'.
		if strand == '-':
			cig = cig[::-1]
		mapq = int(mapq)
		edit_dist = int(edit_dist)
		assert strand in '+-'
		a = SupplementaryAlignment(ref, pos, strand, cig, mapq, edit_dist)
		alignments.append(a)
	return alignments


class AlignedRead:
	"""
	An AlignedRead describes all alignments of a read that appears in a
	SAM/BAM file. This collects all the supplementary alignments for the read in
	one place and gives a read-centric view of the alignments, instead of a
	reference-centric one.
	"""
	def __init__(self, read, reference_name):
		"""
		read -- an AlignedSegment. The SA tag of the read is parsed.
		"""
		#assert not read.is_secondary, "Read should not be secondary"
		#assert not read.is_supplementary, "Read should not be supplementary"
		self.alignments = self._extract_supplementary_alignments(read, reference_name)
		self.query_name = read.query_name
		self._primary_read = read  # TODO not necessarily correct since assertions were removed above
		self._length = self.alignments[0].cigar.query_length(count_clipped='hard')
		#assert self._length == Cigar(read.cigar).query_length(count_clipped='soft'), "Shouldn't be hard-clipped"

	def __len__(self):
		"""
		Number of bases in this read.
		"""
		return self._length

	def __iter__(self):
		yield from self.alignments

	def aligned_bases(self):
		"""
		Return how many bases are aligned, considering all supplementary
		alignments. Overlapping supplementary alignments are allowed: Each base
		is counted at most once!
		"""
		events = []
		for alignment in self.alignments:
			events.append((alignment.query_start, 'start', None))
			events.append((alignment.query_end, 'stop', alignment))

		depth = 0  # number of observed 'start' events
		bases = 0  # number of covered bases
		last_qstart = None
		for qpos, what, alignment in sorted(events, key=lambda x: x[0]):
			if what == 'start':
				if depth == 0:
					last_qstart = qpos
				depth += 1
			elif what == 'stop':
				depth -= 1
				if depth == 0:
					# interval (last_qstart, qpos) was covered
					bases += qpos - last_qstart
		return bases

	def _extract_supplementary_alignments(self, aligned_segment, reference_name):
		"""
		Given a single entry in a BAM file (an AlignedSegment) that potentially
		has supplementary alignments specified by the SA tag, return a list of
		SupplementaryAlignment objects. The list includes at least the aligned
		segment itself.
		"""
		tags = dict(aligned_segment.tags)
		cig = Cigar(aligned_segment.cigar)
		if aligned_segment.is_reverse:
			strand = '-'
			cig = cig[::-1]
		else:
			strand = '+'
		alignments = [SupplementaryAlignment(reference_name, aligned_segment.pos,
			strand, cig, aligned_segment.mapq, tags['NM'])]
		if 'SA' in tags:
			alignments.extend(parse_supplementary(tags['SA']))
		if __debug__:
			l = alignments[0].cigar.query_length(count_clipped='hard')
			for alignment in alignments[1:]:
				assert alignment.cigar.query_length(count_clipped='hard') == l
		return alignments
