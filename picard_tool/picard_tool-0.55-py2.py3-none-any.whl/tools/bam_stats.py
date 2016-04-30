from collections import defaultdict
import json
import logging
import os
import pickle
import sys
#
import pandas as pd
#
from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util


def get_key_interval_dicts_from_json(key_intervalname_json_path, logger):
    with open(key_intervalname_json_path, 'r') as json_path_open:
        json_data = json.load(json_path_open)
    return json_data


def samtools_flagstat_to_dict(uuid, bam_path, flagstat_path, logger):
    data_dict = dict()
    values_to_store = ['in total', 'mapped', 'paired in sequencing', 'read1', 'read2']
    with open(flagstat_path, 'r') as flagstat_open:
        for line in flagstat_open:
            line = line.strip('\n')
            for value_to_store in values_to_store:
                if value_to_store in line:
                    if value_to_store == 'mapped':
                        if 'mate' in line:  # avoid 'with mate mapped to a different chr'/'with itself and mate mapped'
                            continue
                    line_split = line.split(' ')
                    first_val = line_split[0]
                    second_val = line_split[2]
                    total_val = str(int(first_val) + int(second_val))
                    data_dict[value_to_store] = total_val
    return data_dict


def samtools_stats_to_dict(uuid, bam_path, stats_path, logger):
    data_dict = dict()
    values_to_store = ['raw total sequences:', 'filtered sequences:', 'sequences:', 'is sorted:', '1st fragments:',
                     'last fragments:', 'reads mapped:', 'reads mapped and paired:', 'reads unmapped:',
                     'reads properly paired:', 'reads paired:', 'reads duplicated:', 'reads MQ0:', 'reads QC failed:',
                     'non-primary alignments:', 'total length:', 'bases mapped:', 'bases mapped (cigar):', 'bases trimmed:',
                     'bases duplicated:', 'mismatches:', 'error rate:', 'average length:', 'maximum length:', 'average quality:',
                     'insert size average:', 'insert size standard deviation:', 'inward oriented pairs:',
                     'outward oriented pairs:', 'pairs with other orientation:', 'pairs on different chromosomes:']
    with open(stats_path, 'r') as stats_open:
        for line in stats_open:
            line = line.strip('\n')
            if line.startswith('SN\t'):
                line_split = line.split('\t')
                line_key = line_split[1]
                for value_to_store in values_to_store:
                    if value_to_store == line_key:
                        #dict_key='_'.join(value_to_store.strip(':').split(' '))
                        line_value = line_split[2].strip()
                        #data_dict[dict_key]=line_value
                        dict_key = value_to_store.strip(':')
                        if dict_key == 'bases mapped (cigar)':
                            dict_key = 'bases mapped CIGAR'
                        data_dict[dict_key] = line_value
    return data_dict


def all_tsv_to_df(tsv_path, logger):
    logger.info('all_tsv_to_df open: %s' % tsv_path)
    data_dict = dict()
    with open(tsv_path, 'r') as tsv_open:
        i = 0
        for line in tsv_open:
            line = line.strip('\n')
            line_split = line.split('\t')
            data_dict[i] = line_split
            i += 1
    logger.info('data_dict=\n%s' % data_dict)
    df = pd.DataFrame.from_dict(data_dict, orient='index')
    logger.info('df=\n%s' % df)
    return df


def samtools_idxstat_to_df(uuid, bam_path, idx_path, logger):
    logger.info('storing idx_path %s to db' % idx_path)
    df = all_tsv_to_df(idx_path, logger)
    df.columns = ['NAME', 'LENGTH', 'ALIGNED_READS', 'UNALIGNED_READS']
    logger.info('df=\n%s' % df)
    return df


