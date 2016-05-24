import getpass
import os

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util

from tools import picard_util

def picard_collectwgsmetrics(uuid, bam_path, input_state, reference_fasta_path, engine, logger):
    step_dir = os.getcwd()
    bam_name = os.path.basename(bam_path)
    bam_base, bam_ext = os.path.splitext(bam_name)
    if pipe_util.already_step(step_dir, bam_name + '_collectwgsmetrics', logger):
        logger.info('already completed step `CollectWgsMetrics` of: %s' % bam_name)
    else:
        logger.info('running step `CollectWgsMetrics` of: %s' % bam_name)
        home_dir = os.path.join('/home', getpass.getuser()) #cwltool sets HOME to /var/spool/cwl, so need to be explicit
        stats_path = 'picard_collectwgsmetrics_' + bam_base
        cmd = ['java', '-d64', '-jar', os.path.join(home_dir, 'tools/picard-tools/picard.jar'), 'CollectWgsMetrics', 'INPUT=' + bam_path, 'OUTPUT=' + stats_path, 'REFERENCE_SEQUENCE=' + reference_fasta_path]
        output = pipe_util.do_command(cmd, logger)

        # save time/mem to db
        df = time_util.store_time(uuid, cmd, output, logger)
        df['bam_path'] = bam_name
        df['input_state'] = input_state
        unique_key_dict = {'uuid': uuid, 'bam_name': bam_name}
        table_name = 'time_mem_picard_collectwgsmetrics'
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)

        # save stats to db
        table_name = 'picard_collectwgsmetrics'
        select = 'GENOME_TERRITORY'
        df = picard_util.picard_select_tsv_to_df(uuid, bam_path, stats_path, logger)
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)

        # save stats to db
        table_name = 'picard_collectwgsmetrics_histogram'
        select = 'coverage'
        df = picard_util.picard_select_tsv_to_df(uuid, bam_path, stats_path, logger)
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)


        pipe_util.create_already_step(step_dir, bam_name + '_collectwgsmetrics', logger)
        logger.info('completed running step `CollectWgsMetrics` of: %s' % bam_name)

    return

