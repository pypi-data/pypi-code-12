from collections import OrderedDict

from django.conf import settings as django_settings
from django.core import exceptions
from .shard import Shard
from . import utils


class ShardingFactory:
    def __init__(self):
        self.primary = django_settings.DATABASES.get('default')

    def configure(self):
        shards = dict()
        nodes = django_settings.DJANGO_AUTOSHARD.NODES
        for node in nodes:
            try:
                _ = node['HOST']
            except KeyError:
                raise exceptions.ImproperlyConfigured('Node {} does not have a host.'.format(node))
            try:
                _ = node['RANGE']
            except KeyError:
                raise exceptions.ImproperlyConfigured('Node {} does not specify a shard range.'.format(node))

            node_shards = self.set_logical_shards(node)
            shards.update(node_shards)

        django_settings.SHARDS = OrderedDict(sorted(shards.items()))
        django_settings.DATABASE_ROUTERS = ('django_autoshard.routers.ShardRouter', )

    def set_logical_shards(self, node):
        result = dict()
        for i in node['RANGE']:
            shard = self.primary.copy()
            shard['HOST'] = node['HOST']
            shard['NAME'] = '{}_{}'.format(self.primary['NAME'], i)
            alias = 'shard_{}'.format(i)
            django_settings.DATABASES[alias] = shard
            node_index = utils.get_shard_index(alias)
            replicas = self.set_replicas()
            result[node_index] = Shard(node_index, alias, replicas)
        return result

    def set_replicas(self):
        return {}
