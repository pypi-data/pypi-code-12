import json
import os

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util

from tools import picard_util

def get_interval_file(json_path, bam_base, interval_type):
    with open(json_path, 'r') as json_path_open:
        json_data = json.load(json_path_open)
    interval_file = json_data[bam_base][interval_type]
    return interval_file

def picard_calculatehsmetrics(uuid, bam_path, input_state, json_path, interval_dir, engine, logger):
    step_dir = os.getcwd()
    bam_name = os.path.basename(bam_path)
    bam_base, bam_ext = os.path.splitext(bam_name)
    if pipe_util.already_step(step_dir, bam_name + '_calculatehsmetrics', logger):
        logger.info('already completed step `CalculateHsMetrics` of: %s' % bam_path)
    else:
        logger.info('running step `CalculateHsMetrics` of: %s' % bam_path)

        bait_interval = get_interval_file(json_path, bam_base, 'bait')
        target_interval = get_interval_file(json_path, bam_base, 'target')
        bait_interval_path = os.path.join(interval_dir, bait_interval)
        target_interval_path = os.path.join(interval_dir, target_interval)
        home_dir = os.path.expanduser('~')
        stats_path = 'picard_calculatehsmetrics_' + bam_base
        cmd = ['java', '-d64', '-jar', os.path.join(home_dir, 'tools/picard-tools/picard.jar'), 'CalculateHsMetrics', 'INPUT=' + bam_path, 'OUTPUT=' + stats_path, 'BAIT_INTERVALS=' + bait_interval_path, 'TARGET_INTERVALS=' + target_interval_path, 'METRIC_ACCUMULATION_LEVEL=READ_GROUP']
        output = pipe_util.do_command(cmd, logger)

        # save time/mem to db
        df = time_util.store_time(uuid, cmd, output, logger)
        df['bam_path'] = bam_path
        unique_key_dict = {'uuid': uuid, 'bam_path': bam_path}
        table_name = 'time_mem_picard_calculatehsmetrics'
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)

        # save stats to db
        table_name = 'picard_calculatehsmetrics'
        select = 'BAIT_SET'
        df = picard_util.picard_select_tsv_to_df(uuid, bam_path, stats_path, logger)
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)


        pipe_util.create_already_step(step_dir, bam_name + '_calculatehsmetrics', logger)
        logger.info('completed running step `CalculateHsMetrics` of: %s' % bam_path)

    return
