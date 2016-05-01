import os
from fnmatch import fnmatchcase
import click


class Ignores(object):
    def __init__(self, default_patterns=[]):
        self.patterns = default_patterns

    def read(self, path):
        with open(path, 'r') as stream:
            self.patterns.extend([line.strip() for line in stream])
    
    def match(self, path):
        filename = os.path.basename(path)

        if any(fnmatchcase(filename, pattern) for pattern in self.patterns):
            return True
        else:
            return False
