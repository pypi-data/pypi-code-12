"""dictutil provides additional classes or functions for python dicts
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict

class DefaultDictWithEnhancedFactory(defaultdict):
    """A dict with a default factory that takes the missing key"""
    def __missing__(self, key):
        return self.default_factory(key)
