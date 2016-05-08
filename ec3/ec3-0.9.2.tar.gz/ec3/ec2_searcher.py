#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import boto3
from ec3 import compat


def make_tag_filters(tag_dict):
    filters = []
    for tag_name, tag_vals in compat.iteritems(tag_dict):
        if not isinstance(tag_vals, list):
            if isinstance(tag_vals, tuple):
                tag_vals = list(tag_vals)
            else:
                tag_vals = [tag_vals]
        filters.append({
            'Name': 'tag:%s' % tag_name,
            'Values': tag_vals
        })
    return filters


class EC2Searcher(object):
    @property
    def ec2_conn(self):
        if not hasattr(self, '_ec2_conn'):
            self._ec2_conn = boto3.resource('ec2')
        return self._ec2_conn

    def search(self, tags=None, only_running=True, vpc_scopes=None):
        filters = make_tag_filters(tags or {})
        if only_running:
            filters.append({
                'Name': 'instance-state-name',
                'Values': ['running']
            })
        vpc_scopes = list(filter(None, vpc_scopes or []))
        if vpc_scopes:
            filters.append({
                'Name': 'vpc-id',
                'Values': vpc_scopes
            })
        return self.ec2_conn.instances.filter(Filters=filters).all()
