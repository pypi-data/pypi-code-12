#!/bin/env python
# -*- coding: utf-8 -*-

import socket
from .database import update_db, get_db
from dockerfly.errors import VEthStatusException

db_name = 'containers.json'

def get_all_status():
    return get_db(db_name)

def get_status(container_id):
    for container in get_all_status():
        if container_id == container.get('id', None):
            return container
    raise LookupError("The container doesn't exist in dockerfly")

def verify_ips(eth_ip):
    try:
        socket.inet_aton(eth_ip.split('/')[0])
    except socket.error as e:
        raise VEthStatusException("invalid ip address:{}, {}".format(eth_ip, e.message))

    all_eths_status = []
    for container in get_all_status():
        all_eths_status.extend(container['eths'])

    all_eth_ips = [name[2] for name in all_eths_status]

    if eth_ip in all_eth_ips and '0.0.0.0' not in eth_ip:
        raise VEthStatusException("eth ip has already existed")

def update_status(containers, key='id'):
    curr_containers = get_all_status()
    updating_containers = containers
    new_containers = []

    for curr_container in curr_containers:
        for updating_container in updating_containers:
            if updating_container.get(key, None) and curr_container.get(key, None) \
               and updating_container[key] == curr_container[key]:
                for k,v in updating_container.items():
                    curr_container[k] = v
        new_containers.append(curr_container)

    update_db(new_containers, db_name)

def add_status(containers):
    curr_containers = get_all_status()
    curr_containers.extend(containers)

    update_db(curr_containers, db_name)

def remove_status(container_ids, key='id'):
    curr_containers = get_all_status()
    new_containers = []
    for index, container in enumerate(curr_containers):
        if container.get(key, None) not in container_ids:
            new_containers.append(container)

    update_db(new_containers, db_name)

def get_status_db():
    return db_name
