#!/usr/bin/env python3
"""
Print a report for individual reads in a SAM/BAM file.
"""
__author__ = 'Marcel Martin'

import sys
from collections import Counter, namedtuple, defaultdict
from itertools import islice
from contextlib import ExitStack
from pysam import Samfile
from sqt import HelpfulArgumentParser, Cigar, cigar
from sqt.region import Region

from .bamstats import AlignedRead, print_coverage_report

def add_arguments(parser):
	arg = parser.add_argument
	arg('--minimum-length', '-m', type=int, default=1,
		help='Minimum read length. Ignore reads that are shorter. Default: %(default)s')
	arg('--quality', '-q', type=int, default=0,
		help='Minimum mapping quality (default: %(default)s')
	arg('--minimum-cover-fraction', metavar='FRACTION', type=float, default=0.01,
		help='Alignment must cover at least FRACTION of the read to appear in the cover report. (%(default)s)')
	arg("bam", metavar="SAM/BAM", help="Name of a SAM or BAM file")
	arg("region", help="Region")


def main(args=None):
	if args is None:
		parser = HelpfulArgumentParser(description=__doc__)
		add_arguments(parser)
		args = parser.parse_args()
	region = Region(args.region)
	n_records = 0
	seen_reads = set()
	with Samfile(args.bam) as sf:
		for record in sf.fetch(region.reference, region.start, region.stop):
			if record.query_length < args.minimum_length:
				continue
			n_records += 1
			if record.is_unmapped:
				unmapped += 1
				unmapped_bases += len(record.seq)
				continue
			if record.mapq < args.quality:
				continue
			assert record.cigar is not None

			if not record.query_name in seen_reads:
				aligned_read = AlignedRead(record, sf.getrname(record.tid))
				print_coverage_report(aligned_read, minimum_cover_fraction=args.minimum_cover_fraction)
				seen_reads.add(record.query_name)


if __name__ == '__main__':
	main()
