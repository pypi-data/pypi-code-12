#!/usr/bin/env python
'''
GCfromDNA : determine GC content in DNA sequences from fasta (.fa) files.
This script can be run as an imported python module or directly from the command line. 
GCfromDNA takes optional filename argument(s). If no filename is provided, 
the script prompts for user's selection from fasta files located in the current directory.
Batch processing is possible. 
GC content (percent) is calculated for each sequence, the sequence names are formatted, and 
the data is saved as a csv file with the original filename (e.g., file1.fa --> file1.csv). 

Example invocations: 

#----as imported module----#
	#!/usr/bin/env python
	from biotoolkit import GCfromDNA
	GCfromDNA.compute( ['file1.fa','file2.fa','file3.fa'] ) 	#pass optional file arguments as list

#----interactively----#
	$ python
	>>> from biotoolkit import GCfromDNA
	>>> GCfromDNA.compute()										#pass optional file arguments as list (not shown)

#----from folder containing GCfromDNA.py----#
	$ python GCfromDNA.py file1.fa file2.fa file3.fa			#optional file arguments separated by spaces
	
		or
	
	$ python GCfromDNA.py *.fa									#simple batch processing for wildcards
'''

from Bio import SeqIO
from Bio.SeqUtils import GC
import sys
import subprocess as sp


def exit():
	print; print 'Exiting...';print
	sys.exit()


def write_csv(new_doc,fname):
	#Generate csv file from parsed data and save as original filename (- 'fa') + 'csv'
	new_csv = '\n'.join([x[0]+','+str(x[1]) for x in new_doc])
	fname2 = fname[:len(fname)-2]+'csv'
	with open(fname2,'w') as f:
		f.write(new_csv)
	print '  New doc \'%s\' written from file \'%s\'.' % (fname2,fname)


def parse_files(files):
	#Parse data from fasta files using Bio SeqIO module (handles multiple input files). 
	#Currently set to accept only files ending in '.fa'. 
	#For each file, format all sequence names (replace spaces with underscores). 
	#Calculate GC-content (using Bio.SeqUtils GC module) and truncate to two decimal places. 
	#Send formatted data to write_csv. 
	print 'Notes from file operations:'
	for file in files:
		if not file.endswith('.fa'):
			print '  \'%s\' not fasta (.fa) file (not parsed).' % file
			continue 
		try:
			new_doc = []
			for seq_record in SeqIO.parse(file,'fasta'):
				name = seq_record.description.replace('  ','').rstrip().replace(' ','_')	
				gc_content = int( 100 * GC(seq_record.seq) ) / 100.							
				new_doc.append([name,gc_content])
			write_csv(new_doc,file)
		except:
			print '  Problem parsing file \'%s\'. Check filename.' % file
			

def compute(*args):	
	#Compute function: check for filename arguments.
	#If no arguments found, display fasta files in current directory and prompt user to 
	#select file(s) to parse.
	
	print
	print '#---------------- GCfromDNA version 0.1 -------------------#'
	print '#--Determine GC-content of DNA sequences from fasta files--#'
	print

	if args:	
		#extract list from tuple, if necessary
		args = args[0]	
	if args:	
		#optional filename arguments found; bypass user selection phase		
		parse_files(args)
		
	else:
		#no filename arguments found; display fasta files and prompt for user selection
		files = [x for x in sp.Popen(['ls'],stdout=sp.PIPE).communicate()[0].split() if x.endswith('.fa')]
		
		if files:
			resp = ''
			while 1:
				print 'This folder contains:'
				for f in range(len(files)):
					print ' ', f, files[f]
				print

				print 'Select fasta file by number or name...'
				resp = raw_input(' ...or type \'all\' to parse all or \'q\' to quit: ')
				print
				
				if resp == 'q': exit()
				
				if resp == 'all': 
					parse_files(files)
					break
					
				try:	
					#check for valid integer input
					resp_num = int(resp)
					if -1 < resp_num < len(files):
						parse_files( [files[resp_num]] )
						break
				except:
					pass

				if resp in files:
					#valid filename entered
					parse_files( [resp] )
					break
				else:
					print '* Bad selection *'
					print
				
		else:
			print 'No files with .fa suffix found in current directory.' 
	
	exit()

	
def main():
	
	args = []
	if len(sys.argv) > 1:
		args = sys.argv[1:]

	compute(args)
	
if __name__ == '__main__':
	main()