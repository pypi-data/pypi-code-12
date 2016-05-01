#!/usr/bin/env python

# Copyright 2016  Sam Geeraerts
# License: GPLv3 or later

"""FixedLength is an ordered dictionary with attribute-style access
that represents fixed length records
"""

from __future__ import print_function
import collections

class Integer(object):
    """Integer with a fixed length"""

    def __init__(self, length):
        self.length = length
        self.value = 0

    def __str__(self):
        return str(self.value)


class String(object):
    """String with a fixed length"""

    def __init__(self, length):
        self.length = length
        self.value = ''

    def __str__(self):
        return str(self.value)


class FixedLength(collections.OrderedDict):
    """Dictionary-like class with attribute-style access that represents
    fixed length records
    """

    def __getattr__(self, k):
        try:
            try:
                return super().__getattribute__(k)
            except TypeError:  #P2compat
                return super(FixedLength, self).__getattribute__(k)
        except AttributeError:
            try:
                return self[k]
            except KeyError:
                raise AttributeError(k)

    def __setattr__(self, k, v):
        try:
            object.__getattribute__(self, k)
        except AttributeError:
            if k.startswith('_OrderedDict__'):
                super(FixedLength, self).__setattr__(k, v)
            else:
                try:
                    self[k] = v
                except:
                    try:
                        try:
                            super().__setattr__(k, v)
                        except: #P2compat
                            super(FixedLength, self).__setattr__(k, v)
                    except:
                        raise AttributeError(k)
        else:
            object.__setattr__(self, k, v)

    def __str__(self):
        result = ""
        for v in self.values():
            if hasattr(v, 'value'):
                if type(v) is String:
                    fmt = "{{:{:d}s}}".format(v.length)
                elif type(v) is Integer:
                    fmt = "{{:{:d}d}}".format(v.length)
                result += fmt.format(v.value)
            else:
                result += str(v)
        return result

    @property
    def length(self):
        """Return the number of characters in the record"""
        return sum([v.length for v in self.values()])

    def fromstring(self, record):
        """Parse a string as a fixed length record"""
        start = 0
        for v in self.values():
            end = start + v.length
            if hasattr(v, 'value'):
                if type(v) is String:
                    v.value = record[start:end]
                elif type(v) is Integer:
                    v.value = int(record[start:end])
            else:
                v.fromstring(record[start:end])
            start = end
        len_remainder = self.length - start
        if len_remainder > 0:
            self.remainder = String(len_remainder)
            self.remainder.value = record[start:self.length]


if __name__ ==  '__main__':
    t = FixedLength()
    t.foo = String(18)
    t.bar = Integer(4)
    t.foo.value = 'hi there'
    t.bar.value = 123
    t.payload =  FixedLength()
    t.payload.head = String(10)
    t.payload.tail = String(15)
    t.payload.head.value = "In front"
    t.payload.tail.value = "At back"
    print(t)
    r = FixedLength()
    r.first = String(3)
    r.second = String(3)
    r.third = Integer(8)
    r.four = FixedLength()
    r.four.article = Integer(6)
    r.four.stock = Integer(5)
    r.fromstring('CLSFAB2016040512340500025')
    print(r.first, r.second, r.third, r.four.article, r.four.stock)