def picard_select_tsv_to_df(stats_path, select, logger):
    read_header = False
    data_dict = dict()
    if not os.path.exists(stats_path):
        logger.info('the stats file %s do not exist, so return None' % stats_path)
        return None
    logger.info('stats_path=%s' % stats_path)
    with open(stats_path, 'r') as stats_open:
        i = 0
        for line in stats_open:
            line = line.strip('\n')
            logger.info('line=\n%s' % line)
            if line.startswith('#'):
                continue
            line_split = line.split('\t')
            logger.info('len(line_split)=%s' % str(len(line_split)))
            if not read_header and len(line_split) > 1:
                if select == line_split[0]:
                    header = line_split
                    read_header = True
            elif read_header and len(line_split) == 1:
                df_index = list(range(len(data_dict)))
                df = pd.DataFrame.from_dict(data_dict, orient='index')
                logger.info('df=\n%s' % df)
                df.columns = header
                return df
            elif read_header and len(line_split) > 0:
                if len(line_split) == len(header):
                    logger.info('store line=\n%s' % line)
                    data_dict[i] = line_split
                    i += 1
            elif not read_header and len(line_split) == 1:
                continue
            else:
                logger.info('strange line: %s' % line)
                sys.exit(1)
    if not read_header:
        logger.info('bam file was probably too small to generate stats as header not read: %s' % stats_path)
        return None
    logger.debug('no data saved to df')
    sys.exit(1)
    return None


def picard_CollectAlignmentSummaryMetrics_to_df(uuid, bam_path, stats_path, logger):
    select = 'CATEGORY'
    df = picard_select_tsv_to_df(stats_path, select, logger)
    return df


def picard_CollectInsertSizeMetrics_metrics_to_df(uuid, bam_path, stats_path, logger):
    select = 'MEDIAN_INSERT_SIZE'
    df = picard_select_tsv_to_df(stats_path, select, logger)
    return df


def picard_CollectInsertSizeMetrics_histogram_to_df(uuid, bam_path, stats_path, logger):
    select = 'insert_size'
    df = picard_select_tsv_to_df(stats_path, select, logger)
    if df is not None:
        keep_column_list = ['insert_size', 'All_Reads.fr_count', 'All_Reads.rf_count', 'All_Reads.tandem_count']
        drop_column_list = [ column for column in df.columns if column not in keep_column_list]
        needed_column_list = [ column for column in keep_column_list if column not in df.columns ]
        #drop readgroup specific columns as the bam is already one readgroup
        logger.info('pre drop df=\n%s' % df)
        df.drop(drop_column_list, axis=1, inplace=True)
        logger.info('post drop df=\n%s' % df)
        #add columns that could be present in other files
        for needed_column in needed_column_list:
            df[needed_column] = None
    return df


def picard_QualityScoreDistribution_metrics_to_df(uuid, bam_path, stats_path, logger):
    select = ''  # ###
    df = picard_select_tsv_to_df(stats_path, select, logger)
    return df


def picard_QualityScoreDistribution_histogram_to_df(uuid, bam_path, stats_path, logger):
    select = 'QUALITY'
    df = picard_select_tsv_to_df(stats_path, select, logger)
    return df


def picard_MeanQualityByCycle_metrics_to_df(uuid, bam_path, stats_path, logger):
    select = ''  # ##
    df = picard_select_tsv_to_df(stats_path, select, logger)
    return df


def picard_MeanQualityByCycle_histogram_to_df(uuid, bam_path, stats_path, logger):
    select = 'CYCLE'
    df = picard_select_tsv_to_df(stats_path, select, logger)
    return df


def picard_CollectBaseDistributionByCycle_to_df(uuid, bam_path, stats_path, logger):
    select = 'READ_END'
    df = picard_select_tsv_to_df(stats_path, select, logger)
    return df


def picard_CollectGcBiasMetrics_summary_to_df(uuid, bam_path, stats_path, logger):
    select = 'ACCUMULATION_LEVEL'
    stats_path += '.summary_output'
    df = picard_select_tsv_to_df(stats_path, select, logger)
    return df


def picard_CollectGcBiasMetrics_detail_to_df(uuid, bam_path, stats_path, logger):
    select = 'ACCUMULATION_LEVEL'
    df = picard_select_tsv_to_df(stats_path, select, logger)
    return df


def picard_CollectWgsMetrics_metrics_to_df(uuid, bam_path, stats_path, logger):
    select = 'GENOME_TERRITORY'
    df = picard_select_tsv_to_df(stats_path, select, logger)
    return df


