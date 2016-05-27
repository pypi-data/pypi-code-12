# -*- coding: utf-8 -*-
import logging
from kazoo.client import KazooClient

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)-8s %(message)s"
)


class HaDecorator(object):
    ELECTION_PATH = "/ha-zookeeper/election"

    def __init__(self, hosts, path=None):
        self.hosts = hosts
        if not path:
            self.path = self.ELECTION_PATH
        else:
            self.path = path
        self.zk = None

    def __call__(self, f):
        def wrapped(*args, **kwargs):
            self.zk = KazooClient(hosts=self.hosts)
            self.zk.start()
            election = self.zk.Election(self.path)
            election.run(lambda: f(*args, **kwargs))

        return wrapped

    def __del__(self):
        if self.zk != None:
            self.zk.stop()
