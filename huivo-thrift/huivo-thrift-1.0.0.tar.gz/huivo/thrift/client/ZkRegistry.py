import zookeeper

__author__ = 'sunquan'


def watch_method(func):
    def decorated(handle, atype, state, path):
        return func()
    return decorated

class ZkRegistry(object):
    def __init__(self, zk_address, connection_watcher):
        self.zk_address = zk_address
        self.zk_handler = zookeeper.init(zk_address, connection_watcher, 1000)

    def get_children(self, path, watcher = None):
        _list = zookeeper.get_children(self.zk_handler, path, watcher)
        return _list

