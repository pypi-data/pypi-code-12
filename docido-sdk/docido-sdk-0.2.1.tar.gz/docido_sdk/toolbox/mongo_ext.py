from threading import RLock

from pymongo import MongoClient


__all__ = [
    'MongoClientPool',
]


class MongoClientPool(object):
    lock = RLock()
    connections = dict()

    @classmethod
    def get(cls, **kwargs):
        key = hash(frozenset(kwargs.items()))
        with cls.lock:
            con = cls.connections.get(key)
            if con is None:
                con = MongoClient(**kwargs)
                cls.connections[key] = con
        return con
