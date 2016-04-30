#!/usr/bin/env python

from docker import Client
import docker, os, json
from api import get_docker_client, get_connection_str


def remove_image(
            image_tag,
            target_host_ip,
            force_removal = True):

    # get connection string for the docker remote api on the target host
    docker_api_conn_str = get_connection_str( target_host_ip )

    docker_client = get_docker_client( docker_api_conn_str )

    print image_tag + ", " + target_host_ip
    
    # build the image
    print docker_client.remove_image(
                                    image=image_tag,
                                    force=force_removal)