import os

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util

def bammdnm(uuid, bam_path, input_state, reference_fasta_path, cpu_count, engine, logger):
    step_dir = os.getcwd()
    bam_name = os.path.basename(bam_path)
    out_bam_path = bam_name
    metrics_name = bam_name+'.metrics'
    out_metrics_path = metrics_name
    tempfile = 'tempfile'
    if pipe_util.already_step(step_dir, 'mdnm', logger):
        logger.info('already completed step `bammdnm` of: %s' % bam_name)
    else:
        logger.info('running step `bammdnm` of %s: ' % bam_name)
        cmd = ['bammdnm', 'I=' + bam_path, 'O=' + out_bam_path, 'M=' + out_metrics_path, 'verbose=0', 'level=-1', 'index=1', 'tempfile=' + tempfile, 'markthreads=' + str(cpu_count)]
        output = pipe_util.do_command(cmd, logger)
        df = time_util.store_time(uuid, cmd, output, logger)
        df['bam_name'] = bam_name
        df['input_state'] = input_state
        unique_key_dict = {'uuid': uuid, 'bam_name': bam_name}
        table_name = 'time_mem_biobambam_bammdnm'
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        pipe_util.create_already_step(step_dir, 'mdnm', logger)
        logger.info('completed running step `bammdnm` of: %s' % bam_name)
    return
