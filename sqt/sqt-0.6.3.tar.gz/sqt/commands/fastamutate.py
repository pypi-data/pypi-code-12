#!/usr/bin/env python3
"""
Mutate nucleotides in a FASTA file. Write modified sequences to standard output.
"""
import sys
import random
from sqt import HelpfulArgumentParser
from sqt.io.fasta import FastaReader, FastaWriter

__author__ = "Marcel Martin"


def mutate_sequence(seq, rate=0.1, alphabet='ACGT', indels=True, indel_rate=0.1):
	"""
	TODO this model is not very sophisticated
	"""
	other_chars = {}
	for c in alphabet:
		other_chars[c] = alphabet.replace(c, '')
	mutated = []
	n_sub = 0
	n_indel = 0
	for c in seq:
		c = c.upper()
		r = random.random()
		if r < rate:
			# mutate base
			d = random.choice(other_chars.get(c, 'ACGT'))
			mutated.append(d)
			n_sub += 1
		elif indels and r < (rate + 0.5 * indel_rate):
			# insertion
			mutated.append(random.choice(alphabet))
			mutated.append(c)
			n_indel += 1
		elif indels and r < (rate + indel_rate):
			n_indel += 1
			# deletion
			pass
		else:
			# no change
			mutated.append(c)
	return ''.join(mutated), n_sub, n_indel


def main():
	parser = HelpfulArgumentParser(description=__doc__)
	parser.add_argument("--rate", type=float, default=0.03,
		help="Substitution rate (default: %(default)s)")
	parser.add_argument("--indel-rate", type=float, default=0.0005,
		help="Indel rate (default: %(default)s)")
	parser.add_argument("--seed", type=int, default=None,
		help="Set random seed for reproducible runs (default: use different seed each run)")
	parser.add_argument("fasta", metavar='FASTA-file', help="Input FASTA file")
	args = parser.parse_args()

	if args.seed is not None:
		random.seed(args.seed)
	fasta_output = FastaWriter(sys.stdout, line_length=80)
	for record in FastaReader(args.fasta):
		mutated, n_sub, n_indel = mutate_sequence(record.sequence, rate=args.rate, alphabet='ACGT', indels=True, indel_rate=args.indel_rate)
		fasta_output.write(record.name + '-sub{}-indel{}'.format(n_sub, n_indel), mutated)


if __name__ == '__main__':
	main()
