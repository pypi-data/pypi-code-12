#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals


thunk = lambda func, *args, **kwargs: func(*args, **kwargs)
partial = lambda func, arg: lambda *args, **kwargs: func(arg, *args, **kwargs)
openable = partial(thunk, open)


import pickle
import boto3
from collections import namedtuple


class Loadable(object):
    @classmethod
    def load(cls, filename):
        with open(filename) as f:
            data = pickle.load(f)
        return cls.from_dict(data)

    def to_dict(self):
        raise NotImplementedError()

    @classmethod
    def from_dict(cls, data):
        raise NotImplementedError()

    def save(self, file_name):
        data = self.to_dict()
        if isinstance(file_name, basestring):
            with open(file_name, 'w') as f:
                pickle.dump(data, f, 2)
        else:
            # passed something file-like
            file_name.write(pickle.dumps(data, 2))



def mkfilter(name, *vals):
    return {
        'Name': name,
        'Values': list(vals)
    }


Tag = namedtuple('Tag', ['key', 'value'])
VPC = namedtuple('VPC', ['id', 'name'])


class BotoCache(Loadable):
    def __init__(self, tag_pairs, vpcs, created_time, cache_dir):
        self._tag_pairs = tag_pairs
        self._vpcs = vpcs
        self._created_time = created_time
        self._cache_dir = cache_dir

    def to_dict(self):
        return {
            'tag_pairs': self._tag_pairs,
            'vpcs': self._vpcs
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def list_tags(self):
        return [
            tuple(pair) for pair in self._tag_pairs
        ]

    @classmethod
    def _initialize(cls, cache_dir):
        conn = boto3.client('ec2')
        filters = []
        filters.append(mkfilter(
            'resource-type', 'instance', 'vpc'
        ))
        vpcs = []
        instance_tags = []
        for tag in conn.describe_tags(Filters=filters)['Tags']:
            if tag['ResourceType'] == 'instance':
                instance_tags.append(Tag(key=tag['Key'], value=tag['Value']))
            else:
                assert tag['ResourceType'] == 'vpc'
                if tag['Key'] == 'Name':
                    vpcs.append(VPC(id=tag['ResourceId'], name=tag['Value']))
        return cls(tag_pairs=instance_tags, vpcs=vpcs, cache_dir=cache_dir)


