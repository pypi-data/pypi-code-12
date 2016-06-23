#!/usr/bin/env python

import argparse
import getpass
import logging
import os
import subprocess

from cdis_pipe_utils import pipe_util

def remover(uuid, fastq_path, logger):
    fastq_name = os.path.basename(fastq_path)
    logger.info('running rmdup of: %s' % fastq_name)
    decomp_cmd = [ 'zcat', '"' + fastq_path + '"' ]
    home_dir = os.path.join('/home', getpass.getuser()) #cwltool sets HOME to /var/spool/cwl, so need to be explicit
    python_cmd = os.path.join(home_dir, '.virtualenvs', 'p3', 'bin', 'python3')
    this_dir = os.path.dirname(os.path.realpath(__file__))
    rmdup_cmd_path = os.path.join(this_dir, 'remove_duplicate_fastq_matepair.py')
    time_path = os.path.join('/usr', 'bin', 'time')
    rmdup_cmd = [ time_path, rmdup_cmd_path, '--fastq_name', fastq_name , '--uuid', uuid, '-' ]
    comp_cmd = [ 'gzip', '-', '>', fastq_name ]
    decomp_cmd_shell = ' '.join(decomp_cmd)
    rmdup_cmd_shell = ' '.join(rmdup_cmd)
    comp_cmd_shell = ' '.join(comp_cmd)
    shell_cmd = decomp_cmd_shell + ' | ' + python_cmd + ' ' + rmdup_cmd_shell + ' | ' + comp_cmd_shell
    logger.info('remove_duplicate_reads() shell_cmd=%s' % shell_cmd)
    output = subprocess.check_output(shell_cmd, env=env, stderr=subprocess.STDOUT, shell=True)
    logger.info('contents of output(s)=%s' % output.decode().format())
    return

def main():
    parser = argparse.ArgumentParser('call duplicate fastq read remover')

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
                         required = True
    )
    parser.add_argument('-f', '--fastq_path',
                        required = True
    )

    args = parser.parse_args()
    uuid = args.uuid
    fastq_path = args.fastq_path
    
    tool_name = 'remove_duplicate_fastq_matepair_main'
    logger = pipe_util.setup_logging(tool_name, args, uuid)

    hostname = os.uname()[1]
    logger.info('hostname=%s' % hostname)
    
    remover(uuid, fastq_path, logger)
    
    return


if __name__ == '__main__':
    main()
