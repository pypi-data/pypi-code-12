#!/usr/bin/env python3

import argparse
import logging
import os
import time

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util

def allow_create_fail(sql_path, logger):
    shell_cmd = "sed -i 's/CREATE TABLE/CREATE TABLE if not exists/g' " + sql_path
    pipe_util.do_shell_command(shell_cmd, logger)
    shell_cmd = "sed -i 's/CREATE INDEX/CREATE INDEX if not exists/g' " + sql_path
    pipe_util.do_shell_command(shell_cmd, logger)
    return

def main():
    parser = argparse.ArgumentParser('merge an arbitrary number of sqlite files')
    # Logging flags.
    parser.add_argument('-d', '--debug',
        action = 'store_const',
        const = logging.DEBUG,
        dest = 'level',
        help = 'Enable debug logging.',
    )
    parser.set_defaults(level = logging.INFO)

    parser.add_argument('-s', '--source_sqlite', action='append', required=True)
    parser.add_argument('-u', '--uuid', required=True)
    args = parser.parse_args()

    source_sqlite_list = args.source_sqlite
    uuid = args.uuid

    tool_name = 'merge_sqlite'
    logger = pipe_util.setup_logging(tool_name, args, uuid)
    engine = pipe_util.setup_db(uuid+'_log')

    step_dir = os.getcwd()
    if pipe_util.already_step(step_dir, uuid + '_db', logger):
        logger.info('already completed step `merge_sqlite`')
    else:
        logger.info('running step `merge_sqlite`')
        for source_sqlite_path in source_sqlite_list:
            logger.info('source_sqlite_path=%s' % source_sqlite_path)
            source_sqlite_name = os.path.splitext(os.path.basename(source_sqlite_path))[0]

            start_time = time.time()
            
            #dump
            source_dump_path = source_sqlite_name + '.sql'
            cmd = ['sqlite3', source_sqlite_path, "\'.dump\'", '>', source_dump_path ]
            shell_cmd = ' '.join(cmd)
            pipe_util.do_shell_command(shell_cmd, logger)


            #alter text create table/index
            allow_create_fail(source_dump_path, logger)
            
            #load
            destination_sqlite_path = uuid + '.db'
            cmd = ['sqlite3', destination_sqlite_path, '<', source_dump_path]
            shell_cmd = ' '.join(cmd)
            pipe_util.do_shell_command(shell_cmd, logger)

            elapsed_time = time.time() - start_time

            #store time
            df = time_util.store_seconds(uuid, elapsed_time, logger)
            table_name = 'time_merge_sqlite'
            unique_key_dict = {'uuid': uuid, 'source_sqlite_name': source_sqlite_name, 'destination_sqlite_name': destination_sqlite_path}
            df['uuid'] = uuid
            df['source_sqlite_name'] = source_sqlite_name
            df['destination_sqlite_name'] = destination_sqlite_path
            df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
            
        pipe_util.create_already_step(step_dir, uuid + '_db', logger)
    return

if __name__ == '__main__':
    main()