def picard_CollectWgsMetrics_histogram_to_df(uuid, bam_path, stats_path, logger):
    select = 'coverage'
    df = picard_select_tsv_to_df(stats_path, select, logger)
    return df


def picard_CalculateHsMetrics_to_df(uuid, bam_path, stats_path, logger):
    select = 'BAIT_SET'
    df = picard_select_tsv_to_df(stats_path, select, logger)
    return df


def do_samtools_idxstats(uuid, bam_path, reference_fasta_path, engine, logger):
    step_dir = os.path.dirname(bam_path)
    bam_name = os.path.basename(bam_path)
    bam_base, bam_ext = os.path.splitext(bam_name)
    idx_outfile = 'samtools_idxstats_' + bam_base + '.txt'
    idx_path = os.path.join(step_dir, idx_outfile)
    if pipe_util.already_step(step_dir, 'samtools_' + bam_base + '_idxstats', logger):
        logger.info('already completed step `samtools idxstats` of: %s' % bam_path)
    else:
        logger.info('running step `samtools idxstats` of: %s' % bam_path)
        cmd = ['samtools', 'idxstats', '"' + bam_path + '"', '>', '"' + idx_path + '"' ]
        shell_cmd = ' '.join(cmd)
        idxstats_output = pipe_util.do_shell_command(shell_cmd, logger)

        #save time/mem to db
        df = time_util.store_time(uuid, cmd, idxstats_output, logger)
        df['bam_path'] = bam_path
        df['reference_fasta_path'] = reference_fasta_path
        unique_key_dict = {'uuid': uuid, 'bam_path': bam_path}
        table_name = 'time_mem_samtools_idxstats'
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        pipe_util.create_already_step(step_dir, 'samtools_' + bam_base + '_idxstats', logger)
        logger.info('completed running step `samtools idxstats` of: %s' % bam_path)


    #save stats to db
    if pipe_util.already_step(step_dir, 'samtools_' + bam_base + '_idxstats_db', logger):
        logger.info('already stored `samtools idxstats` to db: %s' % idx_outfile)
    else:
        logger.info('storing `samtools idxstats` to db: %s' % idx_outfile)
        df = samtools_idxstat_to_df(uuid, bam_path, idx_path, logger)
        df['uuid'] = uuid
        df['bam_path'] = bam_path
        df['reference_fasta_path'] = reference_fasta_path
        table_name = 'samtools_idxstats'
        unique_key_dict = {'uuid': uuid, 'bam_path': bam_path, 'reference_fasta_path': reference_fasta_path}
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        pipe_util.create_already_step(step_dir, 'samtools_' + bam_base + '_idxstats_db', logger)
        logger.info('completed storing `samtools idxstats` to db: %s' % idx_outfile)
    return


def do_samtools_flagstat(uuid, bam_path, reference_fasta_path, engine, logger):
    step_dir = os.path.dirname(bam_path)
    bam_name = os.path.basename(bam_path)
    bam_base, bam_ext = os.path.splitext(bam_name)
    flagstat_outfile = 'samtools_flagstat_' + bam_base + '.txt'
    flagstat_path = os.path.join(step_dir, flagstat_outfile)

    if pipe_util.already_step(step_dir, 'samtools_flagstat_' + bam_base, logger):
        logger.info('already completed step `samtools flagstat of: %s' % bam_path)
    else:
        logger.info('running step stat of: %s' % bam_path)
        cmd = ['samtools', 'flagstat', bam_path  ]
        flagstat_output = pipe_util.do_command(cmd, logger)
        with open(flagstat_path, 'w') as flagstat_path_open:
            for aline in flagstat_output.decode().format():
                flagstat_path_open.write(aline)
        #save time/mem to db
        df = time_util.store_time(uuid, cmd, flagstat_output, logger)
        df['bam_path'] = bam_path
        df['reference_fasta_path'] = reference_fasta_path
        table_name = 'time_mem_samtools_flagstat'
        unique_key_dict = {'uuid': uuid, 'bam_path': bam_path, 'reference_fasta_path': reference_fasta_path}
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        pipe_util.create_already_step(step_dir, 'samtools_flagstat_' + bam_base, logger)
        logger.info('completed running step `samtools flagstat` of: %s' % bam_path)


    #save stats to db
    if pipe_util.already_step(step_dir, 'samtools_flagstat_' + bam_base + '_db', logger):
        logger.info('already stored `samtools flagstat` of %s to db' % bam_path)
    else:
        data_dict = samtools_flagstat_to_dict(uuid, bam_path, flagstat_path, logger)
        data_dict['uuid'] = [uuid]
        data_dict['bam_path'] = bam_path
        data_dict['reference_fasta_path'] = reference_fasta_path
        df = pd.DataFrame(data_dict)
        table_name = 'samtools_flagstat'
        unique_key_dict = {'uuid': uuid, 'bam_path': bam_path, 'reference_fasta_path': reference_fasta_path}
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        pipe_util.create_already_step(step_dir, 'samtools_flagstat_' + bam_base + '_db', logger)
        logger.info('completed storing `samtools flagstat` of %s to db' % bam_path)
    return


