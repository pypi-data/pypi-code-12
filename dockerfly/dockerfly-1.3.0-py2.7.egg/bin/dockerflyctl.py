#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""dockerfly bin tool

Usage:
  dockerflyctl    ps
  dockerflyctl    gen          <config_json>
  dockerflyctl    run          <config_json>
  dockerflyctl    rm           <container_id>
  dockerflyctl    resize       <container_id> <new_size>
  dockerflyctl    getpid       <container_id>
  dockerflyctl    rundaemon    <ip> <port>

Options:
  -h --help             Show this screen.
  --version             Show version.

Example:
    show all containers             dockerflyctl    ps
    generate container config       dockerflyctl    gen       centos6.json
    start container                 dockerflyctl    run       centos6.json
    remove container                dockerflyctl    rm        e5d898c10bff
    resize container                dockerflyctl    resize    e5d898c10bff 20480
    getpid container pid            dockerflyctl    getpid    e5d898c10bff
    run daemon server               dockerflyctl    rundaemon 0.0.0.0 5123
"""

import json
from sh import docker, nsenter
from docopt import docopt
import docker as dockerpy

import include
from dockerfly.settings import dockerfly_version
from dockerfly.dockerlib.container import Container
from dockerfly.bin.dockerflyd import rundaemon

def main():
    arguments = docopt(__doc__, version=dockerfly_version)
    docker_cli = dockerpy.Client(base_url='unix://var/run/docker.sock')

    container_json_exp = [{
            'image_name': 'centos:centos6',
            'run_cmd': '/bin/sleep 300',
            'eths':
            [
               ('testDockerflyv0', 'eth0', '192.168.159.10/24'),
               ('testDockerflyv1', 'eth0', '192.168.159.11/24'),
            ],
            'gateway': '192.168.159.2',
            'container_name': None,
            'status': 'stopped',
            'last_modify_time': 0,
            'id': 0,
            'pid': 0,
        }]

    if arguments['ps']:
        print docker('ps')

    if arguments['gen']:
        with open(arguments['<config_json>'], 'w') as config:
            json.dump(container_json_exp, config, indent=4, encoding='utf-8')

    if arguments['run']:
        with open(arguments['<config_json>'], 'r') as config:
            container_json = json.load(config, encoding='utf-8')
            for container in container_json:
                container_id = Container.run(container['image_name'],
                                             container['run_cmd'],
                                             container['eths'],
                                             container['gateway']
                                        )
                print "Container running:ContainerId(%s) Pid(%s)" %(container_id,
                                 docker_cli.inspect_container(container_id)['State']['Pid']
                        )

    if arguments['rm']:
        Container.remove(arguments['<container_id>'])

    if arguments['resize']:
        Container.resize(arguments['<container_id>'], arguments['<new_size>'])

    if arguments['getpid']:
        print docker_cli.inspect_container(arguments['<container_id>'])['State']['Pid']

    if arguments['getpid']:
        print docker_cli.inspect_container(arguments['<container_id>'])['State']['Pid']
        print "run dockerflyd server %s:%s" % (arguments['<ip>'], arguments['<port>'])
        rundaemon(arguments['<ip>'], arguments['<port>'])

if __name__ == '__main__':
    main()
