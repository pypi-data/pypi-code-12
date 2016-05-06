#!/usr/bin/env python

import argparse
import json
import logging
import os
import sys

import pysam
import sqlalchemy

from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import df_util
from cdis_pipe_utils import time_util

def check_readgroup(readgroup_dict, logger):
    if not 'CN' in readgroup_dict:
        logger.debug('"CN" is missing from readgroup: %s' % readgroup_dict)
        sys.exit(1)
    if not 'ID' in readgroup_dict:
        logger.debug('"ID" is missing from readgroup: %s' % readgroup_dict)
        sys.exit(1)
    if not 'LB' in readgroup_dict:
        logger.debug('"LB" is missing from readgroup: %s' % readgroup_dict)
        sys.exit(1)
    if not 'PL' in readgroup_dict:
        logger.debug('"PL" is missing from readgroup: %s' % readgroup_dict)
        sys.exit(1)
    if not 'PU' in readgroup_dict:
        logger.debug('"PU" is missing from readgroup: %s' % readgroup_dict)
        sys.exit(1)
    if not 'SM' in readgroup_dict:
        logger.debug('"SM" is missing from readgroup: %s' % readgroup_dict)
        sys.exit(1)
    # if not 'DT' in readgroup_dict
    return

def extract_readgroup_json(bam_path, engine, logger):
    step_dir = os.getcwd()
    bam_file = os.path.basename(bam_path)
    bam_name, bam_ext = os.path.splitext(bam_file)
    if pipe_util.already_step(step_dir, bam_name + 'json_extract', logger):
        logger.info('already written readgroup json: %s' % bam_name)
    else:
        samfile = pysam.AlignmentFile(bam_path, 'rb')
        samfile_header = samfile.header
        readgroup_dict_list = samfile_header['RG']
        if len(readgroup_dict_list) < 1:
            logger.debug('There are no readgroups in BAM: %s' % bam_name)
            logger.debug('\treadgroup: %s' % readgroup_dict_list)
            sys.exit(1)
        else:
            for readgroup_dict in readgroup_dict_list:
                logger.info('readgroup_dict=%s' % readgroup_dict)
                check_readgroup(readgroup_dict, logger)
                readgroup_json_file = readgroup_dict['ID'] + '.json'
                logger.info('readgroup_json_file=%s\n' % readgroup_json_file)
                with open(readgroup_json_file, 'w') as f:
                    json.dump(readgroup_dict, f, ensure_ascii=False)
            pipe_util.create_already_step(step_dir, bam_name + 'json_extract', logger)
    return

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
    parser.add_argument('-b', '--bam_path',
                        required = True,
                        help = 'BAM file.'
    )

    args = parser.parse_args()
    uuid = args.uuid
    bam_path = args.bam_path

    if args.db_cred_s3url:
        db_cred_s3url = args.db_cred_s3url
    else:
        db_cred_s3url = None
    if args.s3cfg_path:
        s3cfg_path = args.s3cfg_path
    
    tool_name = 'bam_readgroup_to_json'
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

    extract_readgroup_json(bam_path, engine, logger)


if __name__ == '__main__':
    main()
