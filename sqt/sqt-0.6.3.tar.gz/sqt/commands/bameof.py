#!/usr/bin/env python3
"""
Check whether the EOF marker is present in BAM files.
If it's not, this may be a sign that the BAM file was corrupted.

The exit code is 1 if the marker was present in *all files*.
It is 0 if the marker was missing in any of the files.

BUGS/TODO
- Does not work with uncompressed BAM files.
"""

import sys
from sqt import HelpfulArgumentParser

__author__ = "Marcel Martin"


def add_arguments(parser):
	arg = parser.add_argument
	arg("-q", "--quiet", action='store_true',
		help="Don't print anything, just set the exit code.")
	arg("bam", metavar='BAM', nargs='+')


def bam_eof_is_ok(f):
	"""
	Check whether BAM file f contains the 'magic' end-of-file marker.
	Adapted from samtools function bgzf_check_EOF (in bgzf.c).
	"""
	try:
		f.seek(-28, 2)
	except IOError:
		return False
	data = f.read(28)
	return data == b"\037\213\010\4\0\0\0\0\0\377\6\0\102\103\2\0\033\0\3\0\0\0\0\0\0\0\0\0"


def main(args=None):
	if args is None:
		parser = HelpfulArgumentParser(description=__doc__)
		add_arguments(parser)
		args = parser.parse_args()

	exitcode = 0
	for name in args.bam:
		with open(name, 'rb') as f:
			if bam_eof_is_ok(f):
				if not args.quiet:
					print(name, ": OK", sep='')
			else:
				if not args.quiet:
					print(name, ": MISSING", sep='')
					exitcode = 1
				else:
					sys.exit(1)
	sys.exit(exitcode)


if __name__ == '__main__':
	main()
