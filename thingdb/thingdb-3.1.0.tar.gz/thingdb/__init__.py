#
#
#           .        .--.   _..._
#         .'|        |__| .'     '.   .--./)
#     .| <  |        .--..   .-.   . /.''\\
#   .' |_ | |        |  ||  '   '  || |  | |
# .'     || | .'''-. |  ||  |   |  | \`-' /
#'--.  .-'| |/.'''. \|  ||  |   |  | /("'`
#   |  |  |  /    | ||  ||  |   |  | \ '---.
#   |  |  | |     | ||__||  |   |  |  /'""'.\
#   |  '.'| |     | |    |  |   |  | ||     ||
#   |   / | '.    | '.   |  |   |  | \'. __//
#   `'-'  '---'   '---'  '--'   '--'  `'---'
#"thing" database - github/itslukej
try:
    from UserDict import DictMixin
except ImportError:
    from collections import MutableMapping as DictMixin
try:
    import cPickle as pickle
except ImportError:
    import pickle
import os

class _ClosedDict(DictMixin):
    """Returns ValueError when trying to get/set/del item"""

    def closed(self, *args):
        raise ValueError('invalid operation on closed thing')
    __len__ = __getitem__ = __setitem__ = __delitem__ = __iter__ = keys = closed

    def __repr__(self):
        return '<Closed Dictionary>'

class _Wrapper(DictMixin):
    """Main wrapper for thingdb"""
    def __init__(self, dict):
        self.dict = dict
    def keys(self):
        return self.dict.keys()
    def has_key(self, key):
        return key in self.dict
    def __getitem__(self, key):
        return self.dict[key]
    def __setitem__(self, key, value):
        self.dict[key] = value
    def __delitem__(self, key):
        del self.dict[key]
    def __contains__(self, key):
        return key in self.dict
    def __len__(self):
        return len(self.dict)
    def __iter__(self):
        for k in self.dict.keys():
            return k,self.dict[k]
    def __repr__(self):
        return str(self.dict)
    
class _DB(_Wrapper):
    def __init__(self, filename, flag="c"):
        if not os.path.isfile(filename):
            pickle.dump({}, open(filename, "wb+"))
        database = pickle.load(open(filename, "rb"))
        self.filename=filename
        self.flags = flag
        _Wrapper.__init__(self, database)
    def sync(self):
        pickle.dump(self.dict, open(self.filename, "wb"))
    def close(self):
        pickle.dump(self.dict, open(self.filename, "wb"))
        self.dict = _ClosedDict()
    def __repr__(self):
        return "thingDB({0})".format(self.filename)
        
        
def thing(filename, flag="c"):
    return _DB(filename, flag)
