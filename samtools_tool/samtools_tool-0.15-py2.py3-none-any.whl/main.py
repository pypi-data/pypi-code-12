#!/usr/bin/env python

import argparse
import logging
import sys

import sqlalchemy

from cdis_pipe_utils import pipe_util

#import tools.samtools_bedcov as samtools_bedcov
#import tools.samtools_depth as samtools_depth
import tools.samtools_flagstat as samtools_flagstat
import tools.samtools_idxstats as samtools_idxstats
import tools.samtools_stats as samtools_stats

def main():
    parser = argparse.ArgumentParser('samtools docker tool')

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
                        help = 'picard tool'
    )
    parser.add_argument('--uuid',
                        required = True,
                        help = 'uuid string',
    )
    parser.add_argument('--input_state',
                        required = True
    )

    # Tool flags
    parser.add_argument('--bam_path',
                        required = False,
                        help = 'input bam path'
    )
    parser.add_argument('--reference_fasta_path',
                        required = False
    )
    parser.add_argument('--bed_path',
                        required = False
    )

    # setup required parameters
    args = parser.parse_args()
    tool_name = args.tool_name
    uuid = args.uuid
    input_state = args.input_state

    logger = pipe_util.setup_logging('samtools_' + tool_name, args, uuid)

    sqlite_name = uuid + '.db'
    engine_path = 'sqlite:///' + sqlite_name
    engine = sqlalchemy.create_engine(engine_path, isolation_level='SERIALIZABLE')

    if tool_name == 'flagstat':
        bam_path = pipe_util.get_param(args, 'bam_path')
        samtools_flagstat.samtools_flagstat(uuid, bam_path, input_state, engine, logger)
    elif tool_name == 'idxstats':
        bam_path = pipe_util.get_param(args, 'bam_path')
        samtools_idxstats.samtools_idxstats(uuid, bam_path, input_state, engine, logger)
    elif tool_name == 'stats':
        bam_path = pipe_util.get_param(args, 'bam_path')
        samtools_stats.samtools_stats(uuid, bam_path, input_state, engine, logger)
    else:
        sys.exit('No recognized tool was selected')
    return


if __name__ == '__main__':
    main()