def do_samtools_stats(uuid, bam_path, reference_fasta_path, engine, logger):
    step_dir = os.path.dirname(bam_path)
    bam_name = os.path.basename(bam_path)
    bam_base, bam_ext = os.path.splitext(bam_name)
    stats_outfile = 'samtools_stats_' + bam_base + '.txt'
    stats_path = os.path.join(step_dir, stats_outfile)

    if pipe_util.already_step(step_dir, 'samtools_stats_' + bam_base, logger):
        logger.info('already completed step `samtools stats` of: %s' % bam_path)
    else:
        logger.info('running step `samtools stats` of: %s' % bam_path)
        cmd = ['samtools', 'stats', bam_path ]
        stats_output = pipe_util.do_command(cmd, logger)
        with open(stats_path, 'w') as stats_path_open:
            for aline in stats_output.decode().format():
                stats_path_open.write(aline)

        #save time/mem to db
        df = time_util.store_time(uuid, cmd, stats_output, logger)
        df['bam_path'] = bam_path
        df['reference_fasta_path'] = reference_fasta_path
        unique_key_dict = {'uuid': uuid, 'bam_path': bam_path}
        table_name = 'time_mem_samtools_stats'
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        pipe_util.create_already_step(step_dir, 'samtools_stats_' + bam_base, logger)
        logger.info('completed running step `samtools stats` of: %s' % bam_path)



    #save stats to db
    if pipe_util.already_step(step_dir, 'samtools_stats_' + bam_base + '_db', logger):
        logger.info('already stored `samtools stats` of %s to db' % bam_path)
    else:
        data_dict = samtools_stats_to_dict(uuid, bam_path, stats_path, logger)
        data_dict['uuid'] = [uuid]
        data_dict['bam_path'] = bam_path
        data_dict['reference_fasta_path'] = reference_fasta_path
        df = pd.DataFrame(data_dict)
        table_name = 'samtools_stats'
        unique_key_dict = {'uuid': uuid, 'bam_path': bam_path, 'reference_fasta_path': reference_fasta_path}
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        pipe_util.create_already_step(step_dir, 'samtools_stats_' + bam_base + '_db', logger)
        logger.info('completed storing `samtools stats` of %s to db' % bam_path)
    return


