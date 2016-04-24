#!/usr/bin/env python3
"""
Search for a IUPAC string in the sequences of a FASTA file.

Prints matching entries in the fasta file to standard output.
If <FASTA> is not provided, read from standard input.

If output is a terminal, the first occurrence of the pattern
in each sequence is highlighted.
"""
import sys
import re
from sqt import HelpfulArgumentParser
from sqt.io.fasta import FastaReader
from sqt.io.xopen import xopen
from sqt.ansicolor import red, lightred

__author__ = "Marcel Martin, Tobias Marschall"


def add_arguments(parser):
	arg = parser.add_argument
	arg("-d", "--description", action="store_true", default=False,
		help="Search the description/comment fields of the FASTA file instead "
		"of the sequences. If given, the pattern is interpreted as a regular "
		"expression, not as a IUPAC pattern. (default: %(default)s)")
	arg("pattern")
	arg("fasta", nargs='?', const=None)


def iupac_to_regex(iupac):
	"""
	Converts a IUPAC string with wildcards to a regular expression.
	"""
	wildcards = {
		"R": "AG",
		"Y": "CT",
		"S": "CG",
		"W": "AT",
		"K": "GT",
		"M": "AC",
		"B": "CGT",
		"D": "AGT",
		"H": "ACT",
		"V": "ACG",
		"N": "ACGT",
		"X": "ACGT" }
	regex = ""
	for c in iupac.upper():
		if c in "ACGT":
			regex += c
		elif c in wildcards:
			regex += "[" + wildcards[c] + "]"
		else:
			raise ValueError("don't know how to handle character %s" % c)
	return regex



def main(args=None):
	if args is None:
		parser = HelpfulArgumentParser(description=__doc__)
		add_arguments(parser)
		args = parser.parse_args()

	if args.fasta is None:
		infile = sys.stdin
	else:
		infile = xopen(args.fasta)

	# whether to use color in output
	color = sys.stdout.isatty()

	if args.description:
		reg = args.pattern
		color = False
	else:
		reg = iupac_to_regex(args.pattern.upper())
	regex = re.compile(reg)
	for record in FastaReader(infile):
		seq = record.sequence
		#print(desc, seq)
		if args.description:
			match = regex.search(record.name)
		else:
			match = regex.search(record.sequence.upper())
		if match:
			print('>', record.name, sep='')
			if color:
				print(seq[0:match.start()] + lightred(seq[match.start():match.end()]) + seq[match.end():])
			else:
				print(seq)
			match = regex.search(seq.upper())


if __name__ == '__main__':
	main()
