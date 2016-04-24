#!/usr/bin/env python3
"""
Read FASTA-formatted data and replace characters in <FROM-CHARACTERS>
with corresponding characters in <TO-CHARACTERS>.

If the name of a FASTA file is not given, read from standard input.

This is similar to the unix 'tr' command, except that FASTA
comment lines remain unchanged.

You can also translate the sequences within FASTQ files by setting
--format=fastq.

Example (replace C with T and c with t):

%(prog)s translate Cc Tt input.fa > output.fa
"""
import sys
#import string
from sqt import HelpfulArgumentParser
from sqt.io.fasta import FastqReader, FastqWriter, FastaWriter, FastaReader

__author__ = "Marcel Martin"


def main():
	parser = HelpfulArgumentParser(description=__doc__)
	parser.add_argument("--format", choices=('fasta', 'fastq'), default='fasta')
	parser.add_argument("fromchars", metavar="FROM-CHARACTERS")
	parser.add_argument("tochars", metavar="TO-CHARACTERS")
	parser.add_argument("file", nargs='?', default='-')
	args = parser.parse_args()
	trans = bytes.maketrans(args.fromchars.encode('ascii'), args.tochars.encode('ascii'))

	if args.format == 'fasta':
		fw = FastaWriter(sys.stdout)
		with FastaReader(args.file) as fr:
			for record in fr:
				record.sequence = record.sequence.translate(trans)
				fw.write(record)
	else:
		fw = FastqWriter(sys.stdout)
		with FastqReader(args.file) as fr:
			for record in fr:
				record.sequence = record.sequence.translate(trans)
				fw.write(record)


if __name__ == '__main__':
	main()
