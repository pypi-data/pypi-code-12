import os

import pandas as pd

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util

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

def samtools_idxstat_to_df(uuid, bam_path, idx_outfile, logger):
    logger.info('storing idx_outfile %s to db' % idx_outfile)
    df = all_tsv_to_df(idx_outfile, logger)
    df.columns = ['NAME', 'LENGTH', 'ALIGNED_READS', 'UNALIGNED_READS']
    logger.info('df=\n%s' % df)
    return df


def samtools_idxstats(uuid, bam_path, input_state, engine, logger):
    step_dir = os.getcwd()
    bam_name = os.path.basename(bam_path)
    bam_base, bam_ext = os.path.splitext(bam_name)
    idx_outfile = 'samtools_idxstats_' + bam_base + '.txt'
    if pipe_util.already_step(step_dir, 'samtools_' + bam_base + '_idxstats', logger):
        logger.info('already completed step `samtools idxstats` of: %s' % bam_path)
    else:
        logger.info('running step `samtools idxstats` of: %s' % bam_name)

        home_dir = os.path.join('/home', getpass.getuser()) #cwltool sets HOME to /var/spool/cwl, so need to be explicit
        samtools_path = os.path.join(home_dir, '.local', 'bin', 'samtools')

        cmd = [samtools_path, 'idxstats', bam_path ]
        idxstats_output = pipe_util.do_command(cmd, logger)
        with open(idx_outfile, 'w') as idx_outfile_open:
            for aline in idxstats_output.decode().format():
                idx_outfile_open.write(aline)

        #save time/mem to db
        df = time_util.store_time(uuid, cmd, idxstats_output, logger)
        df['bam_name'] = bam_name
        df['input_state'] = input_state
        unique_key_dict = {'uuid': uuid, 'bam_name': bam_name}
        table_name = 'time_mem_samtools_idxstats'
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        pipe_util.create_already_step(step_dir, 'samtools_' + bam_base + '_idxstats', logger)
        logger.info('completed running step `samtools idxstats` of: %s' % bam_name)


    #save stats to db
    if pipe_util.already_step(step_dir, 'samtools_' + bam_base + '_idxstats_db', logger):
        logger.info('already stored `samtools idxstats` to db: %s' % idx_outfile)
    else:
        logger.info('storing `samtools idxstats` to db: %s' % idx_outfile)
        df = samtools_idxstat_to_df(uuid, bam_path, idx_outfile, logger)
        df['uuid'] = uuid
        df['bam_name'] = bam_name
        df['input_state'] = input_state
        table_name = 'samtools_idxstats'
        unique_key_dict = {'uuid': uuid, 'bam_name': bam_name}
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        pipe_util.create_already_step(step_dir, 'samtools_' + bam_base + '_idxstats_db', logger)
        logger.info('completed storing `samtools idxstats` to db: %s' % idx_outfile)
    return
