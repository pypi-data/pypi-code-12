import os

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util

def bammerge(uuid, outbam_name, bam_path_list, reference_fasta_path, cpu_count, engine, logger):
    step_dir = os.getcwd()
    bam_name = os.path.basename(bam_path)
    metrics_name = outbam_name+'.metrics'
    tempfile = 'tempfile'
    if pipe_util.already_step(step_dir, 'merge', logger):
        logger.info('already completed step `bammerge` of: %s' % outbam_name)
    else:
        logger.info('running step `bammerge` of %s: ' % bam_path)
        for input_bam in bam_path_list:
            input_string = 'I=' + input_bam
        cmd = ['bammerge', 'O=' + outbam_name, 'M=' + metrics_name, 'verbose=0', 'level=-1', 'index=1', 'tmpfile=' + tempfile, 'SO=coordinate', input_string]
        output = pipe_util.do_command(cmd, logger)
        df = time_util.store_time(uuid, cmd, output, logger)
        df['outbam_name'] = outbam_name
        unique_key_dict = {'uuid': uuid, 'outbam_name': outbam_name}
        table_name = 'time_mem_biobambam_bammerge'
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        pipe_util.create_already_step(step_dir, 'merge', logger)
        logger.info('completed running step `bammerge` of: %s' % outbam_name)
    return
