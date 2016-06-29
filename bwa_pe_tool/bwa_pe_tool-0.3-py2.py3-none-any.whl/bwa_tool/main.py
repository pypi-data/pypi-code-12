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

def check_for_table(engine, logger):
    if 'fastqc_data_Basic_Statistics' in engine.table_names():
        return
    else:
        logger.info('table "fastqc_data_Basic_Statistics" is missing')
        sys.exit(1)

def get_fastqc_measure(fastq_path, fastqc_db_path, measure_value, logger):
    engine_path = 'sqlite:///' + fastqc_db_path
    engine = sqlalchemy.create_engine(engine_path, isolation_level='SERIALIZABLE')
    fastq_name = os.path.basename(fastq_path)
    sql_text = 'select Value from fastqc_data_Basic_Statistics where fastq_name = "' + fastq_name \
               + '" and Measure = "' + measure_value +  '"'
    sql = sqlalchemy.text(sql_text)
    result = engine.execute(sql)
    result_all = result.fetchall()
    if len(result_all) != 1:
        logger('more/less than 1 result: %s' % result_all)
        sys.exit(1)
    else:
        row_value = result_all[0]
        if len(row_value) != 1:
            logger('more/less than 1 result: %s' % row_value)
            sys.exit(1)
        else:
            cell_value = row_value[0]
            if '-' in cell_value:
                str_value = cell_value.split('-')[-1]
                return str_value
            else:
                return cell_value
    return

def main():
    parser = argparse.ArgumentParser('bwa pe mapping')

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
    parser.add_argument('-f', '--fastqc_db_path',
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
    fastqc_db_path = args.fastqc_db_path
    thread_count = args.thread_count
    
    tool_name = 'bwa_pe'
    logger = pipe_util.setup_logging(tool_name, args, uuid)

    sqlite_name = uuid + '.db'
    engine_path = 'sqlite:///' + sqlite_name
    engine = sqlalchemy.create_engine(engine_path, isolation_level='SERIALIZABLE')

    hostname = os.uname()[1]
    logger.info('hostname=%s' % hostname)

    measure_value = 'Sequence length'
    fastq1_readlength = int(get_fastqc_measure(fastq1_path, fastqc_db_path, measure_value, logger))
    logger.info('fastq1_readlength: %s' % fastq1_readlength)
    fastq2_readlength = int(get_fastq_readlength(fastq2_path, fastqc_db_path, measure_value, logger))
    logger.info('fastq2_readlength: %s' % fastq2_readlength)
    fastq_readlength = max(fastq1_readlength, fastq2_readlength)

    measure_value = 'Encoding'
    fastq1_encoding = get_fastqc_measure(fastq1_path, fastqc_db_path, measure_value, logger)
    logger.info('fastq1_encoding: %s' % fastq1_encoding)
    fastq2_encoding = get_fastq_readlength(fastq2_path, fastqc_db_path, measure_value, logger)
    logger.info('fastq2_readlength: %s' % fastq2_encoding)
    if fastq1_encoding != fastq2_encoding:
        logger.info('unequal fastq encoding: %s != %s' % (fastq1_encoding, fastq2_encoding))

    if (fastq_readlength < 70) or (fastq1_encoding == 'Illumina 1.5') or (fastq1_encoding == 'Illumina-1.3'):
        bwa_aln.bwa_aln(uuid, fastq1_path, fastq2_path, fastq1_encoding,reference_fasta_path, readgroup_json_path,
                        thread_count, engine, logger)
    elif (fastq_readlength >= 70) and (fastq_encoding == 'Sanger / Illumina 1.9'):
        bwa_mem.bwa_mem(uuid, fastq1_path, fastq2_path, reference_fasta_path, readgroup_json_path, thread_count, engine, logger)
    else:
        logger.info('unrecognized fastq_encoding: %s' % fastq_encoding)


if __name__ == '__main__':
    main()
