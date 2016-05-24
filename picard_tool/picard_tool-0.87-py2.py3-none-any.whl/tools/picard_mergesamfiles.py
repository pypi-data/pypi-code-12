import getpass
import os

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util


def picard_mergesamfiles(uuid, bam_path_list, input_state, outbam_name, engine, logger):
    step_dir = os.getcwd()
    bam_name = outbam_name
    if pipe_util.already_step(step_dir, 'mergesamfiles', logger):
        logger.info('already completed step `picard MergeSamFiles` of: %s' % bam_name)
    else:
        logger.info('running step `picard MergeSamFiles` of: %s' % bam_name)
        home_dir = os.path.join('/home', getpass.getuser()) #cwltool sets HOME to /var/spool/cwl, so need to be explicit

        cmd = ['java', '-d64', '-jar', os.path.join(home_dir, 'tools/picard-tools/picard.jar'), 'MergeSamFiles', 'USE_THREADING=true', 'OUTPUT=' + outbam_name, 'TMP_DIR=' + step_dir, 'VALIDATION_STRINGENCY=STRICT', 'SORT_ORDER=coordinate']
        for input_bam in bam_path_list:
            input_string = 'INPUT=' + input_bam
            cmd.append(input_string)
        output = pipe_util.do_command(cmd, logger)
        df = time_util.store_time(uuid, cmd, output, logger)
        df['bam_name'] = bam_name
        df['input_state'] = input_state
        unique_key_dict = {'uuid': uuid, 'bam_name': bam_name}
        table_name = 'time_mem_picard_mergesamfiles'
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        pipe_util.create_already_step(step_dir, 'mergesamfiles', logger)
        logger.info('completed running step `picard MergeSamFiles` of: %s' % bam_name)
    return
