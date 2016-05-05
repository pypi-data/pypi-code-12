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
    import anydbm
except ImportError:
    import dbm as anydbm
try:
    from UserDict import DictMixin
except ImportError:
    from collections import MutableMapping as DictMixin
    
import sys

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
        self.cache={}
    def keys(self):
        return self.dict.keys()
    def has_key(self, key):
        return key in self.dict
    def __getitem__(self, key):
        try:
            value = self.cache[key]
        except KeyError:
            value = self.dict[key]
        return value
    def __setitem__(self, key, value):
        self.cache[key] = value
    def __delitem__(self, key):
        try:
            del self.dict[key]
        except KeyError:
            del self.cache[key]
    def __contains__(self, key):
        return key in self.dict
    def __len__(self):
        return len(self.dict)
    def __iter__(self):
        if sys.version_info >= (3, 0):
            for k,v in self.dict.items():
                yield k,v
        else:
            for k,v in self.dict.iteritems():
                yield k,v
        
class _DB(_Wrapper):
    def __init__(self, filename, flag="c"):
        _Wrapper.__init__(self, anydbm.open(filename, flag))
    def sync(self):
        if sys.version_info >= (3, 0):
            for key, entry in self.cache.items():
                self.dict[key] = entry
        else:
            for key, entry in self.cache.iteritems():
                self.dict[key] = entry
        if hasattr(self.dict, 'save'):
            self.dict.save()
    def close(self):
        self.sync()
        self.dict.close()
        self.dict = _ClosedDict()
        
        
def thing(filename, flag="c"):
    return _DB(filename, flag)
