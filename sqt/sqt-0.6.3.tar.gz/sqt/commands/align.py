#!/usr/bin/env python3
"""
Compare two strings
"""
from sqt import HelpfulArgumentParser
import sys
import os
from collections import namedtuple
from cutadapt import align
from sqt import FastaReader
from sqt.align import globalalign, GlobalAlignment
from sqt.dna import reverse_complement

__author__ = "Marcel Martin"


Alignment = namedtuple('Alignment', 'start1 stop1 start2 stop2 matches errors')

def add_arguments(parser):
	arg = parser.add_argument
	arg('--semiglobal', '--overlap', action='store_true', default=False,
		help='Run a semi-global alignment (for detecting overlaps). '
		'Default: global alignment.')
	arg('--max-error-rate', '-e', type=float, default=None,
		help='Switch to cutadapt algorithm (also enables --semiglobal). '
		'No alignment will be printed.')
	arg('--reverse-complement', '--rc', action='store_true',
		default=False,
		help='Run the alignment also with the reverse-complement of the second '
		'sequence')
	arg('--merge', action='store_true', default=False,
		help='Output a merged sequence (also enables --semiglobal)')
	arg('sequence1', help='Sequence or path to FASTA file. If FASTA, only the first sequence is used.')
	arg('sequence2', help='Sequence or path to FASTA file. If FASTA, only the first sequence is used.')


def print_numbers(sequence1, sequence2, alignment, overlap):
	print()
	print('Length of sequence 1:', len(sequence1))
	print('Length of sequence 2:', len(sequence2))
	print('Errors in alignment:', alignment.errors)
	if overlap:
		print('Length of overlap in sequence 1:', alignment.stop1 - alignment.start1)
		print('Length of overlap in sequence 2:', alignment.stop2 - alignment.start2)
	if hasattr(alignment, 'matches'):
		print('Matches:', alignment.matches)


def load_sequence(path_or_sequence):
	if os.path.exists(path_or_sequence):
		with FastaReader(path_or_sequence) as fr:
			sequence = next(iter(fr)).sequence
	else:
		sequence = path_or_sequence
	return sequence


def main(args=None):
	if args is None:
		parser = HelpfulArgumentParser(description=__doc__)
		add_arguments(parser)
		args = parser.parse_args()
	sequence1 = load_sequence(args.sequence1)
	sequence2 = load_sequence(args.sequence2)

	sequences = [ (False, sequence2) ]
	if args.reverse_complement:
		sequences.append((True, reverse_complement(sequence2)))

	if args.merge:
		args.semiglobal = True

	# credit: http://stackoverflow.com/questions/566746/
	rows, columns = os.popen('stty size', 'r').read().split()
	columns = int(columns)

	for revcomp, sequence2 in sequences:
		if revcomp:
			print('Alignment with reverse-complemented sequence 2:')
		else:
			print('Alignment:')
		print()
		if args.max_error_rate is not None:
			flags = align.SEMIGLOBAL
			result = align.locate(sequence1.upper(), sequence2.upper(), max_error_rate=args.max_error_rate, flags=flags)
			if result is None:
				print('No alignment found')
				continue
			alignment = Alignment(*result)
			print_numbers(sequence1, sequence2, alignment, overlap=True)
		else:
			alignment = GlobalAlignment(sequence1.upper(), sequence2.upper(), semiglobal=args.semiglobal)
			alignment.print(width=columns, gap_char='-')
			print_numbers(sequence1, sequence2, alignment, args.semiglobal)

		if args.merge:
			merged = sequence1[0:alignment.start1]
			merged += sequence2[0:alignment.start2]
			merged += sequence1[alignment.start1:alignment.stop1]
			merged += sequence1[alignment.stop1:]
			merged += sequence2[alignment.stop2:]
			print('Merged (length {}):'.format(len(merged)), merged)


if __name__ == '__main__':
	main()
