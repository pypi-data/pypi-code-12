#!/usr/bin/env python3
"""
Simulate reads that optionally contain adapter sequences.
"""
import sys
from random import randint, random, seed

from sqt import HelpfulArgumentParser
from sqt.io.fasta import IndexedFasta

__author__ = "Marcel Martin"

LENGTH = 100

#adapter = 'GCCTAACTTCTTAGACTGCCTTAAGGACGT'
#adapter_prob = 0.5


def main():
	parser = HelpfulArgumentParser(description=__doc__)
	arg = parser.add_argument
	arg("--length", "-l", type=int, default=100)
	arg("--seed", type=int, default=None, help="seed for random number generator")
	#arg("--minimum-length", "-m", type=int, default=100)
	#arg("--maximum-length", "-M", type=int, default=100)
	arg("--adapter", "-a", default=None,
		help="Add an adapter")
	arg("--probability", "-p", default=0.5,
		help="Fraction of reads (approximate) that should contain the adapter")
	arg("n", type=int, help="Number of reads")
	arg("fasta", #nargs='?',
		help="FASTA file from which reads are sampled. Only the first chromosome (entry) is used.")
	arg("chromosome", help="chromosome that is picked from the FASTA file")

	args = parser.parse_args()
	if args.seed is not None:
		seed(args.seed)
	adapter = args.adapter
	adapter_prob = args.probability
	length = args.length
	fasta = IndexedFasta(args.fasta)
	chrom = fasta.get(args.chromosome)
	i = 0
	while i < args.n:
		start = randint(0, len(chrom) - 100)
		seq = chrom[start:start+length]
		if b'N' in seq:
			continue
		i += 1
		seq = seq.decode('ascii')
		if adapter is not None and random() < adapter_prob:
			pos = randint(0, length-1)
			seq = seq[:pos] + adapter + seq[pos:]
			seq = seq[:length]
			extra = ' adapterpos={}'.format(pos+1)
		else:
			extra = ''
		print('>r{} {}:{}-{}{}'.format(i, args.chromosome, start+1, start+length, extra))
		print(seq)


	#ALPHABET = 'ACGT'
	#for i in range(args.n):
		#l = randint(args.minimum_length, args.maximum_length)
		#seq = ''.join(choice('ACGT') for _ in range(l))
		#print(">r{0}\n{1}".format(i+1, seq))


if __name__ == '__main__':
	main()
