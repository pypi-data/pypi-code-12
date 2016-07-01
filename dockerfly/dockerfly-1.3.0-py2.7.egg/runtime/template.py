#!/bin/env python
# -*- coding: utf-8 -*-

container = {
        "gateway": "192.168.159.1",
        "eths": [
            [
                "testDockerflyv10",
                "eth0",
                "192.168.159.31/24"
            ]
        ],
        "image_name": "172.16.11.13:5000/brain/centos:centos6_sshd",
        "container_name": "dockerfly_1418176930_xxxx",
        "run_cmd": "/usr/sbin/sshd -D",
        'id':3,
        'status':'running',
        'last_modify_time':1418176930.012
    }
