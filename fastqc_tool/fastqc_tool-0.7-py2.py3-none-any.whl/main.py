#!/usr/bin/env python3

import argparse
import logging
import sys

from cdis_pipe_utils import pipe_util

import fastqc

def main():
    parser = argparse.ArgumentParser('FastQC tool')

    # Logging flags.
    parser.add_argument('-d', '--debug',
        action = 'store_const',
        const = logging.DEBUG,
        dest = 'level',
        help = 'Enable debug logging.',
    )
    parser.set_defaults(level = logging.INFO)
    
    # Required flags.
    parser.add_argument('-f', '--fastq_path',
                        required=True
    )
    parser.add_argument('-u', '--uuid',
                        required=True
    )
    parser.add_argument('--db_cred_s3url',
                        required=False
    )
    parser.add_argument('--s3cfg_path',
                        required=False
    )

    # setup required parameters
    args = parser.parse_args()
    uuid = args.uuid
    fastq_path = args.fastq_path

    if args.db_cred_s3url:
        db_cred_s3url = args.db_cred_s3url
    else:
        db_cred_s3url = None
    if args.s3cfg_path:
        s3cfg_path = args.s3cfg_path

    
    tool_name = 'fastqc'
    logger = pipe_util.setup_logging(tool_name, args, uuid)

    if db_cred_s3url is not None: #db server case
        conn_dict = pipe_util.get_connect_dict(db_cred_s3url, s3cfg_path, logger)
        engine = sqlalchemy.create_engine(sqlalchemy.engine.url.URL(**conn_dict))
    else: # local sqlite case
        sqlite_name = uuid + '.db'
        engine_path = 'sqlite:///' + sqlite_name
        engine = sqlalchemy.create_engine(engine_path, isolation_level='SERIALIZABLE')

    fastqc.fastqc(uuid, fastq_path, engine, logger)
    
    return


if __name__ == '__main__':
    main()
