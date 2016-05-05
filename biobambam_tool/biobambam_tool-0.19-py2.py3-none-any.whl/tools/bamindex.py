import os

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util


def bamindex(uuid, bam_path, input_state, engine, logger):
    step_dir = os.getcwd()
    bam_name = os.path.basename(bam_path)
    bam_base, bam_ext = os.path.splitext(bam_name)
    bai_name = bam_base + '.bai'
    if pipe_util.already_step(step_dir, bam_name + '_bamindex', logger):
        logger.info('already completed step `bamindex` of: %s' % bam_name)
    else:
        logger.info('running step `picard BuildBamIndex` of: %s' % bam_name)
        cmd = ['bamindex', 'verbose=0', 'disablevalidation=1', 'I=' + bam_path, 'O=' + bai_name]
        output = pipe_util.do_command(cmd, logger)
        df = time_util.store_time(uuid, cmd, output, logger)
        df['bam_name'] = bam_name
        df['input_state'] = input_state
        unique_key_dict = {'uuid': uuid, 'bam_name': bam_name}
        table_name = 'time_mem_biobambam_bamindex'
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        pipe_util.create_already_step(step_dir, bam_name + '_bamindex', logger)
        logger.info('completed running step `bamindex` of: %s' % bam_name)
    return
