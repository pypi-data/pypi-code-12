#!/usr/bin/env python3

import argparse
import logging
import os
import sys
import time

import pandas as pd
import sqlalchemy
from Bio import SeqIO

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util

def store_dup_db(uuid, fastq_name, duplicate_set, engine):
    if len(duplicate_set) >= 1:
        duplicate_list = sorted(list(duplicate_set))
        df = pd.DataFrame({'uuid': [uuid],
                           'fastq_name': fastq_name
        })
        df['qname'] = duplicate_list
        unique_key_dict = {'uuid': uuid, 'fastq_name': fastq_name}
        table_name = 'fastq_duplicate_qname'
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
    else:
        duplicate_list = None
        df = pd.DataFrame({'uuid': [uuid],
                           'fastq_name': fastq_name
        })
        df['qname'] = duplicate_list
        unique_key_dict = {'uuid': uuid, 'fastq_name': fastq_name}
        table_name = 'fastq_duplicate_qname'
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)        
    return

def remove_dups(uuid, infile, outfile, fastq_name, engine, logger):
    aset = set()
    duplicate_set = set()
    readcounter = 0
    duplicatecounter = 0
    for record in SeqIO.parse(infile,'fastq'):
        if record.id in aset:
            duplicate_set.add(record.id)
            duplicatecounter += 1
            logger.info('duplicate: %s' % record.id)
        else:
            readcounter += 1
            aset.add(record.id)
            SeqIO.write(record, outfile, 'fastq')
    logger.info('len(aset)=%s' % len(aset))
    logger.info('readcounter=%s' % str(readcounter))
    logger.info('duplicatecounter=%s' % str(duplicatecounter))
    store_dup_db(uuid, fastq_name, duplicate_set, engine)
    return

def main():
    parser = argparse.ArgumentParser('remove duplicate reads from fastq')

    # Logging flags.
    parser.add_argument('-d', '--debug',
        action = 'store_const',
        const = logging.DEBUG,
        dest = 'level',
        help = 'Enable debug logging.',
    )
    parser.set_defaults(level = logging.INFO)

    parser.add_argument('infile',
                        nargs='?',
                        type=argparse.FileType('r'),
                        default=sys.stdin
    )
    parser.add_argument('outfile',
                        nargs='?',
                        type=argparse.FileType('w'),
                        default=sys.stdout
    )
    parser.add_argument('-u', '--uuid',
                        required = True
    )
    parser.add_argument('-f', '--fastq_name',
                        required = True
    )
    args = parser.parse_args()

    infile = args.infile
    outfile = args.outfile
    uuid = args.uuid
    fastq_name = args.fastq_name

    tool_name = 'remove_duplicate_fastq_matepair_remover'
    logger = pipe_util.setup_logging(tool_name, args, uuid)
    
    hostname = os.uname()[1]
    logger.info('hostname=%s' % hostname)

    sqlite_name = uuid + '.db'
    engine_path = 'sqlite:///' + sqlite_name
    engine = sqlalchemy.create_engine(engine_path, isolation_level='SERIALIZABLE')

    start_time = time.time()
    remove_dups(uuid, infile, outfile, fastq_name, engine, logger)
    end_time = time.time()
    elapsed_time = end_time - start_time

    #store time
    df = time_util.store_seconds(uuid, elapsed_time, logger)
    df['fastq_name'] = fastq_name
    unique_key_dict = {'uuid': uuid, 'fastq_name': fastq_name}
    table_name = 'time_remove_duplicate_fastq_matepair'
    return

if __name__ == '__main__':
    main()
