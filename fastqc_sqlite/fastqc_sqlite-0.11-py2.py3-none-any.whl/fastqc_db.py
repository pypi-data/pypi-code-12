import os
import shutil
import sys
#
import pandas as pd
#
from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import fastq_util
from cdis_pipe_utils import time_util

def get_total_deduplicated_percentage(fastqc_data_open, logger):
    for line in fastqc_data_open:
        if line.startswith('#Total Deduplicated Percentage'):
            line_split = line.strip('\n').lstrip('#').split('\t')
            return line_split
    logger.debug('get_total_deduplicated_percentage() failed')
    sys.exit(1)


def fastqc_detail_to_df(uuid, fq_path, fastqc_data_path, data_key, engine, logger):
    logger.info('detail step: %s'  % data_key)
    logger.info('fastqc_data_path: %s' % fastqc_data_path)
    process_data = False
    process_header = False
    have_data = False
    with open(fastqc_data_path, 'r') as fastqc_data_open:
        for line in fastqc_data_open:
            #logger.info('line=%s' % line)
            if line.startswith('##FastQC'):
                #logger.info('\tcase 1')
                continue
            elif process_data and not process_header and line.startswith('>>END_MODULE'):
                #logger.info('\tcase 2')
                break
            elif line.startswith(data_key):
                #logger.info('\tcase 3')
                logger.info('fastqc_detail_to_df() found data_key: %s' % data_key)
                process_data = True
            elif process_data and line.startswith('>>END_MODULE'):
                #logger.info('\tcase 4')
                logger.info('fastqc_detail_to_df() >>END_MODULE')
                if data_key == '>>Basic Statistics':
                    value_list = get_total_deduplicated_percentage(fastqc_data_open, logger)
                    row_df = pd.DataFrame([uuid, fq_path] + value_list)
                    row_df_t = row_df.T
                    row_df_t.columns = ['uuid', 'fastq_path'] + header_list
                    #logger.info('9 row_df_t=%s' % row_df_t)
                    df = df.append(row_df_t)
                break
            elif process_data and line.startswith('#'):
                #logger.info('\tcase 5')
                process_header = True
                header_list = line.strip('#').strip().split('\t')
                logger.info('fastqc_detail_to_df() header_list: %s' % header_list)
            elif process_data and process_header:
                #logger.info('\tcase 6')
                logger.info('fastqc_detail_to_df() columns=%s' % header_list)
                df = pd.DataFrame(columns = ['uuid', 'fastq_path'] + header_list)
                process_header = False
                have_data = True
                #logger.info('2 df=%s' % df)
                line_split = line.strip('\n').split('\t')
                logger.info('process_header line_split=%s' % line_split)
                row_df = pd.DataFrame([uuid, fq_path] + line_split)
                row_df_t = row_df.T
                row_df_t.columns = ['uuid', 'fastq_path'] + header_list
                logger.info('1 row_df_t=%s' % row_df_t)
                df = df.append(row_df_t)
                #logger.info('3 df=%s' % df)
            elif process_data and not process_header:
                #logger.info('\tcase 7')
                line_split = line.strip('\n').split('\t')
                logger.info('not process_header line_split=%s' % line_split)
                row_df = pd.DataFrame([uuid, fq_path] + line_split)
                row_df_t = row_df.T
                row_df_t.columns = ['uuid', 'fastq_path'] + header_list
                logger.info('not process_header line_split=%s' % line_split)
                logger.info('2 row_df_t=%s' % row_df_t)
                df = df.append(row_df_t)
                #logger.info('4 df=%s' % df)
            elif not process_data and not process_header:
                #logger.info('\tcase 8')
                continue
            else:
                #logger.info('\tcase 9')
                logger.debug('fastqc_detail_to_df(): should not be here')
                sys.exit(1)
    if have_data:
        logger.info('complete df=%s' % df)
        return df
    else:
        logger.info('no df')
        return None
    logger.debug('fastqc_detail_to_df(): should not reach end of function')
    sys.exit(1)


def fastqc_summary_to_dict(data_dict, fastqc_summary_path, engine, logger):
    logger.info('fastqc_summary_path=%s' % fastqc_summary_path)
    with open(fastqc_summary_path, 'r') as fastqc_summary_open:
        for line in fastqc_summary_open:
            line_split = line.split('\t')
            line_key = line_split[1].strip()
            line_value = line_split[0].strip()
            data_dict[line_key] = line_value
    return data_dict



def fastqc_db(uuid, fastqc_zip_path, engine, logger):
    fastqc_zip_name = os.path.basename(fastqc_zip_path)
    step_dir = os.getcwd()
    fastqc_zip_base, fastqc_zip_ext = os.path.splitext(fastqc_zip_name)
    if pipe_util.already_step(step_dir, 'fastqc_db_' + fastqc_zip_base, logger):
        logger.info('already completed step `fastqc db`: %s' % fq_path)
    else:
        logger.info('writing `fastqc db`: %s' % fastqc_zip_path)

        #extract fastqc report
        cmd = ['unzip', fastqc_zip_path, '-d', step_dir]
        output = pipe_util.do_command(cmd, logger)
        
        fastqc_data_path = os.path.join(step_dir, fastqc_zip_base, 'fastqc_data.txt')
        fastqc_summary_path = os.path.join(step_dir, fastqc_zip_base, 'summary.txt')
        
        summary_dict = dict()
        summary_dict['uuid'] = [uuid]  # need one non-scalar value in df to avoid index
        summary_dict['fastq_name'] = fastq_name
        summary_dict = fastqc_summary_to_dict(summary_dict, fastqc_summary_path, engine, logger)
        df = pd.DataFrame(summary_dict)
        table_name = 'fastqc_summary'
        unique_key_dict = {'uuid': uuid, 'fastq_name': fastq_name}
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        data_key_list = ['>>Basic Statistics', '>>Per base sequence quality', '>>Per tile sequence quality',
                           '>>Per sequence quality scores', '>>Per base sequence content', '>>Per sequence GC content',
                           '>>Per base N content', '>>Sequence Length Distribution', '>>Sequence Duplication Levels',
                           '>>Overrepresented sequences', '>>Adapter Content', '>>Kmer Content']
        for data_key in data_key_list:
            df = fastqc_detail_to_df(uuid, fq_path, fastqc_data_path, data_key, engine, logger)
            if df is None:
                continue
            table_name = 'fastqc_data_' + '_'.join(data_key.lstrip('>>').strip().split(' '))
            logger.info('fastqc_to_db() table_name=%s' % table_name)
            unique_key_dict = {'uuid': uuid, 'fastq_path': fq_path}
            df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)

        shutil.rmtree(os.path.join(step_dir, fastqc_zip_base))
        pipe_util.create_already_step(step_dir, 'fastqc_db_' + fastqc_zip_base, logger)
        logger.info('completed writing `fastqc db`: %s' % fq_path)
    return
