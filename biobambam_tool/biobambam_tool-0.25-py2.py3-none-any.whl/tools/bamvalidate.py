import os

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util


def bamvalidate(uuid, bam_path, input_state, cpu_count, engine, logger):
    step_dir = os.getcwd()
    bam_name = os.path.basename(bam_path)
    tmpfile = 'tmpfile'
    inputthreads = str(cpu_count/2)
    outputthreads = inputthreads
    if pipe_util.already_step(step_dir, bam_name + '_bamvalidate', logger):
        logger.info('already completed step `bamvalidate` of: %s' % bam_name)
    else:
        logger.info('running step `picard BuildBamValidate` of: %s' % bam_name)
        cmd = ['bamvalidate', 'verbose=1', 'I=' + bam_path, 'tmpfile=' + tmpfile, 'inputthreads='+inputthreads, 'outputthreads='+outputthreads]
        output = pipe_util.do_command(cmd, logger)
        df = time_util.store_time(uuid, cmd, output, logger)
        df['bam_name'] = bam_name
        unique_key_dict = {'uuid': uuid, 'bam_name': bam_name}
        table_name = 'time_mem_biobambam_bamvalidate'
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        pipe_util.create_already_step(step_dir, bam_name + '_bamvalidate', logger)
        logger.info('completed running step `bamvalidate` of: %s' % bam_name)
    return
