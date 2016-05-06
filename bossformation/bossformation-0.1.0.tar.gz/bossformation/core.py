# Copyright 2016 Joseph Wright <rjosephwright@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from __future__ import print_function
import base64
import functools as f
import itertools
import json
import os
import random
import re
import shutil
import socket
import string
import subprocess
import sys
import threading as t
import time
import tempfile
import yaml
import Queue

import boto3 as boto
import jinja2 as j


def cached(func):
    cache = {}

    @f.wraps(func)
    def wrapper(*args, **kwargs):
        key = func.__name__ + str(sorted(args)) + str(sorted(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return wrapper

@cached
def aws_connect(service, kind='resource'):
    assert(kind in ('client', 'resource'))
    session = boto.Session()
    connection = getattr(session, kind)
    return connection(service)

def azs():
    ec2  = aws_connect('ec2', 'client')
    return [z['ZoneName'] for z in ec2.describe_availability_zones()['AvailabilityZones']
            if z['State'] == 'available']

def resource_id_for(service, name, prefix, flt):
    if name.startswith(prefix): return name
    item = list(service.filter(Filters=[flt]))
    if item: return item[0].id

def ami_id_for(name):
    ec2 = aws_connect('ec2')
    return resource_id_for(
        ec2.images, name, 'ami-',
        { 'Name': 'name', 'Values': [name] }
    )

def sg_id_for(name):
    ec2 = aws_connect('ec2')
    return resource_id_for(
        ec2.security_groups, name, 'sg-',
        { 'Name': 'group-name', 'Values': [name] }
    )

def subnet_id_for(name):
    ec2 = aws_connect('ec2')
    return resource_id_for(
        ec2.subnets, name, 'subnet-',
        { 'Name': 'tag:Name', 'Values': [name] }
    )

def expand_properties(path):
    e = j.Environment(loader=j.FileSystemLoader('.'))
    e.globals.update(dict(
        azs = azs,
        ami_id_for = ami_id_for,
        sg_id_for = sg_id_for,
        subnet_id_for = subnet_id_for,
    ))
    t = e.get_template(path)
    return yaml.load(t.render())

def expand_template(template, properties, loader):
    e = j.Environment(loader=loader)
    e.globals.update(properties)
    t = e.get_template(template)
    return yaml.load(t.render())
