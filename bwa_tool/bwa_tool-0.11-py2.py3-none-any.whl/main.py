#!/usr/bin/env python

import argparse
import logging
import os
import sys

import sqlalchemy

from cdis_pipe_utils import pipe_util

import tools.bwa_mem as bwa_mem

def is_nat(x):
    '''
    Checks that a value is a natural number.
    '''
    if int(x) > 0:
        return int(x)
    raise argparse.ArgumentTypeError('%s must be positive, non-zero' % x)

def main():
    parser = argparse.ArgumentParser('bwa mem mapping')

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

    # Optional db flags
    parser.add_argument('--db_cred_s3url',
                        required = False
    )
    parser.add_argument('--s3cfg_path',
                        required = False
    )

    
    # Tool flags
    parser.add_argument('-f', '--reference_fasta_path',
                        required = True,
                        help = 'Reference fasta path.'
    )
    parser.add_argument('-1','--fastq1_path',
                        required = True
    )
    parser.add_argument('-2','--fastq2_path',
                        required = True
    )
    parser.add_argument('-r', '--readgroup_json_path',
                        required = True
    )
    parser.add_argument('-j', '--thread_count',
                        required = True,
                        type = is_nat,
                        help = 'Number of threads for execution.',
    )

    args = parser.parse_args()
    uuid = args.uuid
    reference_fasta_path = args.reference_fasta_path
    fastq1_path = args.fastq1_path
    fastq2_path = args.fastq2_path
    readgroup_json_path = args.readgroup_json_path
    thread_count = args.thread_count

    if args.db_cred_s3url:
        db_cred_s3url = args.db_cred_s3url
    else:
        db_cred_s3url = None
    if args.s3cfg_path:
        s3cfg_path = args.s3cfg_path
    
    tool_name = 'bwa_mem'
    logger = pipe_util.setup_logging(tool_name, args, uuid)

    if db_cred_s3url is not None: #db server case
        conn_dict = pipe_util.get_connect_dict(db_cred_s3url, s3cfg_path, logger)
        engine = sqlalchemy.create_engine(sqlalchemy.engine.url.URL(**conn_dict))
    else: # local sqlite case
        sqlite_name = uuid + '.db'
        engine_path = 'sqlite:///' + sqlite_name
        engine = sqlalchemy.create_engine(engine_path, isolation_level='SERIALIZABLE')

    hostname = os.uname()[1]
    logger.info('hostname=%s' % hostname)

    
    bwa_mem.bwa_mem(uuid, fastq1_path, fastq2_path, reference_fasta_path, readgroup_json_path, thread_count, engine, logger)


if __name__ == '__main__':
    main()
