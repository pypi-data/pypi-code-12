#!/usr/bin/env python
from distutils.core import setup
def main():
	setup(
		name='biotoolkit',
		version='0.0.1',
		description='biotoolkit contains GCfromDNA: Analyze GC-content of DNA sequences from fasta files',
		author='meh',
		packages=['biotoolkit'],

	)
	
	pass
if __name__ == '__main__':
	main()