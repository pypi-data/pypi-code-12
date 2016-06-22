#!/usr/bin/env python

import argparse
import datetime
import logging
import os
import time

import sqlalchemy
import pandas as pd

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util
from cdis_pipe_utils import postgres

def main():
    parser = argparse.ArgumentParser('update status of job')
    # Logging flags.
    parser.add_argument('-d', '--debug',
        action = 'store_const',
        const = logging.DEBUG,
        dest = 'level',
        help = 'Enable debug logging.',
    )
    parser.set_defaults(level = logging.INFO)

    parser.add_argument('--case_id',
                        required=True
    )
    parser.add_argument('--gdc_id',
                        required=True
    )
    parser.add_argument('--repo',
                        required = True
    )
    parser.add_argument('--repo_hash',
                        required = True
    )
    parser.add_argument('--s3_url',
                        required = False
    )
    parser.add_argument('--status',
                        required = True
    )
    parser.add_argument('--table_name',
                        required=True
    )

    args = parser.parse_args()

    case_id = args.case_id
    gdc_id = args.gdc_id
    repo = args.repo
    repo_hash = args.repo_hash
    status = args.status
    table_name = args.table_name

    tool_name = 'queue_status'
    logger = pipe_util.setup_logging(tool_name, args, gdc_id)

    sqlite_name = case_id + '.db'
    engine_path = 'sqlite:///' + sqlite_name
    engine = sqlalchemy.create_engine(engine_path, isolation_level='SERIALIZABLE')

    status_dict = dict()
    status_dict['case_id'] = case_id
    status_dict['gdc_id'] = [gdc_id]
    status_dict['repo'] = repo
    status_dict['repo_hash'] = repo_hash
    status_dict['status'] = status
    if s3_url is not None:
        status_dict['s3_url'] = s3_url
    else:
        status_dict['s3_url'] = None

    time_seconds = time.time()
    datetime_now = str(datetime.datetime.now())

    status_dict['time_seconds'] = time_seconds
    status_dict['datetime_now'] = datetime_now
    logger.info('writing status_dict=%s' % str(status_dict))
    df = pd.DataFrame(status_dict)

    unique_key_dict = {'case_id': case_id, 'gdc_id': gdc_id, 'repo_hash': repo_hash, 'status': status }
    df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)

    return

if __name__ == '__main__':
    main()
