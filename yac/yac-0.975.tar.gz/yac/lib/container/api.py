#!/usr/bin/env python

from docker import Client

# get connection string for connecting to docker on a remote host
# default port is 5555
def get_connection_str( host, port = 5555):	
    return "http://%s:%s" % ( host, port )

# get docker client
def get_docker_client( connection_str = 'unix://var/run/docker.sock'):
    return Client( version='auto', base_url=connection_str )

# find a container by name
# for some reason this method isn't implemented directly in the docker-py module
def find_container_by_name( container_name, connection_str = 'unix://var/run/docker.sock'):

    # get a client connection
    client = get_docker_client( connection_str )

    # get a list of all containers
    containers = client.containers(all=True)

    # initialize null container (returned if we can't find any that match)
    null_container = {}

    # find the container
    for container in containers:

        # gotcha alert, if server has no containers, container['Names'] can include Names=None,
        # so need to be defensive ...
        if (container and 'Names' in container and container['Names']):

            for this_name in container['Names']:

                if (this_name and container_name in this_name):

                    return container

    return null_container

	