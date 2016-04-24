#!/usr/bin/env python3
"""
Check whether two FASTQ files contain paired-end reads.
The corresponding reads in FASTQ1 and FASTQ2 must have
the same names. A read name suffix of "/1" in FASTQ1 and
a suffix of "/2" in FASTQ is ignored.

The read name is only the part before the first space character.

FASTQ1 and FASTQ2 may be gzipped.

The exit code is nonzero on failure, zero otherwise.
"""
import sys
from itertools import zip_longest
from sqt.io.fasta import FastqReader
from sqt import HelpfulArgumentParser

__author__ = "Marcel Martin"


def check(fastq1, fastq2, limit=None):
	"""
	Raise ValueError if given FASTQ files seem to be paired incorrectly.
	"""
	with FastqReader(fastq1) as fastq1:
		with FastqReader(fastq2) as fastq2:
			n = 1
			for record1, record2 in zip_longest(fastq1, fastq2):
				if record1 is None:
					raise ValueError("File 2 is longer than file 1")
				if record2 is None:
					raise ValueError("File 1 is longer than file 2")
				name1 = record1.name.split(' ', 1)[0]
				if name1.endswith("/1"):
					name1 = name1[:-2]
				name2 = record2.name.split(' ', 1)[0]
				if name2.endswith("/2"):
					name2 = name2[:-2]
				if name1 != name2:
					raise ValueError("Incorrect names at record no. {}: '{}' != '{}'".format(n, name1, name2))
				if n == limit:
					return
				n += 1


def main():
	parser = HelpfulArgumentParser(description=__doc__)
	parser.add_argument("-n", "--limit", type=int, default=1000,
		help="Only check the first N records. Set to zero to check the entire file (default: %(default)s)")
	parser.add_argument("--quiet", "-q", action='store_true', default=False,
		help="Don't print anything, just set the exit code.")
	parser.add_argument('fastq1', metavar='FASTQ1',
		help='File with first read of paired-end reads')
	parser.add_argument('fastq2', metavar='FASTQ2',
		help='File with second read of paired-end reads')
	args = parser.parse_args()

	if not args.quiet:
		def message(*args, **kwargs):
			print(*args, **kwargs)
	else:
		def message(*args, **kwargs):
			pass

	try:
		check(args.fastq1, args.fastq2, args.limit)
	except ValueError as e:
		message(e)
		sys.exit(1)
	message("OK")


if __name__ == '__main__':
	main()
