
from __future__ import print_function
import sys
import os

__interactive__ = os.isatty(sys.stdout.fileno())

def eprint(*args, **kwargs):
    # If not interactive (e.g. writing to log), show user from whence msg came
    if not __interactive__:
        print('mdbtools Error: ', file=sys.stderr, end='')
    print(*args,file=sys.stderr,**kwargs)
