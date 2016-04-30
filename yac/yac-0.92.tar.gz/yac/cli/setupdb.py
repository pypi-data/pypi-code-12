#!/usr/bin/env python

import os, argparse, getpass
#from slib.db import setup_db
#from slib.name import get_db_name, get_db_user_name, get_stack_name
#from slib.stack import get_rds_db_endpoint


def main():
	
	parser = argparse.ArgumentParser('Setup the DB for a new stack')
	# required args
	parser.add_argument('app',  help='the app name')
	parser.add_argument('env',  help='the env', choices=['dev', 'stage', 'prod', 'archive'])
	parser.add_argument('-x','--suffix',  help='app suffix, to support multiple instances of the same app in the same env')

	# pull out args
	args = parser.parse_args()