#!/usr/bin/env python3
"""
Compute per-reference statistics given a BAM file and a matching FASTA reference.

The output is a tab-separated table with the following columns:

chromosome:
  reference/scaffold/chromosome name

gc:
  GC content (number of found G, C bases divided by the number of
  found A, C, G, T bases)

length:
  length of the reference

non_acgt:
  number of characters that are not one of A, C, G, T

bases:
  total number of bases aligned to the reference, not counting those aligning
  to bases that are neither A, C, G nor T

avg_cov:
  average coverage = bases / (length - non_acgt)

median_cov:
  median coverage (as above, coverage over non-ACGT bases is not counted)

TODO:
- optionally print summary over all reference sequences
"""
__author__ = 'Marcel Martin'

import sys
from collections import Counter, namedtuple
from pysam import Samfile
from sqt import HelpfulArgumentParser
from sqt._helpers import byte_frequencies
from sqt.math import frequency_median
from sqt.io.fasta import IndexedFasta

Info = namedtuple('Info', 'length acgt_length bases acgt_bases median_coverage acgt_median_coverage gc')


def collect_info(samfile, fasta, name, mask):
	sequence = fasta.get(name)[:]
	length = len(sequence)
	freqs = byte_frequencies(sequence)
	assert length == samfile.lengths[samfile.gettid(name)]
	acgt_length = sum(freqs[c] for c in b'ACGTacgt')
	gc = sum(freqs[c] for c in b'GCgc')

	# Get coverage
	acgt_bases = 0
	bases = 0
	coverages = Counter()
	acgt_coverages = Counter()
	for column in samfile.pileup(name, stepper='all', mask=mask):
		n = column.n
		if sequence[column.pos] in b'ACGTacgt':
			acgt_bases += n
			acgt_coverages[n] += 1
		bases += n
		coverages[n] += 1

	# Compute medians
	assert coverages[0] == 0
	assert acgt_coverages[0] == 0
	coverages[0] = length - sum(coverages.values())
	acgt_coverages[0] = acgt_length - sum(acgt_coverages.values())

	median_coverage = frequency_median(coverages)
	acgt_median_coverage = frequency_median(acgt_coverages)

	return Info(
		length=length,
		acgt_length=acgt_length,
		bases=bases,
		acgt_bases=acgt_bases,
		median_coverage=median_coverage,
		acgt_median_coverage=acgt_median_coverage,
		gc=gc,
	)


def main():
	parser = HelpfulArgumentParser(description=__doc__)
	parser.add_argument('--mask', default='0x504',
		help="Exclude reads in which flags have one of the bits in MASK set. "
			"Default is 0x504, that is, exclude unmapped reads (0x4), "
			"secondary alignments (0x100) and PCR/optical duplicates (0x400).")
	parser.add_argument("fasta", metavar="FASTA", help="path to reference FASTA file")
	parser.add_argument("bam", metavar="BAM", help="path to BAM file")
	args = parser.parse_args()
	try:
		args.mask = int(args.mask, base=0)
	except ValueError:
		parser.error('Could not interpret mask value "{}"'.format(args.mask))

	print('chromosome', 'gc', 'length', 'non_acgt', 'bases', 'avg_cov', 'median_cov', sep='\t')
	with Samfile(args.bam) as samfile, IndexedFasta(args.fasta) as fasta:
		reference_names = samfile.references
		for name in reference_names:
			info = collect_info(samfile, fasta, name, args.mask)
			print(
				name,
				"{:.4f}".format(info.gc / info.acgt_length),
				info.length,
				info.length - info.acgt_length,
				info.acgt_bases,
				"{:.3f}".format(info.acgt_bases / info.acgt_length),
				info.acgt_median_coverage,
				sep='\t',
			)


if __name__ == '__main__':
	main()
