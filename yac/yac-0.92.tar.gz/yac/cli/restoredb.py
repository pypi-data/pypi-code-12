#!/usr/bin/env python

import argparse, sys
#from slib.name import get_stack_name
#from slib.stack import get_rds_db_endpoint
#from slib.db import rename_rds_instance, snapshot_exists, restore_intance_from_snapshot
# from slib.db import restore_security_group, delete_instance

def prompt_for_confirmation(msg):

    sys.stdout.write('\r')                            
    sys.stdout.write( '%s%s%s'%('\033[92m',msg, '\033[0m'))
    sys.stdout.flush() 
    raw_input(" ")

def main():

	parser = argparse.ArgumentParser('Restore a DB from an RDS snapshot')

	# required args
	parser.add_argument('app',  help='the app name')
	parser.add_argument('env',  help='the env', 
	                            choices=['dev', 'stage', 'prod','archive'])
	parser.add_argument('snap', help='the name of the RDS snapshot to restore from')
	parser.add_argument('-x','--suffix',  help='app suffix, to support multiple instances of the same app in the same env')
	parser.add_argument('-s','--skipto',  help='skip to this step number')

	# pull out args
	args = parser.parse_args()