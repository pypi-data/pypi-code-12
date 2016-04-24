#!/usr/bin/env python3
"""
Efficiently extract a region from a FASTA file. When an .fai index of the file
is available, only the necessary parts of the file are read. If the index is
not available, the entire file is read into memory first. Create an index (.fai
file) with "samtools faidx".

The result is printed in FASTA format to standard output.

Regions are specified in the format "[rc:]name[:start-stop]".
If "start" and "stop" are omitted, the whole sequence is returned.
Coordinates are 1-based and both endpoints of the interval are included.
A region specification may be prefixed by 'rc:' in order to output the reverse
complement of the specified region. It must hold that start <= stop,
even when reverse complements are requested. If it does not hold, the output
sequence is empty.

Please be aware that samtools faidx uses only the part of the sequence name up to, but not including,
the first whitespace character. That is, if an entry in your FASTA file looks like this:

>seq1 this is a sequence

Then the identifier for this sequence is simply 'seq1'. For consistency, this
convention is also followed when the .fai file is not used.


Examples
--------

Extract chromosome 1 from a FASTA file named hg19.fa:

    fastaextract hg19.fa chr1

Extract the first 200 nucleotides from chromosome 1 in hg19.fa:

    fastaextract hg19.fa chr1:1-200

Extract the reverse complement of the bases 201 up to the end of chr1:

    fastaextract hg19.fa rc:chr1:201-

TODO
* create a .fai index on the fly instead of reading the full file into memory.
* check for duplicate names when no index used
"""


import os.path
import sys
import mmap

from .. import HelpfulArgumentParser
from ..io.fasta import (FastaReader, NonIndexedFasta, IndexedFasta, FastaWriter,
	FastaIndexMissing)
from ..io.xopen import xopen
from ..dna import reverse_complement
from ..region import Region

__author__ = "Marcel Martin"


def main():
	if sys.version < '2.7':
		print("Sorry, Python version >= 2.7 required!", file=sys.stderr)
		sys.exit(1)
	parser = HelpfulArgumentParser(description=__doc__)
	parser.add_argument("--width", "-w", type=int, default=80,
		help="Characters per line in output FASTA (default: %(default)s). "
			"Set to 0 to disallow line breaks entirely.")
	parser.add_argument("fasta", metavar="FASTA", help="The FASTA file")
	parser.add_argument("region", metavar="REGION", nargs='+')
	args = parser.parse_args()
	if args.width == 0:
		args.width = None

	try:
		fasta = IndexedFasta(args.fasta)
	except FastaIndexMissing:
		if os.path.getsize(args.fasta) > 1024 ** 3:  # 1 GiB
			print("ERROR: The file is very large and no index exists, "
				"please create an index with 'samtools faidx'.", file=sys.stderr)
			sys.exit(1)
		fasta = NonIndexedFasta(args.fasta)

	writer = FastaWriter(sys.stdout, line_length=args.width)
	regions = [ Region(s) for s in args.region ]
	for region in regions:
		sequence = fasta[region.reference][region.start:region.stop]
		if region.is_reverse_complement:
			sequence = reverse_complement(sequence)
		if sys.version > '3':
			sequence = sequence.decode()
		writer.write(str(region), sequence)


if __name__ == '__main__':
	main()
