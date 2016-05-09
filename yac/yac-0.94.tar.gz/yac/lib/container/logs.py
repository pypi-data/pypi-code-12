#!/usr/bin/env python

import argparse
from docker import Client
from api import get_docker_client, get_connection_str, find_container_by_name

def get_logs(container_alias, target_host_ip):

	# get connection string for the docker remote api on the target host
	docker_api_conn_str = get_connection_str( target_host_ip )

	docker_client = get_docker_client( docker_api_conn_str )

	# find container
	container = find_container_by_name( container_alias, docker_api_conn_str )

	# get logs from container
	return docker_client.logs(container=container.get('Id'))
