#!/usr/bin/env python3
"""
Repair a BAM file that (incorrectly) contains phred64-encoded qualities.
BAM files must encode their quality values in phred33.

Output is written in SAM format to standard output.
"""
from sqt import HelpfulArgumentParser
from pysam import Samfile

__author__ = "Marcel Martin"

PHRED_64_TO_33_TRANS = bytes.maketrans(bytes(range(64, 64+100)), bytes(range(33, 33+100)))

def get_argument_parser():
	parser = HelpfulArgumentParser(description=__doc__)
	add = parser.add_argument
	add('bam', help='Input BAM file')
	return parser


def main():
	parser = get_argument_parser()
	args = parser.parse_args()

	with Samfile(args.bam) as infile:
		with Samfile('-', 'wh', template=infile) as outfile:
			for record in infile:
				record.qual = record.qual.translate(PHRED_64_TO_33_TRANS)
				outfile.write(record)


if __name__ == '__main__':
	main()
