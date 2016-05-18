# -*- encoding: utf-8 -*-
from __future__ import unicode_literals, division, \
                       absolute_import, print_function
import pylru


class LRUCache(pylru.lrucache):

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