def do_picard_metrics(uuid, bam_path, reference_fasta_path, engine, logger, metrics_type, wxs_dict = None):
    step_dir = os.getcwd()
    bam_name = os.path.basename(bam_path)
    bam_base, bam_ext = os.path.splitext(bam_name)
    home_dir = os.path.expanduser('~')
    picard_dir = os.path.join(home_dir, 'tools', 'picard-tools')
    stats_outfile = 'picard_' + metrics_type + '_' + bam_base
    stats_path = os.path.join(step_dir, stats_outfile)

    if pipe_util.already_step(step_dir, 'picard_' + metrics_type + '_' + bam_base, logger):
        logger.info('already completed step `picard %s` of: %s' % (metrics_type, bam_path))
    else:
        logger.info('running step `picard %s` of: %s' % (metrics_type, bam_path))
        cmd = ['java', '-d64', '-Xmx40G', '-jar', os.path.join(picard_dir, 'picard.jar'), metrics_type, 'INPUT=' + bam_path , 'OUTPUT=' + stats_path , 'REFERENCE_SEQUENCE=' + reference_fasta_path, 'VALIDATION_STRINGENCY=LENIENT', 'TMP_DIR=' + step_dir]
        logger.info('do_picard_metrics() pre-alter cmd=%s' % cmd)
        if metrics_type == 'CollectAlignmentSummaryMetrics':
            pop_item = cmd.pop(8) # remove reference sequence for preharmonized BAMs
            logger.info('CollectAlignmentSummaryMetrics removed: %s' % pop_item)
        if metrics_type == 'CollectMultipleMetrics':
            cmd.append('PROGRAM=CollectAlignmentSummaryMetrics')
            cmd.append('PROGRAM=CollectInsertSizeMetrics')
            cmd.append('PROGRAM=QualityScoreDistribution')
            cmd.append('PROGRAM=MeanQualityByCycle')
            cmd.append('PROGRAM=CollectBaseDistributionByCycle')
            cmd.append('PROGRAM=CollectGcBiasMetrics')
        if metrics_type == 'CalculateHsMetrics':
            bait_intervals_path = wxs_dict['bait_intervals_path']
            target_intervals_path = wxs_dict['target_intervals_path']
            bait_intervals =  'BAIT_INTERVALS=' + bait_intervals_path
            target_intervals = 'TARGET_INTERVALS=' + target_intervals_path
            cmd.append(bait_intervals)
            cmd.append(target_intervals)
        logger.info('do_picard_metrics() post-alter cmd=%s' % cmd)    
        picard_output = pipe_util.do_command(cmd, logger)

        #save time/mem to db
        df = time_util.store_time(uuid, cmd, picard_output, logger)
        df['bam_path'] = bam_path
        df['reference_fasta_path'] = reference_fasta_path
        unique_key_dict = {'uuid': uuid, 'bam_path': bam_path}
        table_name = 'time_mem_picard_' + metrics_type
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        pipe_util.create_already_step(step_dir, 'picard_' + metrics_type + '_' + bam_base, logger)
        logger.info('completed running step `picard %s` of: %s' % (metrics_type, bam_path))


    #save stats to db
    if pipe_util.already_step(step_dir, 'picard_' + metrics_type + '_' + bam_base + '_db', logger):
        logger.info('already stored `picard %s` of %s to db' % (metrics_type, bam_path))
    else:
        df_list = list()
        table_name_list = list()
        ###CASE FOR METRICS###
        logger.info('base stats_path=%s' % stats_path)
        if metrics_type == 'CollectAlignmentSummaryMetrics':
            table_name = 'picard_CollectAlignmentSummaryMetrics'
            df = picard_CollectAlignmentSummaryMetrics_to_df(uuid, bam_path, stats_path, logger)
            if df is not None:
                df_list.append(df)
                table_name_list.append(table_name)
                
        elif metrics_type == 'CollectMultipleMetrics':
            table_name = 'picard_CollectAlignmentSummaryMetrics'
            casm_stats_path = stats_path + '.alignment_summary_metrics'
            logger.info('casm_stats_path=%s' % casm_stats_path)
            df = picard_CollectAlignmentSummaryMetrics_to_df(uuid, bam_path, casm_stats_path, logger)
            if df is not None:
                df_list.append(df)
                table_name_list.append(table_name)

            table_name = 'picard_CollectInsertSizeMetric'
            cism_stats_path = stats_path + '.insert_size_metrics'
            logger.info('cism_stats_path=%s' % cism_stats_path)
            df = picard_CollectInsertSizeMetrics_metrics_to_df(uuid, bam_path, cism_stats_path, logger)
            if df is not None:
                df_list.append(df)
                table_name += '_metrics'
                table_name_list.append(table_name)

            df = picard_CollectInsertSizeMetrics_histogram_to_df(uuid, bam_path, cism_stats_path, logger)
            if df is not None:
                df_list.append(df)
                table_name += '_histogram'
                table_name_list.append(table_name)


            table_name = 'picard_QualityScoreDistribution'
            qsd_stats_path = stats_path + '.quality_distribution_metrics'
            logger.info('qsd_stats_path=%s' % qsd_stats_path)
            df = picard_QualityScoreDistribution_histogram_to_df(uuid, bam_path, qsd_stats_path, logger)
            if df is not None:
                df_list.append(df)
                table_name += '_histogram'
                table_name_list.append(table_name)

            table_name = 'picard_MeanQualityByCycle'
            mqbc_stats_path = stats_path + '.quality_by_cycle_metrics'
            logger.info('mqbc_stats_path=%s' % mqbc_stats_path)
            df = picard_MeanQualityByCycle_histogram_to_df(uuid, bam_path, mqbc_stats_path, logger)
            if df is not None:
                df_list.append(df)
                table_name += '_histogram'
                table_name_list.append(table_name)

            table_name = 'picard_CollectBaseDistributionByCycle'
            cbdbc_stats_path = stats_path + 'base_distribution_by_cycle_metrics'
            logger.info('cbdbc_stats_path=%s' % cbdbc_stats_path)
            df = picard_CollectBaseDistributionByCycle_to_df(uuid, bam_path, stats_path, logger)
            if df is not None:
                df_list.append(df)
                table_name_list.append(table_name)

            table_name = 'picard_CollectGcBiasMetrics'
            cgbm_summary_stats_path = stats_path + '.gc_bias.summary_metrics'
            logger.info('cgbm_detail_stats_path=%s' % cgbm_summary_stats_path)
            df = picard_CollectGcBiasMetrics_summary_to_df(uuid, bam_path, cgbm_summary_stats_path, logger)
            if df is not None:
                df_list.append(df)
                table_name += '_summary'
                table_name_list.append(table_name)

            cgbm_detail_stats_path = stats_path + '.gc_bias.detail_metrics'
            logger.info('cgbm_detail_stats_path=%s' % cgbm_detail_stats_path)
            df = picard_CollectGcBiasMetrics_detail_to_df(uuid, bam_path, cgbm_detail_stats_path, logger)
            if df is not None:
                df_list.append(df)
                table_name += '_detail'
                table_name_list.append(table_name)
        elif metrics_type == 'CollectWgsMetrics':
            table_name = 'picard_' + metrics_type
            df = picard_CollectWgsMetrics_metrics_to_df(uuid, bam_path, stats_path, logger)
            if df is not None:
                df_list.append(df)
                table_name_list.append(table_name)

            df = picard_CollectWgsMetrics_histogram_to_df(uuid, bam_path, stats_path, logger)
            if df is not None:
                df_list.append(df)
                table_name += '_histogram'
                table_name_list.append(table_name)
        elif metrics_type == 'CalculateHsMetrics':
            table_name = 'picard_' + metrics_type
            df = picard_CalculateHsMetrics_to_df(uuid, bam_path, stats_path, logger)
            if df is not None:
                df_list.append(df)
                table_name_list.append(table_name)
        else:
            logger.debug('Unknown metrics_type: %s' % metrics_type)
            sys.exit(1)
        for i, df in enumerate(df_list):
            logger.info('df_list enumerate i=%s:' % i)
            df['uuid'] = uuid
            df['bam_path'] = bam_path
            df['reference_fasta_path'] = reference_fasta_path
            logger.info('metrics_type=%s' % metrics_type)
            logger.info('df=\n%s' % df)
            table_name = table_name_list[i]
            logger.info('\ttable_name=%s' % table_name)
            logger.info('\tdf=%s' % df)
            unique_key_dict = {'uuid': uuid, 'bam_path': bam_path, 'reference_fasta_path': reference_fasta_path}
            df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        pipe_util.create_already_step(step_dir, 'picard_' + metrics_type + '_' + bam_base + '_db', logger)
    logger.info('completed storing `picard %s` of %s to db' % (metrics_type, bam_path))
    return
