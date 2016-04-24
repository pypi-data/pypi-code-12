#!/usr/bin/env python3
"""
Read in reads in FASTA format, insert an adapter sequence at a random
position, shorten the read to its original length, and write it out.

An annotation is added to the read description that describes the
adapter position, such as "adapterpos=17". The position is 1-based.
"""
import sys
from random import randint, random, seed, choice

from sqt import HelpfulArgumentParser
from sqt.io.fasta import FastaReader

__author__ = "Marcel Martin"

#adapter = 'GCCTAACTTCTTAGACTGCCTTAAGGACGT'

def mutate_sequence(seq, rate=0.1, alphabet='ACGT', indels=False, indel_rate=0.1):
	"""
	If indels is True, the mutation_rate is equally split up between insertions,
	deletions and substitutions.
	"""
	mutated = []
	charpos = dict( (c,i) for (i,c) in enumerate(alphabet))
	for c in seq:
		c = c.upper()
		r = random()
		if indels and r < 0.5 * rate * indel_rate:
			# insertion
			mutated.append(choice(alphabet))
			mutated.append(c)
		elif indels and r < rate * indel_rate:
			# deletion
			pass
		elif r < rate:
			# mutate base
			d = alphabet[(charpos[c] + randint(1, len(alphabet)-1)) % len(alphabet)]
			assert d != c
			mutated.append(d)
		else:
			# no change
			mutated.append(c)
	return ''.join(mutated)


def main():
	parser = HelpfulArgumentParser(description=__doc__)
	arg = parser.add_argument
	arg("--seed", type=int, default=None, help="seed for random number generator")
	arg("--erate", type=float, default=None,
		help="error rate for simulated errors, no indels (default: no errors)")
	arg("--adapter", "-a", default='GCCTAACTTCTTAGACTGCCTTAAGGACGT',
		help="Adapter sequence")
	arg("--probability", "-p", default=0.5,
		help="Fraction of reads (approximate) that should contain the adapter")
	arg("fasta", help="Input FASTA file. Use '-' for standard input.")

	args = parser.parse_args()
	if args.seed is not None:
		seed(args.seed)
	adapter = args.adapter
	adapter_prob = args.probability
	with FastaReader(args.fasta) as reader:
		for read in reader:
			if random() < adapter_prob:
				if args.erate is not None:
					a = mutate_sequence(adapter, args.erate, indels=False)
				else:
					a = adapter
				l = len(read)
				pos = randint(0, l-1)
				seq = read.sequence
				seq = seq[:pos] + a + seq[pos:]
				read.sequence = seq[:l]
				read.name = read.name + ' adapterpos={}'.format(pos+1)
			print('>{}\n{}'.format(read.name, read.sequence))



if __name__ == '__main__':
	main()
