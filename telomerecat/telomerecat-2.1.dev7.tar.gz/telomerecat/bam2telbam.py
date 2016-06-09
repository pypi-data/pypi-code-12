#!/usr/bin/env python
#Once upon a time...

#Create a bam file with all the putatative telomere reads

import sys,os
import argparse
import textwrap
import pysam
import time
import gc

import parabam

import Queue as Queue2

from parabam.command import subset
from multiprocessing import Queue,Process
from itertools import izip

######################################################################
##
##      Create telbams for list of given BAM files.
##
##      Author: jhrf
##
######################################################################

#Here we define what constitutes a telomereic read.
#If both reads in a pair match the critea we store
#them to the telbam
def engine(reads,user_constants,parent):
	tel_pats = user_constants["tel_pats"]

	read,mate = reads

	telomere_status = [True if tel_pats[1] in seq or tel_pats[0] in seq else False
						 for seq in iter((read.seq,mate.seq))]
	if any(telomere_status):
		return [("telbam",read),("telbam",mate)]
	return []

#This whole package is essentially just a wrapper for a call to parabam subset
class Interface(parabam.core.Interface):
	"""Interface to interact with telomerecat programatically. This interface
	is also called by the `telomerecat` script"""
	def __init__(self,temp_dir):
		super(Interface,self).__init__(temp_dir)

	def run_cmd(self,parser):
		"""Called from the master `telomerecat` script which handels the
		cmd line interface. Requires an argparse parser. Users should call
		the `run` function."""
		cmd_args = parser.parse_args()

		self.run(input_paths = cmd_args.input,
			total_procs = cmd_args.p,
			task_size = cmd_args.s,
			reader_n=cmd_args.f,
			verbose = cmd_args.v,
			announce=True)

	def run(self,input_paths,total_procs,task_size,reader_n=2,verbose=False,keep_in_temp=False,announce=False):
		"""The main function for invoking the part of the program which creates a telbam from a bam

		Arguments:
			bams (list): The BAM files we wish to run telomerecat telbam on
			total_procs (int): The maximum numbers of task that will be run at one time
			task_size (int): The amount of reads that any one task will process concurrently
			verbose (int): Expects an int from 0 to 2. The level of output produced by telomerecat
			keep_in_temp (bool): Files will be kept in temp file after processing. Useful for incorporation into pipelines
			announce (bool): Specify whether the program returns a welcome string."""

		if not verbose:
			announce = False
		program_name = "telomerecat bam2telbam"
		self.__introduce__(program_name,announce)

		subset_types=["telbam"]
		tel_pats = ["TTAGGGTTAGGG","CCCTAACCCTAA"]

		#need to define my constants and engine here:
		telbam_constants = {"thresh":1,
							"tel_pats":tel_pats}

		final_output_paths = {}

		for input_path in input_paths:

			if verbose:
				sys.stdout.write(" Generating TELBAM from: %s\n" % (input_path,))
				sys.stdout.write("\t- TELBAM generation started %s\n" %\
									(self.__get_date_time__(),))

			subset_interface = subset.Interface(self._temp_dir)
			#call to parabam subset
			telbam_paths = subset_interface.run(input_bams=[input_path],
								 total_procs=total_procs,
								 task_size=task_size,
								 reader_n=reader_n,
								 verbose=verbose,
								 user_subsets=subset_types,
								 user_constants = telbam_constants,
								 user_engine = engine,
								 keep_in_temp=keep_in_temp,
								 pair_process=True,
								 include_duplicates=True,
								 debug = False)

			if verbose:
				sys.stdout.write("\t- TELBAM generation finished %s\n\n"\
									 % (self.__get_date_time__(),))

			gc.collect()
			final_output_paths.update(telbam_paths)

		self.__goodbye__(program_name,announce)
		return final_output_paths

	def get_parser(self):
		parser = self.default_parser()
		parser.description = textwrap.dedent('''\
        telomerecat bam2telbam
        ----------------------------------------------------------------------

             The bam2telbam command allows you to generate a TELBAM 
             from a parent BAM file. A TELBAM is a file including all of the
             reads with at least 2 occurences of the telomeric hexamer.

             Once you have genereated a TELBAM you may then generate length
             estimates more quickly, when compared to running the `bam2length`
             command on a full BAM file. This is helpful if you intend to 
             generate TL estimates more than once or if you require a  
             collection of telomere reads.
   
             Given the following BAM file:

             	example_bam_name.bam

             `telomerecat bam2telbam` will create the following TELBAM in the
             directory which it is run:

             	example_bam_name_telbam.bam

             To find out how to generate a length estimate from a TELBAM
             type `telomerecat telbam2length` into your terminal

        ----------------------------------------------------------------------
         ''')

		parser.add_argument('input',metavar='BAM(S)', nargs='+',
			help='BAM file(s) for which we wish to generate TELBAMS')
		parser.add_argument('-v',choices=[0,1,2],default=0,type=int,
            help="Verbosity. The amount of information output by the program:\n"\
            "\t0: No output [Default]\n"\
            "\t1: Total Reads Processsed\n"\
            "\t2: Detailed output")

		return parser


if __name__ == "__main__":
	print "Type telomerecat -h for help!"

#....happily ever after.
