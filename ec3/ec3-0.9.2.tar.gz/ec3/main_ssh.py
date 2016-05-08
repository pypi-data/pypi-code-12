#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import os
import random

from ec3.util import get_tags
from ec3 import exceptions
from ec3.ec2_searcher import EC2Searcher


def main_ssh(conf):
    print(conf)
    searcher = EC2Searcher()
    instances = list(searcher.search(
        tags=conf.tag_filters,
        vpc_scopes=[conf.vpc_scope]
    ))
    for instance in instances:
        name = get_tags(instance).get('Name', 'NO NAME')
        print(name, instance.instance_id, instance.public_dns_name)
    if not instances:
        raise exceptions.NoInstancesFound()
    instance = random.choice(instances)
    args = []
    if conf.key_file_path:
        args.extend(['-i', conf.key_file_path])
    target = "%s@%s" % (conf.remote_user, instance.public_dns_name)
    args.append(target)
    name = 'ec3 : %s' % target
    os.execlp("ssh", name, *args)
