# definition of a dict-replacement class that allows dot-notation attribute access

class Dict(dict):
    """A dict class that:
        * allows dot-notation attribute access, returning None if key not found
        * sorts keys on calls to keys() and items() and repr(), making many things easier
        * therefore requires that all keys need to be a sortable collection -- 
            for example only use string keys.
        * allows calling itself with parameters, which creates a new Dict based on 
            this one without modifying it. (immutability)
    Usage:
    >>> d = Dict(c=3, b=2, a=1)                     # initialize with parameters or **{...}
    >>> d.a                                         # dot-access notation
    1
    >>> d                                           # ordered keys
    {'a': 1, 'b': 2, 'c': 3}
    >>> d.update(d=4); d                            # Dict.update() modifies Dict in place
    {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    >>> d(e=5)                                      # new Dict is a copy, doesn't modify existing
    {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}
    >>> d                                           # no changes
    {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    """

    def __init__(xCqNck7t, **kwargs):
        # The random name for self here is necessary to avoid key conflicts with "self"
        # (used as a key, e.g., in the WordPress API).
        dict.__init__(xCqNck7t)
        xCqNck7t.update(**kwargs)        

    def __call__(xCqNck7t, *args, **kwargs):
        """Dict(key=val) creates a new dict with the key:val. That has always been true for 
        initializing a new Dict. But now, this pattern also works for an existing Dict. 
        For example:
        >>> d1 = Dict(a=1, b=2); d2 = d1(c=3); d1; d2
        {'a': 1, 'b': 2}
        {'a': 1, 'b': 2, 'c': 3}
        >>> 
        Note that d1 has not been changed — this method creates a new dict based
        on the old one without changing the old one.
        """
        d = xCqNck7t.__class__(*args, **xCqNck7t)
        d.update(**kwargs)
        return d

    def update(xCqNck7t, **kwargs):
        """Updates the Dict with the given values. Turns internal dicts into Dicts."""
        def dict_list_val(inlist):
            l = []
            for i in inlist:
                if type(i)==dict:
                    l.append(Dict(**i))
                elif type(i)==list:
                    l.append(make_list(i))
                elif type(i)==bytes:
                    l.append(i.decode('UTF-8'))
                else:
                    l.append(i)
            return l
        for k in list(kwargs.keys()):
            if type(kwargs[k])==dict:
                xCqNck7t[k] = Dict(**kwargs[k])
            elif type(kwargs[k])==list:
                xCqNck7t[k] = dict_list_val(kwargs[k])
            else:
                xCqNck7t[k] = kwargs[k]

    # allow dot-notation attribute access alongside dict-notation
    def __getattr__(self, name):
        return dict.get(self, name)       # returns None if the key is not found.

    def __setattr__(self, name, val):
        self[name] = val

    def __repr__(self):
        """displays the Dict with keys in alphabetical order, for consistent test output."""
        keys = self.keys()
        keys.sort()
        return "{" + ", ".join(["%s: %s" % (repr(k), repr(self[k])) for k in keys]) + "}"

    def keys(self, key=None, reverse=False):
        """sort the keys before returning them"""
        ks = sorted(list(dict.keys(self)), key=key, reverse=reverse)
        return ks
        
    def values(self, key=None, reverse=False):
        """sort the values in the same order as the keys"""
        ks = self.keys(key=key, reverse=reverse)
        return [self[k] for k in ks]

    def json(self, indent=None):
        import json as _json
        return _json.dumps(self, indent=indent)
  
class StringDict(Dict):
    """Returns "" when a key does not exist. This is useful in web apps and 
    where a value is going to be built based on conditions, without needing to
    initialize the value first. For example:
    >>> sd = StringDict()
    >>> sd.name += "A Dict"     # Able to use += here.
    """
    def __getattr__(self, name):
        return Dict.get(self, name) or ""

if __name__ == "__main__":
    import doctest
    doctest.testmod()

