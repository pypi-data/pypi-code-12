import getpass
import os

import pandas as pd

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util


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


def samtools_flagstat(uuid, bam_path, input_state, engine, logger):
    step_dir = os.getcwd()
    bam_name = os.path.basename(bam_path)
    bam_base, bam_ext = os.path.splitext(bam_name)
    flagstat_outfile = 'samtools_flagstat_' + bam_base + '.txt'
    flagstat_path = os.path.join(step_dir, flagstat_outfile)

    if pipe_util.already_step(step_dir, 'samtools_flagstat_' + bam_base, logger):
        logger.info('already completed step `samtools flagstat of: %s' % bam_name)
    else:
        logger.info('running step stat of: %s' % bam_path)

        home_dir = os.path.join('/home', getpass.getuser()) #cwltool sets HOME to /var/spool/cwl, so need to be explicit
        samtools_path = os.path.join(home_dir, '.local', 'bin', 'samtools')

        cmd = [samtools_path, 'flagstat', bam_path ]
        flagstat_output = pipe_util.do_command(cmd, logger)
        with open(flagstat_path, 'w') as flagstat_path_open:
            for aline in flagstat_output.decode().format():
                flagstat_path_open.write(aline)
        #save time/mem to db
        df = time_util.store_time(uuid, cmd, flagstat_output, logger)
        df['bam_name'] = bam_name
        df['input_state'] = input_state
        table_name = 'time_mem_samtools_flagstat'
        unique_key_dict = {'uuid': uuid, 'bam_name': bam_name}
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        pipe_util.create_already_step(step_dir, 'samtools_flagstat_' + bam_base, logger)
        logger.info('completed running step `samtools flagstat` of: %s' % bam_name)


    #save stats to db
    if pipe_util.already_step(step_dir, 'samtools_flagstat_' + bam_base + '_db', logger):
        logger.info('already stored `samtools flagstat` of %s to db' % bam_name)
    else:
        data_dict = samtools_flagstat_to_dict(uuid, bam_path, flagstat_path, logger)
        data_dict['uuid'] = [uuid]
        data_dict['bam_name'] = bam_name
        data_dict['input_state'] = input_state
        df = pd.DataFrame(data_dict)
        table_name = 'samtools_flagstat'
        unique_key_dict = {'uuid': uuid, 'bam_path': bam_path}
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        pipe_util.create_already_step(step_dir, 'samtools_flagstat_' + bam_base + '_db', logger)
        logger.info('completed storing `samtools flagstat` of %s to db' % bam_name)
    return
