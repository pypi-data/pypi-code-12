import getpass
import os

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util

def bamtofastq(uuid, bam_path, input_state, engine, logger):
    step_dir = os.getcwd()
    bam_name = os.path.basename(bam_path)
    if pipe_util.already_step(step_dir, 'fastq', logger):
        logger.info('already completed step `bamtofastq` of: %s' % bam_name)
    else:
        logger.info('running step `bamtofastq` of %s: ' % bam_name)
        home_dir = os.path.join('/home', getpass.getuser()) #cwltool sets HOME to /var/spool/cwl, so need to be explicit
        tempfq = os.path.join(step_dir, 'tempfq')
        bin_path = os.path.join(home_dir, 'tools', 'biobambam2', 'bin', 'bamtofastq')
        cmd = [bin_path, 'filename=' + bam_path, 'outputdir=' + step_dir, 'tryoq=1', 'collate=1', 'outputperreadgroup=1', 'T=' + tempfq, 'gz=1', 'level=1', 'outputperreadgroupsuffixF=_1.fq.gz', 'outputperreadgroupsuffixF2=_2.fq.gz', 'outputperreadgroupsuffixO=_o1.fq.gz', 'outputperreadgroupsuffixO2=_o2.fq.gz', 'outputperreadgroupsuffixS=_s.fq.gz', 'exclude=QCFAIL,SECONDARY,SUPPLEMENTARY']
        output = pipe_util.do_command(cmd, logger)
        df = time_util.store_time(uuid, cmd, output, logger)
        df['bam_name'] = bam_name
        df['input_state'] = input_state
        unique_key_dict = {'uuid': uuid, 'bam_name': bam_name}
        table_name = 'time_mem_biobambam_bamtofastq'
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        pipe_util.create_already_step(step_dir, 'fastq', logger)
        logger.info('completed running step `bamtofastq` of: %s' % bam_name)
    return
