#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
import functools

DEFAULT = object();

class AutoVivification(dict):

    """
    Returns a copy of d without empty leaves
    see: https://stackoverflow.com/questions/27973988/python-how-to-remove-all-empty-fields-in-a-nested-dict/35263074
    """
    def clean_empty(self, d=DEFAULT):
        if d is DEFAULT:
            d = self
        if isinstance(d, list):
            return [v for v in (self.clean_empty(v) for v in d) if v or v == 0]
        elif isinstance(d, type(self)):
            return type(self)({k: v for k, v in ((k, self.clean_empty(v)) for k, v in d.items()) if v or v == 0})
        elif isinstance(d, dict):
            return {k: v for k, v in ((k, self.clean_empty(v)) for k, v in d.items()) if v or v == 0}
        return d

    """
    returns a copy of d with compressed leaves
    """
    def compress(self, d=DEFAULT):
        if d is DEFAULT:
            d = self
        if isinstance(d, list):
            l = [v for v in (self.compress(v) for v in d)]
            try:
                return list(set(l))
            except TypeError:
                # list contains not hashables
                ret = []
                for i in l:
                    if i not in ret:
                        ret.append(i)
                return ret
        elif isinstance(d, type(self)):
            return type(self)({k: v for k, v in ((k, self.compress(v)) for k, v in d.items())})
        elif isinstance(d, dict):
            return {k: v for k, v in ((k, self.compress(v)) for k, v in d.items())}
        return d

    """
    returns a copy of d with all dicts casted to type(self)
    """
    def cast_dicts(self, d=DEFAULT):
        if d is DEFAULT:
            d = self
        if isinstance(d, list):
            return [v for v in (self.cast_dicts(v) for v in d)]
        elif isinstance(d, dict):
            return type(self)({k: v for k, v in ((k, self.cast_dicts(v)) for k, v in d.items())})
        return d

    """
    merges b into a recursively, if a is not given: merges into self
    also merges lists and :
        * merge({a:a},{a:b}) = {a:[a,b]}
        * merge({a:[a]},{a:b}) = {a:[a,b]}
        * merge({a:a},{a:[b]}) = {a:[a,b]}
        * merge({a:[a]},{a:[b]}) = {a:[a,b]}
    """
    def merge(self, b, a=DEFAULT):
        if a is DEFAULT:
            a = self
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    self.merge(b[key], a[key])
                else:
                    if type(a[key]) is list and type(b[key]) is list:
                        a[key] += b[key]
                    elif type(a[key]) is list and type(b[key]) is not list:
                        a[key] += [b[key]]
                    elif type(a[key]) is not list and type(b[key]) is list:
                        a[key] = [a[key]] + b[key]
                    elif type(a[key]) is not list and type(b[key]) is not list:
                        a[key] = [a[key]] + [b[key]]
            else:
                a[key] = b[key]
        return a

    """
    Implementation of perl's autovivification feature.
    see: https://stackoverflow.com/questions/635483/what-is-the-best-way-to-implement-nested-dictionaries-in-python
    """
    def __getitem__(self, item):
        # if the item is a list we autoexpand it
        if type(item) is list:
            return functools.reduce(lambda d, k: d[k], item, self)
        else:
            try:
                return dict.__getitem__(self, item)
            except KeyError:
                value = self[item] = type(self)()
                return value
