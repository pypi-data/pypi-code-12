import getpass
import json
import os

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util

from tools import picard_util

def unxz(interval_dir, file_path, logger):
    cwd = os.getcwd()
    os.chdir(interval_dir)
    cmd = ['unxz', file_path + '.xz']
    output = pipe_util.do_command(cmd, logger)
    os.chdir(cwd)
    return

def get_exome_kit(readgroup_bam_path, readgroup_json_path, bam_library_kit_json_path, orig_bam_name, logger):
    readgroup_bam_name = os.path.basename(readgroup_bam_path)
    with open(readgroup_json_path, 'r') as readgroup_json_path_open:
        readgroup_json_path_data = json.load(readgroup_json_path_open)
    with open(bam_library_kit_json_path, 'r') as bam_library_kit_json_path_open:
        bam_library_kit_json_data = json.load(bam_library_kit_json_path_open)

    readgroup_id = readgroup_json_path_data['ID']
    if readgroup_id not in os.path.basename(readgroup_bam_name):
        logger.info('readgroup_id is: %s, but readgroup_bam_name is: %s' % (readgroup_id, readgroup_bam_name))
    readgroup_library = readgroup_json_path_data['LB']
    exome_kit = bam_library_kit_json_data[orig_bam_name][readgroup_library]
    return exome_kit

def get_interval_file(exome_kit, bait_target_key_interval_json_path, interval_type, logger):
    with open(kit_to_bait_target_interval_json_path, 'r') as f_open:
        data = json.load(f_open)
    interval_name = data[interval_type][exome_kit]
    return interval_name

def picard_calculatehsmetrics(uuid, readgroup_bam_path, readgroup_json_path, bam_library_kit_json_path, orig_bam_name, input_state, engine, logger):
    step_dir = os.getcwd()
    readgroup_bam_name = os.path.basename(readgroup_bam_path)
    readgroup_bam_base, bam_ext = os.path.splitext(readgroup_bam_name)
    if pipe_util.already_step(step_dir, readgroup_bam_name + '_calculatehsmetrics', logger):
        logger.info('already completed step `CalculateHsMetrics` of: %s' % readgroup_bam_name)
    else:
        logger.info('running step `CalculateHsMetrics` of: %s' % readgroup_bam_name)
        home_dir = os.path.join('/home', getpass.getuser()) #cwltool sets HOME to /var/spool/cwl, so need to be explicit
        interval_dir = os.path.join(home_dir, 'tools', 'exome_kit', 'intervals')
        bait_target_key_interval_json_path = os.path.join(interval_dir, 'bait_target_key_interval.json.xz')
        unxz(interval_dir, bait_target_key_interval_json_path, logger)
        
        exome_kit = get_exome_kit(readgroup_bam_path, readgroup_json_path, bam_library_kit_json_path, orig_bam_name, logger)
        bait_interval_name = get_interval_file(exome_kit, bait_target_key_interval_json_path, 'bait', logger)
        target_interval_name = get_interval_file(exome_kit, bait_target_key_interval_json_path, 'target', logger)
        
        bait_interval_path = os.path.join(interval_dir, bait_interval_name)
        target_interval_path = os.path.join(interval_dir, target_interval_name)

        unxz(interval_dir, bait_interval_path, logger)
        unxz(interval_dir, target_interval_path, logger)
        
        stats_path = 'picard_calculatehsmetrics_' + bam_base
        cmd = ['java', '-d64', '-jar', os.path.join(home_dir, 'tools/picard-tools/picard.jar'), 'CalculateHsMetrics', 'INPUT=' + readgroup_bam_path, 'OUTPUT=' + stats_path, 'BAIT_INTERVALS=' + bait_interval_path, 'TARGET_INTERVALS=' + target_interval_path, 'METRIC_ACCUMULATION_LEVEL=READ_GROUP']
        output = pipe_util.do_command(cmd, logger)

        # save time/mem to db
        df = time_util.store_time(uuid, cmd, output, logger)
        df['bam_name'] = readgroup_bam_name
        unique_key_dict = {'uuid': uuid, 'bam_name': readgroup_bam_name}
        table_name = 'time_mem_picard_calculatehsmetrics'
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)

        # save stats to db
        table_name = 'picard_calculatehsmetrics'
        select = 'BAIT_SET'
        df = picard_util.picard_select_tsv_to_df(uuid, bam_path, stats_path, logger)
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)


        pipe_util.create_already_step(step_dir, readgroup_bam_name + '_calculatehsmetrics', logger)
        logger.info('completed running step `CalculateHsMetrics` of: %s' % readgroup_bam_name)

    return
