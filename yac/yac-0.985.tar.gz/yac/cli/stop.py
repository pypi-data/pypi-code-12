#!/usr/bin/env python

import argparse
from docker import Client
from yac.lib.container.api import get_docker_client, get_connection_str, find_container_by_name
from yac.lib.hosts import get_host

def main():
	
	parser = argparse.ArgumentParser(description='Stop one of the containers')

	# required args
	parser.add_argument('env',   help='the environment to be targeted', choices=['dev', 'stage', 'prod'])            
	parser.add_argument('type',  help='the host type to be targeted', choices=['rw', 'ro']) 
	parser.add_argument('alias', help='name (alias) of container to load', choices=container_aliases)

	# pull out args
	args = parser.parse_args()
	env = args.env
	host_type = args.type
	which_container = args.alias

	# get the ip of the targeted host
	target_host_ip = get_host(env, host_type, 'app')

	# get the ip address of the target host
	# the is currently only one sinstance per tack
	target_host_ip = get_ec2_ip( stack_name )[0]

	# get connection string for the docker remote api on the target host
	docker_api_conn_str = get_connection_str( target_host_ip )

	docker_client = get_docker_client( docker_api_conn_str )

	# find container
	container = find_container_by_name( args.alias, docker_api_conn_str )

	# stop the container
	# Provide a long timeout (30s) to give container time to gracefully shut itself down
	# After timeout expires, docker will sent SIGKILL which could interrupt an app's
	# shutdown sequence and could result in data integrity issues (e.g. the confluence
	# container writes data to its DB during shutdown. Interruping this process can result
	# in plugin data integrity issues, and can even prevent access to the UPM UI.)
	print docker_client.stop(container=container.get('Id'),
	                         timeout=60)
