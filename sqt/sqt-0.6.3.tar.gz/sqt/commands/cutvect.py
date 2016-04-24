#!/usr/bin/env python3
"""
Remove vector sequence

Limitations:
- Only one vector sequence supported.
- Only the first and last 500 bp of the vector sequence are actually searched for.
- If sequence is circular, vector might not be found.
"""
import sys
from cutadapt import align
from ..dna import reverse_complement
from .. import FastaWriter, SequenceReader, FastaReader
from argparse import ArgumentParser

def add_arguments(parser):
	arg = parser.add_argument
	arg('vector', help='FASTA with vector sequence(s)')
	arg('reads', help='FASTA/FASTQ with read')


def uncircularize(s, error_rate=0.05):
	"""
	Given a sequence s that overlaps itself (a prefix equals a suffix), return
	the sequence without the redundant suffix. To avoid random matches, the
	redundant sequence is only removed if it has a length of at least
	100 characters or 10% of the length of s, whichever is smaller.

	>>> uncircularize('hellotherehallo', error_rate=0.2)
	'hellothere'
	"""
	flags = align.START_WITHIN_SEQ2 | align.STOP_WITHIN_SEQ1

	# We cannot just align the sequence to itself since that results in a not
	# very helpful alignment, so take a prefix.
	k = int(len(s) * max(0.25, error_rate)) + 1
	prefix = s[:-k]
	result = align.locate(prefix, s, max_error_rate=error_rate, flags=flags)
	if result is None:
		return s
	pstart, pstop, sstart, sstop, matches, errors = result
	if pstop - pstart > min(100, int(0.1 * len(s))) and errors / (pstop - pstart) <= error_rate:
		# found overlap
		return s[:sstart]
	else:
		return s


def main(args=None):
	if args is None:
		parser = HelpfulArgumentParser(description=__doc__)
		add_arguments(parser)
		args = parser.parse_args()

	vectors = list(FastaReader(args.vector))
	assert len(vectors) == 1, "Only FASTA files with exactly one vector sequence currently supported"

	vector = vectors[0].sequence.upper()
	flags = align.START_WITHIN_SEQ2 | align.STOP_WITHIN_SEQ2
	prefix = vector[:500]
	suffix = vector[-500:]

	writer = FastaWriter(sys.stdout, line_length=80)
	for read in SequenceReader(args.reads):
		print('Working on', len(read.sequence), 'bp read', repr(read.name), file=sys.stderr)
		seq = read.sequence.upper()
		uncirc = uncircularize(seq)
		if len(uncirc) < len(seq):
			print('    uncircularized length:', len(uncirc), file=sys.stderr)
			circular = True
			seq = uncirc
		else:
			print('    not circular', file=sys.stderr)
			circular = False
		# The vector is either within the sequence:
		# ---XXXXXX---
		# or (due to circularity) a suffix and prefix:
		# XX------XXXX

		# So by appending the sequence to itself, we make certain that a full
		# copy of the vector sequence appears:
		# XX------XXXXXX---...

		if circular:
			s = seq + seq  # TODO 500 would be enough as long as we're only checking prefix and suffix
		else:
			s = seq
		for revcomp in False, True:
			if revcomp:
				s = reverse_complement(s)

			# Search for prefix of the vector
			result = align.locate(prefix, s, max_error_rate=0.1, flags=flags)
			if result is None:
				continue
			vstart, vstop, start, _, _, errors = result
			prefix_erate = errors / (vstop - vstart)
			assert prefix_erate <= 0.1
			print('    Prefix match found with {:.2%} errors'.format(prefix_erate), file=sys.stderr)

			# Search for suffix of the vector, but not before the prefix
			vstart, vstop, _, stop, _, errors = align.locate(suffix, s[start:], max_error_rate=0.1, flags=flags)
			suffix_erate = errors / (vstop - vstart)
			if suffix_erate > 0.1:
				print('    Suffix error rate too large.', file=sys.stderr)
				continue
			print('    Suffix match found with {:.2%} errors'.format(suffix_erate), file=sys.stderr)

			if circular:
				# We can output a single sequence.
				# Stop coordinate is relative to s[start:], so the actual
				# start is at start + stop.
				seq = s[start+stop:start+len(seq)]
				print('    Read trimmed. Length changed from', len(read.sequence), 'to', len(seq), file=sys.stderr)
				writer.write(read.name, seq)
			else:
				# Need to output two separate sequences here.
				seq1 = s[0:start]
				seq2 = s[stop:]
				print('    Read split into two. Length changed from', len(read.sequence), 'to', len(seq1), '+', len(seq2), file=sys.stderr)
				# Numbering is switched on purpose since seq1 actually
				# follows seq2 on the reference.
				writer.write(read.name + '-1', seq2)
				writer.write(read.name + '-2', seq1)
			break


if __name__ == '__main__':
	main()
