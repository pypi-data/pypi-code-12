#!/usr/bin/env python

import argparse
import json
import logging
import sys

import pandas as pd
import sqlalchemy

from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import df_util


def readgroup_to_db(json_data, uuid, engine, logger):
    for rg_key in sorted(json_data.keys()):
        rg_dict = dict()
        rg_dict['uuid'] = [uuid]
        rg_dict['ID'] = json_data['ID']
        rg_dict['key'] = rg_key
        rg_dict['value'] = json_data[rg_key]
        df = pd.DataFrame(rg_dict)
        unique_key_dict = {'uuid': uuid, 'ID': json_data['ID'], 'key': rg_key}
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
    return

def main():
    parser = argparse.ArgumentParser('readgroup json db insertion')

    # Logging flags.
    parser.add_argument('-d', '--debug',
        action = 'store_const',
        const = logging.DEBUG,
        dest = 'level',
        help = 'Enable debug logging.',
    )
    parser.set_defaults(level = logging.INFO)
    
    # Required flags.
    parser.add_argument('--json_path',
                        required = True,
                        help = 'readgroup json path'
    )
    parser.add_argument('--uuid',
                        required = True,
                        help = 'uuid string',
    )

    # optional flags
    parser.add_argument('--db_cred_s3url',
                        required = False
    )
    parser.add_argument('--s3cfg_path',
                        required = False
    )

    
    # setup required parameters
    args = parser.parse_args()
    tool_name = 'readgroup_json_db'
    uuid = args.uuid
    json_path = args.json_path

    if args.db_cred_s3url:
        db_cred_s3url = args.db_cred_s3url
    else:
        db_cred_s3url = None
    if args.s3cfg_path:
        s3cfg_path = args.s3cfg_path

    logger = pipe_util.setup_logging(tool_name, args, uuid)

    if db_cred_s3url is not None: #db server case
        conn_dict = pipe_util.get_connect_dict(db_cred_s3url, s3cfg_path, logger)
        engine = sqlalchemy.create_engine(sqlalchemy.engine.url.URL(**conn_dict))
    else: # local sqlite case
        sqlite_name = uuid + '.db'
        engine_path = 'sqlite:///' + sqlite_name
        engine = sqlalchemy.create_engine(engine_path, isolation_level='SERIALIZABLE')

    with open(json_path, 'r') as json_open:
        json_data = json.load(json_open)
    readgroup_to_db(json_data, uuid, engine, logger)
        
    return


if __name__ == '__main__':
    main()
