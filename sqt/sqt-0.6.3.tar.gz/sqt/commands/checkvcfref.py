#!/usr/bin/env python3
"""
Read in a file with variants (typically VCF) and check if the given
reference allele matches what is actually in the reference sequence
at the given position.
"""
import sys
import csv

from sqt import HelpfulArgumentParser, IndexedFasta

__author__ = "Marcel Martin"


def main():
	parser = HelpfulArgumentParser(description=__doc__)
	arg = parser.add_argument
	arg("reference", help="Reference file in FASTA format. An associated .fai index file must exist.")
	arg("variantfile", help="Input (VCF) file with variants.")
	args = parser.parse_args()

	reference = IndexedFasta(args.reference)
	with open(args.variantfile) as f:
		reader = csv.reader([row for row in f if row[0] != '#'], delimiter='\t')
		n = 0
		for row in reader:
			n += 1
			chrom = row[0]
			if chrom.startswith('chr'):
				chrom = chrom[3:]
			pos = int(row[1]) - 1
			ref = row[3]
			actual = reference.get(chrom)[pos:pos+len(ref)].decode()
			if not actual == ref:
				print('Problem with record no.', n, 'found:')
				print('CHROM={} POS={} REF={}'.format(chrom, pos+1, ref))
				print('Reference sequence in FASTA file is:', actual)
				sys.exit(1)
		else:
			print((n, 'records checked, everything ok.'))
			sys.exit(0)


if __name__ == '__main__':
	main()
