#!/bin/env python
# -*- coding: utf-8 -*-

import os
import sh
import time
import glob
import traceback
import docker as dockerpy
from datetime import datetime
from docker.utils import create_host_config

from dockerfly.dockernet.veth import MacvlanEth
from dockerfly.dockerlib.libs import run_in_process
from dockerfly.errors import ContainerActionError
from dockerfly.logger import getLogger

logger = getLogger()

class Container(object):

    docker_cli = dockerpy.Client(base_url='unix://var/run/docker.sock', timeout=300)

    @classmethod
    @run_in_process
    def run(cls, image_name, run_cmd, veths, gateway):
        """create basic container, then running

        Args:
            image_name: docker image name
            veths: virtual eths, [('em0v0', 'em0', '192.168.159.10/24'),
                                  ('em1v1', 'em1', '192.168.159.11/24')... )],

                   !!!notify!!!:
                   the first eth will be assigned to the default gateway for container
        Return:
            container_id
        """
        try:
            container_id = cls.create(image_name, run_cmd)
            cls.start(container_id, veths, gateway)
        except dockerpy.errors.APIError as e:
            logger.error(traceback.format_exc())
            raise ContainerActionError(str(e))

        return container_id

    @classmethod
    def create(cls, image_name, run_cmd, container_name=None):
        """create continer"""
        if not container_name:
            container_name = "dockerfly_%s_%s" % (image_name.replace(':','_').replace('/','_'),
                                              datetime.fromtimestamp(int(time.time())).strftime('%Y%m%d%H%M%S'))
        try:
            container = cls.docker_cli.create_container(image=image_name,
                                                    command=run_cmd,
                                                    name=container_name)
        except dockerpy.errors.APIError as e:
            logger.error(traceback.format_exc())
            raise ContainerActionError(str(e))

        return container.get('Id')

    @classmethod
    def start(cls, container_id, veths, gateway):
        """start eths and continer"""
        try:
            cls.docker_cli.start(container=container_id,
                                 #extra_hosts={'ldap.xxx.com.cn':'172.16.11.3'},
                                 privileged=True)
        except dockerpy.errors.APIError as e:
            logger.error(traceback.format_exc())
            raise ContainerActionError(str(e))

        for index, (veth, link_to, ip_netmask) in enumerate(veths):
            macvlan_eth = MacvlanEth(veth, ip_netmask, link_to).create()
            if index == 0:
                macvlan_eth.attach_to_container(container_id,
                                                is_route=True, gateway=gateway)
            else:
                macvlan_eth.attach_to_container(container_id)

    @classmethod
    def stop(cls, container_id):
        """stop continer"""
        try:
            cls.docker_cli.stop(container_id)
        except dockerpy.errors.APIError as e:
            logger.error(traceback.format_exc())
            raise ContainerActionError(str(e))

    @classmethod
    def remove(cls, container_id):
        """remove eths and continer"""
        try:
            cls.docker_cli.stop(container_id)
            cls.docker_cli.remove_container(container_id)
        except dockerpy.errors.APIError as e:
            logger.error(traceback.format_exc())
            raise ContainerActionError(str(e))

    @classmethod
    def resize(cls, container_id, new_size=10240):
        """resize container disk space, only support devicemapper storage backend

        args:
            new_size: 1024Mb
        """
        dev_path = glob.glob("/dev/mapper/docker-*-*-%s*" % container_id)
        if dev_path:
            dev = os.path.basename(dev_path[0])
        else:
            return

        #load
        table = sh.dmsetup('table', dev).split()
        table[1] = str(int(new_size)*1024*1024/512)
        sh.dmsetup((sh.echo(' '.join(table))), 'load', dev)
        sh.dmsetup('resume', dev)
        sh.resize2fs(dev_path[0])

    @classmethod
    def get_pid(cls, container_id):
        try:
            pid = cls.docker_cli.inspect_container(container_id)['State']['Pid']
        except dockerpy.errors.APIError as e:
            logger.error(traceback.format_exc())
            raise ContainerActionError(str(e))
        return pid

