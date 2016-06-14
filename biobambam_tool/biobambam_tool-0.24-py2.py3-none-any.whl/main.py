#!/usr/bin/env python3

import argparse
import logging
import sys

import sqlalchemy

from cdis_pipe_utils import pipe_util

import tools.bamfixmateinformation as bamfixmateinformation
import tools.bamindex as bamindex
import tools.bammarkduplicates as bammarkduplicates
import tools.bammarkduplicates2 as bammarkduplicates2
import tools.bammdnm as bammdnm
import tools.bammerge as bammerge
#import tools.bamsort as bamsort
import tools.bamtofastq as bamtofastq
import tools.bamvalidate as bamvalidate

def main():
    parser = argparse.ArgumentParser('biobambam docker tool')

    # Logging flags.
    parser.add_argument('-d', '--debug',
        action = 'store_const',
        const = logging.DEBUG,
        dest = 'level',
        help = 'Enable debug logging.',
    )
    parser.set_defaults(level = logging.INFO)
    
    # Required flags.
    parser.add_argument('--tool_name',
                        required = True,
                        help = 'biobambam tool'
    )
    parser.add_argument('--uuid',
                        required = True,
                        help = 'uuid string',
    )
    parser.add_argument('--input_state',
                        required = True
    )

    
    # Optional db flags
    parser.add_argument('--db_cred_s3url',
                        required = False
    )
    parser.add_argument('--s3cfg_path',
                        required = False
    )

    
    # Tool flags
    parser.add_argument('--bam_path',
                        required = False
    )
    parser.add_argument('--reference_fasta_path',
                        required = False
    )

    # setup required parameters
    args = parser.parse_args()
    tool_name = args.tool_name
    uuid = args.uuid
    input_state = args.input_state
    if args.db_cred_s3url:
        db_cred_s3url = args.db_cred_s3url
        s3cfg_path = args.s3cfg_path
    else:
        db_cred_s3url = None

    logger = pipe_util.setup_logging('biobambam2_' + tool_name, args, uuid)

    if db_cred_s3url is not None: #db server case
        conn_dict = pipe_util.get_connect_dict(db_cred_s3url, s3cfg_path, logger)
        engine = sqlalchemy.create_engine(sqlalchemy.engine.url.URL(**conn_dict))
    else: # local sqlite case
        sqlite_name =  tool_name + '_' + uuid +'.db'
        engine_path = 'sqlite:///' + sqlite_name
        engine = sqlalchemy.create_engine(engine_path, isolation_level='SERIALIZABLE')

    be_lenient = True
    
    if tool_name == 'bamfixmateinformation':
        bam_path = pipe_util.get_param(args, 'bam_path')
        bamfixmateinformation.bamfixmateinformation(uuid, bam_path, input_state, cpu_count, engine, logger)
    elif tool_name == 'bamindex':
        bam_path = pipe_util.get_param(args, 'bam_path')
        bamindex.bamindex(uuid, bam_path, input_state, engine, logger)
    elif tool_name == 'bammarkduplicates':
        bam_path = pipe_util.get_param(args, 'bam_path')
        bammarkduplicates.bammarkduplicates(uuid, bam_path, input_state, cpu_count, engine, logger)
    elif tool_name == 'bammarkduplicates2':
        bam_path = pipe_util.get_param(args, 'bam_path')
        bammarkduplicates2.bammarkduplicates2(uuid, bam_path, input_state, cpu_count, engine, logger)
    elif tool_name == 'bammdnm':
        bam_path = pipe_util.get_param(args, 'bam_path')
        reference_fasta_path = pipe_util.get_param(args, 'reference_fasta_path')
        bammdnm.bammdnm(uuid, bam_path, reference_fasta_path, input_state, engine, logger)
    elif tool_name == 'bammerge':
        bam_path = pipe_util.get_param(args, 'bam_path')
        bammerge.bammerge(uuid, bam_path, input_state, cpu_count, engine, logger)
    elif tool_name == 'bamsort':
        bam_path = pipe_util.get_param(args, 'bam_path')
        reference_fasta_path = pipe_util.get_param(args, 'reference_fasta_path')
        bamsort.bamsort(uuid, bam_path, reference_fasta_path, input_state, engine, logger)
    elif tool_name == 'bamtofastq':
        bam_path = pipe_util.get_param(args, 'bam_path')
        bamtofastq.bamtofastq(uuid, bam_path, input_state, engine, logger)
    elif tool_name == 'bamvalidate':
        bam_path = pipe_util.get_param(args, 'bam_path')
        bamvalidate.bamvalidate(uuid, bam_path, input_state, cpu_count, engine, logger)
    else:
        sys.exit('No recognized tool was selected')
        
    return


if __name__ == '__main__':
    main()
