import os

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util


def fastqc(uuid, fastq_path, thread_count, engine, logger):
    fastq_name = os.path.basename(fastq_path)
    fastq_dir = os.path.dirname(fastq_path)
    fastq_base, fastq_ext = os.path.splitext(fastq_name)
    if pipe_util.already_step(fastq_dir, 'fastqc_' + fastq_base, logger):
        logger.info('already completed step `fastqc`: %s' % fastq_path)
    else:
        logger.info('running step `fastqc` of %s' % fastq_path)
        cmd = ['fastqc', '--threads', str(thread_count), '--extract', fastq_path]
        output = pipe_util.do_command(cmd, logger)
        df = time_util.store_time(uuid, cmd, output, logger)
        df['fastq_path'] = fastq_path
        table_name = 'time_mem_fastqc'
        unique_key_dict = {'uuid': uuid, 'fastq_path': fastq_path}
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        pipe_util.create_already_step(fastq_dir, 'fastqc_' + fastq_base, logger)
    return
