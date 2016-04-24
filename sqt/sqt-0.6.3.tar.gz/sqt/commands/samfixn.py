#!/usr/bin/env python3
"""
Read a SAM file from standard input, replace all characters in all reads
that are not one of {a, c, g, t, n, A, C, G, T, N} with the character 'N'.
Write the modified SAM file to standard output.

This is approx. 8 times faster than an equivalent awk line using the gsub()
function.
"""
import sys
from os.path import join, dirname, realpath, isfile

from sqt import HelpfulArgumentParser


def main():
	parser = HelpfulArgumentParser(usage=__doc__)
	args = parser.parse_args()

	tab = [ord('N')] * 256
	for c in b'ACGTNacgtn':
		tab[c] = c
	trans = bytes(tab)

	for line in sys.stdin.buffer:
		if line.startswith(b'@'):
			sys.stdout.buffer.write(line)
		else:
			fields = line.split(b'\t')
			fields[9] = fields[9].translate(trans)
			sys.stdout.buffer.write(b'\t'.join(fields))


if __name__ == '__main__':
	main()
