#!/usr/bin/env python
#Once upon a time...

import textwrap
import parabam

import bam2telbam
import telbam2length

######################################################################
##
##      Genereate length estimates for given BAM files
##
##      This simply strings together bam2telbam 
##      and telbam2length packages
##        
##      Author: jhrf
##
######################################################################

class Interface(parabam.core.Interface):
    def __init__(self,temp_dir):
        super(Interface,self).__init__(temp_dir)

    def run_cmd(self,parser):
        cmd_args = parser.parse_args()

        self.run(input_paths = cmd_args.input,
            out_path = cmd_args.out,
            total_procs = cmd_args.p,
            reader_n = cmd_args.f,
            task_size = cmd_args.s,
            keep_telbam = cmd_args.k,
            verbose = cmd_args.v,
            announce = True,
            inserts_path=cmd_args.insert)

    def run(self,input_paths,out_path=None,
        total_procs=8,task_size=250000,keep_telbam=False,
        reader_n=2,verbose=False,announce=False,inserts_path=None):
        
        if not verbose:
            announce = False
        self.__introduce__("telomerecat bam2length",announce)

        telbam_interface = bam2telbam.Interface(self._temp_dir)
        out_files = telbam_interface.run(input_paths=input_paths,
                            total_procs=total_procs,
                            task_size=task_size,
                            reader_n=reader_n,
                            verbose=verbose,
                            keep_in_temp=(not keep_telbam))

        length_paths = self.collapse_out_files(out_files)

        length_interface = telbam2length.Interface(self._temp_dir)
        length_interface.run(input_paths=length_paths,
                            output = out_path,
                            total_procs=total_procs,
                            task_size=task_size,
                            reader_n = reader_n,
                            verbose=verbose,
                            inserts_path=inserts_path)

        self.__goodbye__("telomerecat bam2length",announce)

    def collapse_out_files(self,out_files):
        return [path for path_list in out_files.values() for path in path_list]

    def get_parser(self):
        parser = self.default_parser()
        parser.description = textwrap.dedent(
        '''\
        telomerecat bam2length
        ----------------------------------------------------------------------

            The bam2length command allows the user to genereate a telomere
            length estimate from a BAM file.

            The majority of the time taken running the bam2length script is
            spent collecting telomeric reads from the BAM file. If you wish
            to run multiple analyses on this file be sure to keep the TELBAMS
            that this run creates by using the `-k` option.

            If you wish to generate TELBAMS seperately from length estimation
            you should use the bam2telbam command.
            
            Type `telomerecat bam2telbam` to find out more.

        ----------------------------------------------------------------------
        ''')        

        parser.add_argument('input',metavar='BAM(S)', nargs='+',
            help='BAM file(s) for which we wish to generate \n'\
            'telomere length estimates')
        parser.add_argument('--out',metavar='CSV',type=str,nargs='?',default=None,
            help='Specify output path for length estimation CSV.\n'+\
                'Path automatically generated if left blank [Default: None]')
        parser.add_argument('--insert',metavar='CSV',nargs='?',type=str,default=None,
            help="A file specifying the insert length mean and std for\n"+\
                 "each input sample. If not present telomerecat will\n"+\
                 "automatically estimate insert length of sample [Default: None]")
        parser.add_argument('-k',action="store_true",default=False
            ,help='The program will retain the TELBAMS\n'\
            'created as part of the analysis')
        parser.add_argument('-v',choices=[0,1,2],default=0,type=int,
            help="Verbosity. The amount of information output by the program:\n"\
            "\t0: No output [Default]\n"\
            "\t1: Some output\n"\
            "\t2: Detailed output")

        return parser

if __name__ == "__main__":
    print "Please do not run this script directly."\
     " Type telomerecat -h for more information."


#....happily ever after.