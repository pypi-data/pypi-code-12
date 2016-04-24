#!/usr/bin/env python3
"""
Print q-gram (also called k-mer) frequencies in a FASTA or FASTQ file.

The result is a list of q-grams and their counts, sorted by counts from
least to most frequent.
"""
import sys
from collections import Counter

from sqt import HelpfulArgumentParser
from sqt import SequenceReader

__author__ = "Marcel Martin"

def q_grams(s, q):
	"""yield all q-grams in s"""
	for i in range(len(s) - q):
		yield s[i:i+q]


def add_arguments(parser):
	arg = parser.add_argument
	arg("-q", default=4,
		help="length of the q-grams (also called k-mers) (default: %(default)s)")
	arg("path", metavar='FASTA/FASTQ', help="input FASTA or FASTQ file")


def main(args=None):
	if args is None:
		parser = HelpfulArgumentParser(description=__doc__)
		add_arguments(parser)
		args = parser.parse_args()

	counts = Counter()
	with SequenceReader(args.path) as reader:
		for record in reader:
			counts.update(q_grams(record.sequence, args.q))
	for elem, count in counts.most_common()[::-1]:
		print(elem, count)


if __name__ == '__main__':
	main()
