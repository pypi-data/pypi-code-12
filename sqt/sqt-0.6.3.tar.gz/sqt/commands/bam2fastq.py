#!/usr/bin/env python3
"""
Extract all reads from a BAM file that map to a certain location, but try hard
to extract them even if hard clipping is used.

TODO reverse-complementarity is ignored
TODO behavior when no region is given is not well documented
"""
__author__ = 'Marcel Martin'

import sys
import logging
from pysam import Samfile
from sqt import HelpfulArgumentParser, FastqWriter
from sqt.region import Region
from sqt.reads import AlignedRead
from sqt.cigar import Cigar

logger = logging.getLogger(__name__)

def add_arguments(parser):
	arg = parser.add_argument
	arg("--missing-quality", type=int, default=40,
		help='Quality value to use if an entry does not have qualities '
			'(default: %(default)s)')
	arg("bam", metavar="SAM/BAM", help="Name of a SAM or BAM file")
	arg("-L", '--bed', metavar="BED-FILE", action='append',
		help="BED file with regions", default=[])
	arg("region", nargs='*', help="Region")


def extract_read(aligned_read, aligned_segment, samfile):
	"""
	Return the primary AlignedSegment (the one that is not hard clipped) for
	the aligned read.
	"""
	def is_hard_clipped(segment):
		cig = Cigar(segment.cigar)
		return cig.hard_clipping_left != 0 or cig.hard_clipping_right != 0

	if not is_hard_clipped(aligned_segment):
		return aligned_segment
	for supplementary in aligned_read:
		refname, pos = supplementary.reference_name, supplementary.pos
		for segment in samfile.fetch(refname, pos, pos+1, multiple_iterators=True):
			if (segment.query_name == aligned_segment.query_name and
					not is_hard_clipped(segment)):
				return segment
	return None


def parse_bed(file):
	"""
	Yield Region objects for each line of the BED-formatted input file.
	If a line in the BED file contains less than three fields, the end coordinate
	is set to None. If it contains only one field, the start coordinate is set
	to zero.
	"""
	for line in file:
		line = line.strip()
		if line.startswith('#'):
			continue
		fields = line.split('\t')
		if len(fields) == 1:
			start = 0
			stop = None
		else:
			start = int(fields[1])
			if len(fields) == 2 or fields[2] == '':
				stop = None
			else:
				stop = int(fields[2])
		yield Region(fields[0], start, stop)



def collect_regions(region_specifications, bedpaths):
	"""
	Special case: if neither specifications nor bedpaths are given, yield a
	single None.
	"""
	if not region_specifications and not bedpaths:
		yield None
		return
	for path in bedpaths:
		with open(path) as f:
			for region in parse_bed(f):
				yield region
	for spec in region_specifications:
		yield Region(spec)


def main(args=None):
	if args is None:
		parser = HelpfulArgumentParser(description=__doc__)
		add_arguments(parser)
		args = parser.parse_args()
	missing_quality = chr(args.missing_quality + 33)
	written_reads = set()
	not_found = set()
	no_qualities = 0
	indirect = 0
	n_regions = 0
	names = set()
	regions = list()
	with FastqWriter(sys.stdout) as writer, Samfile(args.bam) as sf:
		for region in collect_regions(args.region, args.bed):
			if region is None:
				region_iter = sf
			else:
				region_iter = sf.fetch(region.reference, region.start, region.stop)
			n_regions += 1
			for record in region_iter:
				names.add(record.query_name)
				if region is None:
					if record.is_supplementary or record.is_secondary or record.is_unmapped:
						continue
					if record.mapping_quality < 1:
						continue
					if record.query_alignment_length < 1000:
						continue
					segment = record
				else:
					if record.is_unmapped:
						assert False, 'shouldn’t happen'
						continue
					assert record.cigar is not None
					if record.query_name in written_reads or record.query_name in not_found:
						continue
					aligned_read = AlignedRead(record, sf.getrname(record.tid))
					segment = extract_read(aligned_read, record, sf)
					if segment is None:
						not_found.add(record.query_name)
						continue
					if segment is not record:
						indirect += 1
					assert segment.query_name == record.query_name
				if segment.query_qualities is not None:
					qualities = ''.join(chr(c+33) for c in segment.query_qualities)
				else:
					qualities = missing_quality * len(segment.query_sequence)
					no_qualities += 1
				writer.write(segment.query_name, segment.query_sequence, qualities)
				written_reads.add(record.query_name)

	logger.info('%s unique read names in %s region(s)', len(names), n_regions)
	logger.info('%s entries written (%s found indirectly)', len(written_reads), indirect)
	logger.info('%s without qualities', no_qualities)


if __name__ == '__main__':
	main()
