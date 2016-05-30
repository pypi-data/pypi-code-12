import os
import pkgutil
import random
import sys


RESOURCE_PACKAGE = 'filks.resources.formats'
RESOURCE_PATHS = (
    'onering.txt',
    'wander.txt',
)


def resource(resource_name, encoding='utf-8'):
    return pkgutil.get_data(RESOURCE_PACKAGE, resource_name).decode(encoding)


def select_format(path=None):
    if not path:
        return resource(random.choice(RESOURCE_PATHS)).strip()
    elif path.strip() == '-':
        return sys.stdin.read().strip()
    elif os.path.exists(path) or ('\n' not in path and '{' not in path and not '}' in path):
        return open(path, 'r', encoding='utf-8').read().strip()
    else:
        return path.strip()  # This is the format itself
