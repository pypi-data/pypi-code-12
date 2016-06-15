#!/usr/bin/env python

import argparse
import getpass
import logging
import os
import sys

import sqlalchemy

from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util
from cdis_pipe_utils import df_util

def get_bam_header(bam_path, step_dir, engine, logger):
    bam_name = os.path.basename(bam_path)
    header_name = bam_name + '.header'
    header_path = os.path.join(step_dir, header_name)

    home_dir = os.path.join('/home', getpass.getuser()) #cwltool sets HOME to /var/spool/cwl, so need to be explicit
    samtools_path = os.path.join(home_dir, '.local', 'bin', 'samtools')
    cmd = [samtools_path, 'view', '-H', bam_path, '>', header_path]
    shell_cmd = ' '.join(cmd)
    pipe_util.do_shell_command(shell_cmd, logger)
    return header_path

def reheader_bam(uuid, bam_path, input_state, engine, logger):
    step_dir = os.getcwd()
    bam_name = os.path.basename(bam_path)
    if pipe_util.already_step(step_dir, bam_name + '_reheader', logger):
        logger.info('already completed step `samtools reheader` of %s to %s' % (bam_path, bam_name))
    else:
        logger.info('running step `samtools reheader` of %s to %s' % (bam_path, bam_name))
        home_dir = os.path.join('/home', getpass.getuser()) #cwltool sets HOME to /var/spool/cwl, so need to be explicit

        #orig header path
        orig_bam_header_path = get_bam_header(bam_path, step_dir, engine, logger)

        #new header path
        reheader_path = os.path.join(step_dir, bam_name + '.reheader')
        cmd = ['head', '-n1', orig_bam_header_path, '>', reheader_path]
        shell_cmd = ' '.join(cmd)
        pipe_util.do_shell_command(shell_cmd, logger)

        #remove @SQ from orig header
        cmd = ["sed", "-i", "'/^@SQ/d'", orig_bam_header_path]
        shell_cmd = ' '.join(cmd)
        pipe_util.do_shell_command(shell_cmd, logger)

        #new @SQ
        python_version = str(sys.version_info.major) + '.' + str(sys.version_info.minor)
        gdc_sq_header_path = os.path.join(home_dir, '.virtualenvs', 'p3','GRCh38.d1.vd1.dict')

        #cat new@SQ to orig header
        cmd = ['cat',gdc_sq_header_path, '>>', reheader_path]
        shell_cmd = ' '.join(cmd)
        pipe_util.do_shell_command(shell_cmd, logger)

        #add program info to new header
        cmd = ['tail', '-n', '+2', orig_bam_header_path, '>>', reheader_path]
        shell_cmd = ' '.join(cmd)
        pipe_util.do_shell_command(shell_cmd, logger)

        #reheader BAM
        samtools_path = os.path.join(home_dir, '.local', 'bin', 'samtools')
        cmd = [samtools_path, 'reheader', reheader_path, bam_path, '>', bam_name ]
        shell_cmd = ' '.join(cmd)
        output = pipe_util.do_shell_command(shell_cmd, logger)
        df = time_util.store_time(uuid, shell_cmd, output, logger)
        df['bam'] = bam_name
        df['input_state'] = input_state
        unique_key_dict = {'uuid': uuid, 'bam': bam_name}
        table_name = 'time_mem_samtools_reheader'
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)

        logger.info('completed running step `samtools reheader` of %s to %s' % (bam_path, bam_name))
        pipe_util.create_already_step(step_dir, bam_name + '_reheader', logger)
    return bam_name

def main():
    parser = argparse.ArgumentParser('reheader a BAM to include gdc @SQ info')

    # Logging flags.
    parser.add_argument('-d', '--debug',
        action = 'store_const',
        const = logging.DEBUG,
        dest = 'level',
        help = 'Enable debug logging.',
    )
    parser.set_defaults(level = logging.INFO)

    # Tool flags
    parser.add_argument('-b', '--bam_path',
                        required = True
    )
    parser.add_argument('-u', '--uuid',
                        required = True
    )
    parser.add_argument('--input_state',
                        required = True
    )

    args = parser.parse_args()
    bam_path = args.bam_path
    uuid = args.uuid
    input_state = args.input_state

    bam_name = os.path.basename(bam_path)

    logger = pipe_util.setup_logging('bam_reheader', args, bam_name)

    sqlite_name =  uuid + '.db'
    engine_path = 'sqlite:///' + sqlite_name
    engine = sqlalchemy.create_engine(engine_path, isolation_level='SERIALIZABLE')

    hostname = os.uname()[1]
    logger.info('hostname=%s' % hostname)

    bam_name = reheader_bam(uuid, bam_path, input_state, engine, logger)
    
    return


if __name__ == '__main__':
    main()
