import getpass
import os

import pandas as pd

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util


def samtools_stats_to_dict(uuid, bam_path, stats_file, logger):
    data_dict = dict()
    values_to_store = ['raw total sequences:', 'filtered sequences:', 'sequences:', 'is sorted:', '1st fragments:',
                     'last fragments:', 'reads mapped:', 'reads mapped and paired:', 'reads unmapped:',
                     'reads properly paired:', 'reads paired:', 'reads duplicated:', 'reads MQ0:', 'reads QC failed:',
                     'non-primary alignments:', 'total length:', 'bases mapped:', 'bases mapped (cigar):', 'bases trimmed:',
                     'bases duplicated:', 'mismatches:', 'error rate:', 'average length:', 'maximum length:', 'average quality:',
                     'insert size average:', 'insert size standard deviation:', 'inward oriented pairs:',
                     'outward oriented pairs:', 'pairs with other orientation:', 'pairs on different chromosomes:']
    with open(stats_file, 'r') as stats_open:
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



def samtools_stats(uuid, bam_path, input_state, engine, logger):
    step_dir = os.getcwd()
    bam_name = os.path.basename(bam_path)
    bam_base, bam_ext = os.path.splitext(bam_name)
    stats_file = 'samtools_stats_' + bam_base + '.txt'

    if pipe_util.already_step(step_dir, 'samtools_stats_' + bam_base, logger):
        logger.info('already completed step `samtools stats` of: %s' % bam_name)
    else:
        logger.info('running step `samtools stats` of: %s' % bam_name)
        
        home_dir = os.path.join('/home', getpass.getuser()) #cwltool sets HOME to /var/spool/cwl, so need to be explicit
        samtools_path = os.path.join(home_dir, '.local', 'bin', 'samtools')

        cmd = [samtools_path, 'stats', bam_path ]
        stats_output = pipe_util.do_command(cmd, logger)
        with open(stats_file, 'w') as stats_file_open:
            for aline in stats_output.decode().format():
                stats_file_open.write(aline)

        #save time/mem to db
        df = time_util.store_time(uuid, cmd, stats_output, logger)
        df['bam_name'] = bam_name
        df['input_state'] = input_state
        unique_key_dict = {'uuid': uuid, 'bam_name': bam_name}
        table_name = 'time_mem_samtools_stats'
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        pipe_util.create_already_step(step_dir, 'samtools_stats_' + bam_base, logger)
        logger.info('completed running step `samtools stats` of: %s' % bam_name)



    #save stats to db
    if pipe_util.already_step(step_dir, 'samtools_stats_' + bam_base + '_db', logger):
        logger.info('already stored `samtools stats` of %s to db' % bam_name)
    else:
        data_dict = samtools_stats_to_dict(uuid, bam_path, stats_file, logger)
        data_dict['uuid'] = [uuid]
        data_dict['bam_name'] = bam_name
        df = pd.DataFrame(data_dict)
        table_name = 'samtools_stats'
        unique_key_dict = {'uuid': uuid, 'bam_name': bam_name}
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        pipe_util.create_already_step(step_dir, 'samtools_stats_' + bam_base + '_db', logger)
        logger.info('completed storing `samtools stats` of %s to db' % bam_name)
    return
