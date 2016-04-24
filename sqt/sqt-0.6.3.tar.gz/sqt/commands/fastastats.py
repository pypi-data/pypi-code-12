#!/usr/bin/env python3
"""
Print lots of statistics about one or more FASTA or FASTQ files.

TODO
- computation of contig N50 is relatively slow
"""
import sys
import os
import subprocess
from collections import Counter
from .. import HelpfulArgumentParser, SequenceReader, IndexedFasta
from ..dna import n_intervals, intervals_complement
from ..math import n50, frequency_median, frequency_n50

__author__ = "Marcel Martin"


def byte_frequencies(s):
	return Counter(s)


try:
	from sqt._helpers import byte_frequencies
except:
	pass


def print_statistics(lengths, contig_lengths, shortest=None, longest=None, genome_size=None, character_frequencies=None):
	"""
	lengths -- a dictionary that maps length to frequency (Counter object)
	"""
	n = sum(lengths.values())
	print('No. of sequences: {:11,}'.format(n))
	if n == 0:
		return

	total = sum(length * count for length, count in lengths.items())
	print('Total length:   {:13,}'.format(total))

	min_length, max_length = min(lengths), max(lengths)
	if shortest:
		print('Minimum length: {:13,} in entry "{}"'.format(min_length, shortest))
	else:
		print('Minimum length: {:13,}'.format(min_length))
	if longest:
		print('Maximum length: {:13,} in entry "{}"'.format(max_length, longest))
	else:
		print('Maximum length: {:13,}'.format(max_length))

	print('Average length: {:16.2f}'.format(total / n))
	print('Median length:  {:13,}'.format(frequency_median(lengths)))
	print('Scaffold N50:   {:13,}'.format(frequency_n50(lengths)))
	if genome_size:
		print('Scaffold NG50:  {:13,}'.format(frequency_n50(lengths, genome_size=genome_size)))

	if contig_lengths:
		lengths = contig_lengths
		min_length, max_length = min(lengths), max(lengths)
		print()
		n_contigs = sum(lengths.values())
		print('Number of contigs:     {:13,}'.format(n_contigs))
		total_c = sum(length * count for length, count in lengths.items())
		print('Total contig length:   {:13,}'.format(total_c))
		print('Minimum contig length: {:13,}'.format(min_length))
		print('Maximum contig length: {:13,}'.format(max_length))
		print('Average contig length: {:16.2f}'.format(total_c / n_contigs))
		print('Median contig length:  {:13,}'.format(frequency_median(lengths)))
		print('Contig N50:            {:13,}'.format(frequency_n50(lengths)))

	if character_frequencies:
		print()
		print("Character distribution (<char> <count> <percentage>):")
		assert total == sum(character_frequencies.values())
		acgt = 0
		gc = 0
		for upper, lower in (b'Aa', b'Cc', b'Gg', b'Tt'):
			freq = character_frequencies[upper] + character_frequencies[lower]
			if upper in b'GC':
				gc += freq
			print(chr(upper), '    {:14,} {:6.1%}'.format(freq, freq / total))
			acgt += freq
		other = sum(character_frequencies.values()) - acgt
		print('other {:14,} {:6.2%}'.format(other, other / total))
		print('ACGT  {:14,} {:6.2%}'.format(acgt, acgt / total))
		print('GC    {:14,} {:6.2%} (of ACGT)'.format(gc, gc / (total - other)))


def filter_short_intervals(intervals, minimum_length):
	for start, stop in intervals:
		if stop - start >= minimum_length:
			yield (start, stop)


def fasta_fastq_iter(path):
	with SequenceReader(path, 'rb') as reader:
		for record in reader:
			seq = record.sequence #.upper()
			yield (record.name, len(seq), seq)


def indexed_fasta_iter(path):
	with IndexedFasta(path) as f:
		for index_entry in f.index.values():
			yield (index_entry.name, index_entry.length, None)


def stats(path, tolerable_gapsize, detailed):
	"""
	Determine scaffold lengths, contig lengths and character frequencies.

	Return a tuple (scaffold_lengths, contig_lengths, character_frequencies).
	"""
	scaffold_lengths = Counter()
	contig_lengths = Counter()
	nucleotides = Counter()  # nucleotide frequencies
	shortest = None
	longest = None
	min_length = float('+inf')
	max_length = -1
	if not detailed and os.path.exists(path + '.fai'):
		it = indexed_fasta_iter(path)
	else:
		it = fasta_fastq_iter(path)
	for (name, length, sequence) in it:
		scaffold_lengths[length] += 1
		if length < min_length:
			min_length = length
			shortest = name
		if length > max_length:
			max_length = length
			longest = name
		if detailed and sequence is not None:
			nucleotides += byte_frequencies(sequence)
			intervals = intervals_complement(
				filter_short_intervals(n_intervals(sequence, ord(b'N')), tolerable_gapsize), length)
			for start, stop in intervals:
				contig_lengths[stop - start] += 1

	return scaffold_lengths, contig_lengths, shortest, longest, nucleotides


def get_argument_parser():
	parser = HelpfulArgumentParser(description=__doc__)
	add = parser.add_argument
	add('--detailed', '-d', default=False, action='store_true',
		help='Print information about the sequences themselves, '
			'such as the character distribution and contig N50.')
	add('--genome-size', '-g', type=int, default=None,
		help='Estimated genome size. If given, also NG50 in addition to N50 is computed.')
	add('--tolerable-gapsize', '-t', type=int, default=10,
		help='A stretch of at most this many "N"s is not counted as a gap '
		'separating contigs.')
	add('fastaq', nargs='+', metavar='FASTA/FASTQ',
		help='Input FASTA or FASTQ file(s) (may be gzipped).')
	return parser


def main():
	parser = get_argument_parser()
	args = parser.parse_args()

	overall_frequencies = Counter()
	overall_lengths = Counter()
	if not args.detailed:
		character_frequencies = None
		contig_lengths = None
	for path in args.fastaq:
		print("## File:", path)
		scaffold_lengths, contig_lengths, shortest, longest, character_frequencies = \
			stats(path, args.tolerable_gapsize, detailed=args.detailed)
		overall_frequencies += character_frequencies
		print_statistics(scaffold_lengths, contig_lengths, shortest, longest, args.genome_size, character_frequencies)
		overall_lengths += scaffold_lengths
	if len(args.fastaq) > 1:
		print("## Summary of", len(args.fastaq), "files")
		print_statistics(overall_lengths, None, None, None, args.genome_size, overall_frequencies if args.detailed else None)


if __name__ == '__main__':
	main()
