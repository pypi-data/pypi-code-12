import hashlib
import json
from itertools import tee

from ..core import Task


class cachebust(Task):
    """
    Hashes all input files, and writes their hash value into the filename.

    Also outputs a manifest.json file, containing all the mappings.
    """
    def __init__(self, algorithm='sha512', length=7):
        self.algorithm = algorithm
        self.length = length

    def process(self, inputs):
        mapping = {}
        for t, c, m in inputs:
            c1, c2 = tee(c)
            h = getattr(hashlib, self.algorithm)()
            for chunk in c1:
                h.update(chunk)
            t2 = t.stem + '-' + h.hexdigest()[:self.length] + t.suffix
            mapping[str(t)] = str(t2)
            yield t2, c2, m
        yield 'manifest.json', [json.dumps(mapping).encode('utf-8')], {}
