#!/usr/bin/env python

from docker import Client
import docker, os, json
from api import get_docker_client

def build_image(
            image_tag,
            sources_path,
            connection_str = "",
            rm = "false"):

    print 'Getting docker client for connection_str=%s' % (connection_str)

    docker_client = get_docker_client( connection_str )

    # build the image
    for line in docker_client.build(tag=image_tag,
                                    path=sources_path,
                                    rm=rm):

        line_json = json.loads(line)

        if 'stream' in line_json:
            print line_json['stream']
        else:
            print line_json

def get_image_name(image, version):

    return "%s:%s"%(image,version)



