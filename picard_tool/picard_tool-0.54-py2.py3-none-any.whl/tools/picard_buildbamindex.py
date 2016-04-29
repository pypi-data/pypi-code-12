import os

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util


def picard_buildbamindex(uuid, bam_path, engine, logger, be_lenient):
    step_dir = os.getcwd()
    bam_name = os.path.basename(bam_path)
    bam_base, bam_ext = os.path.splitext(bam_name)
    bai_name = bam_base + '.bai'
    bai_path = os.path.join(step_dir, bai_name)
    if pipe_util.already_step(step_dir, bam_name + '_buildbamindex', logger):
        logger.info('already completed step `validate` of: %s' % bam_path)
    else:
        logger.info('running step `picard BuildBamIndex` of: %s' % bam_path)
        home_dir = os.path.expanduser('~')
        cmd = ['java', '-d64', '-jar', os.path.join(home_dir, 'tools/picard-tools/picard.jar'), 'BuildBamIndex', 'INPUT=' + bam_path, 'OUTPUT=' + bai_path, 'VALIDATION_STRINGENCY=', 'LENIENT']
        output = pipe_util.do_command(cmd, logger)
        df = time_util.store_time(uuid, cmd, output, logger)
        df['bam_name'] = bam_name
        unique_key_dict = {'uuid': uuid, 'bam_name': bam_name}
        table_name = 'time_mem_picard_buildbamindex'
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        pipe_util.create_already_step(step_dir, bam_name + '_buildbamindex', logger)
        logger.info('completed running step validate of: %s' % bam_path)
    return bai_path
