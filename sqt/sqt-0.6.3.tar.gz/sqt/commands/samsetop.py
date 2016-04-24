#!/usr/bin/env python3
"""
Perform set operation on two SAM/BAM files.

The output BAM file will have the same header as file A.

WARNING: Implementation is neither very fast nor memory efficient.

Possible operations:
  union:        Output union of A and B, abort with error if
                different lines for same read are encountered.
  intersection: Output intersection of A and B, abort with error if
                different lines for same read are encountered.
  setminus:     Outputs all read in A that are not in B.
  symdiff:      Output all reads in A or B but not in both.
"""
from sqt import HelpfulArgumentParser
import sys
from pysam import Samfile

__author__ = "Tobias Marschall"

def add_arguments(parser):
	arg = parser.add_argument
	arg("-s", action="store_true", dest="sam_output", default=False,
		help="Output SAM file instead of BAM file")
	arg("-U", action="store_true", dest="exclude_unmapped_A", default=False,
		help="Exclude unmapped reads from file A")
	arg("-V", action="store_true", dest="exclude_unmapped_B", default=False,
		help="Exclude unmapped reads from file B")
	arg("-r", action="store_true", dest="remove_name_suffix", default=False,
		help="Remove trailing \"/*\" from read names. Useful if one mapper appends \"/1\" and another does not.")
	arg('bampath1', help='First BAM or SAM file')
	arg('operation', choices=('union','intersection','setminus','symdiff'))
	arg('bampath2', help='Second BAM or SAM file')
	arg('outputpath', nargs='?',
		help='Output BAM or SAM file. If omitted, only print the number of reads '
		'that would be written.')


def SamOrBam(name, mode='r'):
	if name.endswith('.bam'):
		mode += 'b'
	return Samfile(name, mode)


def remove_suffix(s):
	i = s.rfind('/')
	if i == -1: return s
	else: return s[:i]


def nop(s):
	return s


def dict_of_reads(reads, exclude_unmapped, rename):
	d = dict()
	for read in reads:
		if exclude_unmapped and read.is_unmapped: continue
		name = rename(read.qname)
		if d.has_key(name):
			raise Exception("Duplicate read in input file (%s)"%name)
		d[name] = read
	return d


def union(A, B,outfile, exclude_unmapped_A, exclude_unmapped_B, rename):
	readsB = dict_of_reads(B, exclude_unmapped_B, rename)
	readnamesA = set()
	for read in A:
		if exclude_unmapped_A and read.is_unmapped: continue
		name = rename(read.qname)
		if name in readnamesA:
			raise Error("Duplicate read in input file (%s)"%name)
		readnamesA.add(name)
		if readsB.has_key(name):
			if read.compare(readsB[name]) != 0:
				print('Content mismatch for read %s:'%name, file=sys.stderr)
				print('File A:',read, file=sys.stderr)
				print('File B:',readsB[name], file=sys.stderr)
				sys.exit(1)
			readsB.pop(name)
		outfile.write(read)
	for read in readsB.itervalues():
		outfile.write(read)


def intersection(A,B,outfile,exclude_unmapped_A,exclude_unmapped_B,rename):
	readsB = dict_of_reads(B, exclude_unmapped_B, rename)
	readnamesA = set()
	for read in A:
		if exclude_unmapped_A and read.is_unmapped: continue
		name = rename(read.qname)
		if name in readnamesA:
			raise Error("Duplicate read in input file (%s)"%name)
		readnamesA.add(name)
		if readsB.has_key(name):
			if read.compare(readsB[name])!=0:
				print('Content mismatch for read %s:'%name, file=sys.stderr)
				print('File A:',read, file=sys.stderr)
				print('File B:',readsB[name], file=sys.stderr)
				sys.exit(1)
			outfile.write(read)


def setminus(A,B,outfile,exclude_unmapped_A,exclude_unmapped_B,rename):
	if exclude_unmapped_B: readnamesB = set((rename(read.qname) for read in B if not read.is_unmapped))
	else: readnamesB = set((rename(read.qname) for read in B))
	for read in A:
		if exclude_unmapped_A and read.is_unmapped: continue
		if not rename(read.qname) in readnamesB:
			outfile.write(read)


def symdiff(A,B,outfile,exclude_unmapped_A,exclude_unmapped_B,rename):
	if exclude_unmapped_B: readsB = dict(((rename(read.qname),read) for read in B if not read.is_unmapped))
	else: readsB = dict(((rename(read.qname),read) for read in B))
	for read in A:
		if exclude_unmapped_A and read.is_unmapped: continue
		name = rename(read.qname)
		if readsB.has_key(name):
			readsB.pop(name)
		else:
			outfile.write(read)
	for read in readsB.itervalues():
		outfile.write(read)


class Counter:
	count = 0
	def write(self, x):
		self.count += 1


def main(args=None):
	if args is None:
		parser = HelpfulArgumentParser(description=__doc__)
		add_arguments(parser)
		args = parser.parse_args()
	operation = args.operation
	A = SamOrBam(args.bampath1)
	B = SamOrBam(args.bampath2)
	if args.outputpath:
		outfile = Samfile(args[3], 'wh' if args.sam_output else 'wb', template=A)
	else:
		outfile = Counter()
	globals()[operation](A, B, outfile, args.exclude_unmapped_A, args.exclude_unmapped_B, remove_suffix if args.remove_name_suffix else nop)
	if args.outputpath is None:
		print(outfile.count)


if __name__ == '__main__':
	main()
