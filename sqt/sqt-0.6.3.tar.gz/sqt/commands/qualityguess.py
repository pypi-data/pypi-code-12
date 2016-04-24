#!/usr/bin/env python3
"""
Guess quality encoding of one or more FASTA files.
"""
import sys
import os
import subprocess
from collections import Counter
from sqt.io.fasta import FastqReader, guess_quality_base
from sqt import HelpfulArgumentParser

__author__ = "Marcel Martin"


def get_argument_parser():
	parser = HelpfulArgumentParser(description=__doc__)
	add = parser.add_argument
	add('--verbose', '-v', default=False, action='store_true',
		help='Print histogram of found characters')
	add('--limit', '-n', default=10000, type=int,
		help='Inspect the first LIMIT records in the FASTQ file (default: %(default)s)')
	add('fastq', nargs='+', metavar='FASTQ',
		help='Input FASTQ files (may be gzipped).')
	return parser


def main():
	parser = get_argument_parser()
	args = parser.parse_args()

	for path in args.fastq:
		if args.verbose:
			print('## File:', path)
		else:
			print(path, end='')
		freqs, guess = guess_quality_base(path)
		if args.verbose:
			print()
			print('character ASCII frequency')
			for c in sorted(freqs):
				print("{} {:3} {:7}".format(chr(c), c, freqs[c]))
			print()
		else:
			print(' is ', end='')
		guess = { 33: 'phred33', 64: 'phred64', None: 'unknown'}[guess]
		if args.verbose:
			print("Quality value range assuming phred33: {}..{}".format(min(freqs) - 33, max(freqs) - 33))
			print("Quality value range assuming phred64: {}..{}".format(min(freqs) - 64, max(freqs) - 64))
			print("This is probably", guess)
		else:
			print(guess)


if __name__ == '__main__':
	main()
