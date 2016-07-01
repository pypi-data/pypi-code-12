#!/bin/env python
# -*- coding: utf-8 -*-

from multiprocessing.pool import ThreadPool
import docker as dockerpy

docker_cli = dockerpy.Client(base_url='unix://var/run/docker.sock')

def run_in_process(fn):
    def run(*k):
        pool = ThreadPool(processes=1)
        async_result = pool.apply_async(fn, k)
        return async_result.get()
    return run


def get_all_containers():
    """ list containers, idenical `docker ps` command

    Return:
        [{'Command': '/bin/sleep 30',
          'Created': 1412574844,
          'Id': '6e276c9e6e5759e12a6a9214efec6439f80b4f37618e1a6547f28a3da34db07a',
          'Image': 'busybox:buildroot-2014.02',
          'Names': ['/grave_mayer'],
          'Ports': [],
          'Status': 'Up 1 seconds'}]
    """
    return docker_cli.containers()

def get_all_containers_id():
    return [item['Id'] for item in get_all_containers()]

