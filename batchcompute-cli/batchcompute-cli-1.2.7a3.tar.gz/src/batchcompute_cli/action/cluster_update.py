
# -*- coding:utf-8 -*-

from ..util import client, result_cache,config
from terminal import confirm,green


def update(clusterId, groupName, nodes, yes=False):
    v = int(nodes)

    if v < 1:
        raise Exception('Invalid nodes, it should be a positive integer')

    if config.isGod():
        clusterId = result_cache.get(clusterId, 'clusters')
        groupName = result_cache.get(groupName, 'groups')

    if yes:
        client.change_cluster_vmcount(clusterId, groupName, nodes)
        print(green('done'))
    else:
        if confirm('Change desiredVMCount of %s.%s?' % (clusterId, groupName), default=False):
            client.change_cluster_vmcount(clusterId, groupName, nodes)
            print(green('done'))
