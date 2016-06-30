#!/usr/bin/env python
#Once upon a time...

import textwrap
import parabam

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

class Bam2Length(parabam.core.Interface):
    def __init__(self,temp_dir=None,
                 keep_in_temp=False,
                 task_size=250000,
                 total_procs=8,
                 reader_n=2,
                 verbose=False,
                 announce=True,
                 cmd_run=False,
                 keep_telbam=False):

        super(Bam2Length,self).__init__(instance_name="telomerecat bam2length",
                                         temp_dir=temp_dir,
                                         keep_in_temp=keep_in_temp,
                                         task_size=task_size,
                                         total_procs=total_procs,
                                         reader_n=reader_n,
                                         verbose=verbose,
                                         announce=announce,
                                         cmd_run=cmd_run)
        self.keep_telbam=keep_telbam

    def run_cmd(self):
        self.run(input_paths = self.cmd_args.input,
            out_path = self.cmd_args.out,
            inserts_path=self.cmd_args.insert)

    def run(self, input_paths, out_path=None, inserts_path=None):
        
        #Import here to avoid infinite loop on import
        from telomerecat import Bam2Telbam
        from telomerecat import Telbam2Length

        self.__introduce__()

        telbam_interface = Bam2Telbam(temp_dir=self.temp_dir,
                                      total_procs=self.total_procs,
                                      task_size=self.task_size,
                                      reader_n=self.reader_n,
                                      verbose=self.verbose,
                                      announce=False,
                                      keep_in_temp=(not self.keep_telbam))
        out_files = telbam_interface.run(input_paths=input_paths)

        length_paths = self.collapse_out_files(out_files)
        length_interface = Telbam2Length(temp_dir=self.temp_dir,
                                         total_procs=self.total_procs,
                                         task_size=self.task_size,
                                         reader_n = self.reader_n,
                                         announce=False,
                                         verbose=self.verbose)
        length_interface.run(input_paths=length_paths,
                             output = out_path,
                             inserts_path=inserts_path)

        self.__goodbye__()
        self.interface_exit()

    def collapse_out_files(self,out_files):
        length_paths = []
        for path in out_files.keys():
            length_paths.append(out_files[path]["telbam"])
        return length_paths

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