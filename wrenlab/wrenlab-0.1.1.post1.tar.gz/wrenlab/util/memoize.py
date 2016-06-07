"""
Function memoization using joblib.
"""

import os
import os.path

from joblib import Memory

CACHE_DIRECTORY = os.path.expanduser("~/.cache/wrenlab/cache/")
os.makedirs(CACHE_DIRECTORY, exist_ok=True)
memoize = Memory(cachedir=CACHE_DIRECTORY, compress=True).cache
