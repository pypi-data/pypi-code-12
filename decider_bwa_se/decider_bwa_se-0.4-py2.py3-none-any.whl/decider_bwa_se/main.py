#!/usr/bin/env python

import argparse
import logging
import os
import shutil
import sys

from cdis_pipe_utils import pipe_util

def copy_from_list(file_path_list, file_name):
    for file_path in file_path_list:
        if file_name == os.path.basename(file_path):
            shutil.copyfile(file_path, file_name)
    return

def decider(uuid, fastq_path_list, readgroup_path_list, logger):
    for fastq_path in fastq_path_list:
        fastq_name = os.path.basename(fastq_path)
        copy_from_list(fastq_path_list, fastq_name)
        if fastq_name.endswith('_s.fq.gz'):
            readgroup_name = fastq_name.replace('_s.fq.gz', '.json')
            copy_from_list(readgroup_path_list, readgroup_name)
        elif fastq_name.endswith('_o1.fq.gz'):
            readgroup_name = fastq_name.replace('_o1.fq.gz', '.json')
            copy_from_list(readgroup_path_list, readgroup_name)
        elif fastq_name.endswith('_o2.fq.gz'):
            readgroup_name = fastq_name.replace('_o2.fq.gz', '.json')
            copy_from_list(readgroup_path_list, readgroup_name)
        else:
            logger.info('should not be here: %s' % fastq_name)
            sys.exit(1)
    return

def main():
    parser = argparse.ArgumentParser('SE bwa decider')

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
                        action = 'append',
                        required = True
    )
    parser.add_argument('-r', '--readgroup_path',
                        action = 'append',
                        required = True
    )

    args = parser.parse_args()
    uuid = args.uuid
    fastq_path_list = args.fastq_path
    readgroup_path_list = args.readgroup_path
    
    tool_name = 'decider_bwa_se'
    logger = pipe_util.setup_logging(tool_name, args, uuid)

    hostname = os.uname()[1]
    logger.info('hostname=%s' % hostname)
    
    decider(uuid, fastq_path_list, readgroup_path_list, logger)
    
    return


if __name__ == '__main__':
    main()
