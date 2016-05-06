import json
import os

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util

from tools import picard_util

twentyseven_barcodes_list = [
    'TARGET-30-NAABZJ-01A-01D',
    'TARGET-30-NAABZJ-13A-01D',
    'TARGET-30-NAABZJ-50.1A-01D',
    'TARGET-30-NAABZJ-50.2A-01D',
    'TARGET-30-NAABZK-13A-01D',
    'TARGET-30-NAABZK-50.1A-01D',
    'TARGET-30-NAABZK-50.2A-01D',
    'TARGET-30-NAABZK-50.3A-01D',
    'TARGET-30-NAABZL-13B-01D',
    'TARGET-30-NAABZL-15C-01D',
    'TARGET-30-NAABZL-50.1A-01D',
    'TARGET-30-NAABZL-50.2A-01D',
    'TARGET-30-NAABZM-13A-01D',
    'TARGET-30-NAABZM-50.1A-01D',
    'TARGET-30-NAABZM-50.2A-01D',
    'TARGET-30-NAABZN-13A-01D',
    'TARGET-30-NAABZN-50.1A-01D',
    'TARGET-30-NAABZN-50.2D-01D',
    'TARGET-30-NAABZN-60A-01D',
    'TARGET-30-PAMYEF-13A-01D',
    'TARGET-30-PAMYEF-50.1A-01D',
    'TARGET-30-PAMYEF-50.2A-01D',
    'TARGET-30-PAMYEF-60A-01D',
    'TARGET-30-PASXWX-13B-01D',
    'TARGET-30-PASXWX-50.1B-01D',
    'TARGET-30-PASXWX-50.2A-01D',
    'TARGET-30-PASXWX-60B-01D'
]

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
        logger.info('already completed step `validate` of: %s' % bam_name)
    else:
        logger.info('running step `CalculateHsMetrics` of: %s' % bam_name)

        if wxs_dict['target_center_name']: # TARGET exome
            target_center_name = wxs_dict['target_center_name']
            if target_center_name == 'BCG-DANVERS':
                target_interval = 'S04380110_Covered.hg38.list'
                bait_interval = 'S04380110_Covered.hg38.list'
            elif target_center_name == 'BCM':
                preharmonize_bam_name = os.path.basename(preharmonize_bam_path)
                preharmonize_bam_barcode, ext = os.path.splitext(preharmonize_bam_name)
                if preharmonize_bam_barcode in twentyseven_barcodes_list:
                    target_interval = 'VCRome_2_1_hg19_primary_targets.hg38.list'
                    bait_interval = 'VCRome_2_1_hg19_capture_targets.hg38.list'
                else:
                    target_interval = 'SeqCap_EZ_Exome_v2.hg38.list'
                    bait_interval = 'SeqCap_EZ_Exome_v2.hg38.list'
            elif target_center_name == 'BI':
                target_interval = 'whole_exome_agilent_1.1_refseq_plus_3_boosters.targetIntervals.hg38.list'
                bait_interval = 'whole_exome_agilent_1.1_refseq_plus_3_boosters.baitIntervals.hg38.list'
            elif target_center_name == 'NCI-MELZTER':
                target_interval = 'Agilent SureSelect Human All Exon v3'
                bait_interval = 'Agilent SureSelect Human All Exon v3'
            else:
                logger.debug('TARGET center not known. Call someone.')
                sys.exit(1)
        else: #TCGA exome
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
        df['bam_name'] = bam_name
        df['input_state'] = input_state
        unique_key_dict = {'uuid': uuid, 'bam_name': bam_name}
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
