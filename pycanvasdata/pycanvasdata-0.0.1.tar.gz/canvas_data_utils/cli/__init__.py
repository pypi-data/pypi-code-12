#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse, os
from canvas_data_utils import canvas_data_auth
from canvas_data_utils.logger import logger
from pprint import pprint
from sqlalchemy import func

parser = argparse.ArgumentParser(description='CanvasData Utilities')
command_choices = (
    'convert_to_csv', 
    'import',
    'create_tables',
    'reset',
    'sql_create_statement',
    'list_files',
    'download',
    'sample_queries',
    'schema')
parser.add_argument('command', 
                   help='command_to_run', choices=command_choices)
parser.add_argument('--config', dest='config', default=None,
                   help='path to the configuration file')
parser.add_argument('-t', dest='table', default=None,
                   help='specify a specific table')
parser.add_argument('--offline', 
                   help='run in offline mode')


def canvasdata():
  args = parser.parse_args()
  config = find_config(args)
  print('config file: {}'.format( config))
  cdata = canvas_data_auth.CanvasData(config_filename = config, offline=args.offline)
  if args.command == 'convert_to_csv':
    print('Converting *.gz files to CSV')
    csv_filename = cdata.convert_all_to_csv()

  elif args.command == 'create_tables':
    cdata.create_tables()
  elif args.command == 'reset':
    cdata.reset_database()
  elif args.command == 'sql_create_statement':
    print(cdata.table_creation_statement())

  elif args.command == 'import':
    if args.table:
      if args.table != 'requests':
        cdata.import_data(schema_table = args.table)
      else:
        # Requests need to be imported in a special way
        cdata.import_all_requests()
    else:
      cdata.import_data()

  elif args.command == 'schema':
    cdata.print_schema(args.table)

  elif args.command == 'list_files':
    cdata.list_all_files( args.table)

  elif args.command == 'download':
    cdata.download_all_files(args.table)

  elif args.command == 'sample_queries':
    print('Running Sample Queries')
    Account = cdata.get_orm_obj('account')
    #for acct in cdata.session.query(Account).order_by(Account.id):
    #  print('acct.name', acct.name)

    results = cdata.sql_query("SELECT count(*) as num from account where workflow_state!='deleted'")
    table_label = '(raw) Active Accounts'
    print(cdata.query_to_table_str(table_label, results))

    active_accounts = cdata.query(Account).filter(Account.workflow_state!='deleted').count()
    print('(obj) Active Accounts: {}'.format(active_accounts))

    Course = cdata.get_orm_obj('course')
    #courses_by_status = cdata.query(func.count(Course.workflow_state), Course.workflow_state).filter(Course.workflow_state!='deleted').group_by(Course.workflow_state)
    courses_by_status = cdata.query(
        Course.workflow_state,
        func.count(Course.workflow_state)
    ).group_by(Course.workflow_state)

    print(cdata.query_to_table_str('Courses by status', courses_by_status))

    ExternalToolDim = cdata.get_orm_obj('external_tool_activation_dim')

    query = cdata.query(
        #func.count(ExternalToolDim.account_id), 
        ExternalToolDim.id, 
        ExternalToolDim.name, 
        ExternalToolDim.account_id, 
        ExternalToolDim.workflow_state, 
        Account.name, 
        Account.sis_source_id,
        Account.workflow_state 
      ).filter(
          ExternalToolDim.account_id!=None
      ).filter(
          ExternalToolDim.workflow_state!='deleted'
      ).join(
          Account
      ).filter(
          Account.workflow_state!='deleted'
      )#.group_by(ExternalToolDim.account_id)

    print(cdata.query_to_table_str('Active External Tools', query))

    User = cdata.get_orm_obj('user')
    PseudonymDim = cdata.get_orm_obj('pseudonym_dim')
    pseudonyms_by_status = cdata.query(
        PseudonymDim.workflow_state,
        func.count(PseudonymDim.workflow_state)
      ).group_by(PseudonymDim.workflow_state)

    print(cdata.query_to_table_str('Pseudonyms by workflow_state', pseudonyms_by_status))

def find_config(args=None):
  if args and args.config:
    return args.config
  else:
    # Search for config.ini in 
    # - CWD
    config_filename = 'canvasdata_config.ini'
    cwd_config = os.path.join(os.getcwd(),config_filename)
    if os.path.exists(cwd_config):
      return cwd_config
    homedir_config = os.path.join(os.path.expanduser('~'), config_filename)
    if os.path.exists(homedir_config):
      return homedir_config
    # - ~/canvasdata_config.ini
