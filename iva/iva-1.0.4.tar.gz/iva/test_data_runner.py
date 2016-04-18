import os
import iva

class Error (Exception): pass

class Tester:
    def __init__(self, outdir, iva_script, trimmo_jar=None, threads=1):
        self.outdir = os.path.join(outdir)
        if os.path.exists(self.outdir):
            raise Error('Output directory alread exists. Cannot continue')

        self.iva_script = iva_script
        self.trimmo_jar = trimmo_jar
        self.threads = threads


    def _copy_input_files(self):
        extractor = iva.egg_extract.Extractor(os.path.abspath(os.path.join(os.path.dirname(iva.__file__), os.pardir)))
        test_files = os.path.join('iva', 'test_run_data')
        extractor.copy_dir(test_files, self.outdir)
        print('Copied input test files into here:', os.path.abspath(self.outdir))
         

    def _run_iva(self):
        os.chdir(self.outdir)
        cmd = self.iva_script + ' --threads ' + str(self.threads)
        if self.trimmo_jar:
            cmd += ' --trimmomatic ' + self.trimmo_jar

        cmd += ' --pcr_primers hiv_pcr_primers.fa -f reads_1.fq.gz -r reads_2.fq.gz iva.out'

        print('Current working directory:', os.getcwd())
        print('Running iva on the test data with the command:', cmd, sep='\n')
        iva.common.syscall(cmd)


    def _check_output(self):
        print('Finished running iva')
        expected_contigs_file = os.path.abspath(os.path.join('iva.out', 'contigs.fasta'))
        if os.path.exists(expected_contigs_file):
            print('Looks OK. Final output contigs file is:', expected_contigs_file)
        else:
            print('Something went wrong! Final output contigs file not found:', expected_contigs_file)


    def run(self):
        self._copy_input_files()
        self._run_iva()
        self._check_output()

