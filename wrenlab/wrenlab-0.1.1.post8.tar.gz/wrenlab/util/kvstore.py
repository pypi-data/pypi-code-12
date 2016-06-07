import os
import os.path
import shelve

class KVStore(shelve.DbfilenameShelf):
    """
    NOTE: keys are coerced to strings, so iterating through keys() or items()
    will be messed up.

    Values can be arbitrary objects.
    """

    def __init__(self, name, writeback=False):
        path = KVStore._path(name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        flag = "c" if writeback else "r"
        super(KVStore, self).__init__(path, flag=flag, writeback=writeback)

    @staticmethod
    def _path(name):
        return os.path.expanduser("~/.cache/wrenlab/kvstore/{}.bdb".format(name))

    @staticmethod
    def exists(name):
        return os.path.exists(KVStore._path(name))

    def __getitem__(self, key):
        return super(KVStore, self).__getitem__(str(key))

    def __setitem__(self, key, value):
        super(KVStore, self).__setitem__(str(key), value)


