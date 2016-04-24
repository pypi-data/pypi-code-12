#!/usr/bin/env python3
"""
"""
import sys
from random import randint, random, seed
import matplotlib as mpl
mpl.use('pdf')  # enable matplotpib over an ssh connection without X
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sqt import HelpfulArgumentParser
from sqt.io.fasta import IndexedFasta

__author__ = "Marcel Martin"


def get_argument_parser():
	parser = HelpfulArgumentParser(description=__doc__)
	add = parser.add_argument
	add("--left", type=float, default=None)
	add("--right", type=float, default=None)
	add("--title", help="Plot title (default: Histogram of <INFILENAME>)")
	add("--bins", type=int, default=40, help="number of bins (default: %(default)s")
	add("infile", help="use '-' for standard input")
	add("image", nargs='?', help="name of PDF or SVG file")
	return parser


def main():
	parser = get_argument_parser()
	args = parser.parse_args()
	if args.infile == '-':
		path = sys.stdin.buffer
		title = 'Histogram'
	else:
		path = args.infile
		title = 'Histogram of ' + args.infile
	if args.title:
		title = args.title
	data = pd.read_csv(path, dtype=float).values  # delimiter=None is default

	fig, ax = plt.subplots()
	ax.set_title(title)
	plt.hist(data, bins=args.bins, rwidth=0.8)
	ax.set_xlim(left=args.left, right=args.right)
	if args.image is not None:
		plt.savefig(args.image)
	else:
		plt.show()


if __name__ == '__main__':
	main()
