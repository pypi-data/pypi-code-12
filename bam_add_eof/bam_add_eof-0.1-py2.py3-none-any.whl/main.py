#!/usr/bin/env python

import argparse
import logging
import os
import shutil

import sqlalchemy

from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import df_util
from cdis_pipe_utils import time_util

def rebam(uuid, bam_path, engine, logger):
    bam_name = os.path.basename(bam_path)
    home_dir = os.path.join('/home', getpass.getuser()) #cwltool sets HOME to /var/spool/cwl, so need to be explicit
    samtools_path = os.path.join(home_dir, '.local', 'bin', 'samtools')
    cmd = [samtools_path, 'view', '-hb', bam_path, '>', bam_name]
    shell_cmd = ' '.join(cmd)
    output = pipe_util.do_shell_command(shell_cmd, logger)
    df = time_util.store_time(uuid, shell_cmd, output, logger)
    df['bam_name'] = bam_name
    unique_key_dict = {'uuid': uuid, 'bam_name': bam_name}
    table_name = 'time_mem_samtools_view_hb'
    df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)

def missing_eof(bam_path, picard_validation_path, engine, logger):
    rebam_str = 'Older BAM file -- does not have terminator block'
    with open(picard_validation_path, 'r') as validate_path_open:
        for line in validate_path_open:
            if rebam_str in line:
                logger.info('found %s' % rebam_str)
                return True
    return False

def main():
    parser = argparse.ArgumentParser('add EOF if missing in BAM')

    # Logging flags.
    parser.add_argument('-d', '--debug',
        action = 'store_const',
        const = logging.DEBUG,
        dest = 'level',
        help = 'Enable debug logging.',
    )
    parser.set_defaults(level = logging.INFO)

    # Required flags.
    parser.add_argument('-u', '--uuid',
                         required = True,
                        help = 'analysis_id string',
    )
    parser.add_argument('-b', '--bam_path',
                        required = True,
                        help = 'BAM file.'
    )
    parser.add_argument('-v', '--picard_validation_path',
                        required = True,
                        help = 'output from picard ValidateSamFile'
    )

    args = parser.parse_args()
    uuid = args.uuid
    bam_path = args.bam_path
    picard_validation_path = args.picard_validation_path
    
    tool_name = 'bam_add_eof'
    logger = pipe_util.setup_logging(tool_name, args, uuid)

    sqlite_name = uuid + '.db'
    engine_path = 'sqlite:///' + sqlite_name
    engine = sqlalchemy.create_engine(engine_path, isolation_level='SERIALIZABLE')

    hostname = os.uname()[1]
    logger.info('hostname=%s' % hostname)

    bam_name = os.path.basename(bam_path)
    if missing_eof(bam_path, picard_validation_path, engine, logger):
        logger.info('performing rebam() of %s' % bam_name)
        rebam(uuid, bam_path, engine, logger)
    else:
        logger.info('performing copyfile() of %s as has EOF' % bam_name)
        shutil.copyfile(bam_path, bam_name)
    return


if __name__ == '__main__':
    main()
