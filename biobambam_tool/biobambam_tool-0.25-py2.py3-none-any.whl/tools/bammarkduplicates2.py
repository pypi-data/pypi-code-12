import os

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util

def bammarkduplicates2(uuid, bam_path, input_state, cpu_count, engine, logger):
    step_dir = os.getcwd()
    bam_name = os.path.basename(bam_path)
    metrics_name = bam_name+'.metrics'
    tempfile = 'tempfile'
    logger.info('work_dir is: %s' % work_dir)
    if pipe_util.already_step(step_dir, 'md2', logger):
        logger.info('already completed step `bammarkduplicates2` of: %s' % bam_name)
    else:
        logger.info('running step `bammarkduplicates2` of %s: ' % bam_name)
        cmd = ['bammarkduplicates2', 'I=' + bam_path, 'O=' + bam_name, 'M=' + metrics_name, 'verbose=0', 'level=-1', 'index=1', 'tmpfile=' + tempfile, 'markthreads='+str(cpu_count)]
        output = pipe_util.do_command(cmd, logger)
        df = time_util.store_time(uuid, cmd, output, logger)
        df['bam_name'] = bam_name
        df['input_stage'] = input_stage
        unique_key_dict = {'uuid': uuid, 'bam_name': bam_name}
        table_name = 'time_mem_biobambam_bammarkduplicates2'
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        pipe_util.create_already_step(step_dir, 'md2', logger)
        logger.info('completed running step `bammarkduplicates2` of: %s' % bam_name)
    return
