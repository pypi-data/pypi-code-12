
import os
from glob import glob, escape

def rglob(dirname, pattern, dirs=False, sort=True):
    """recursive glob, gets all files that match the pattern within the directory tree"""
    fns = glob(os.path.join(dirname, pattern))
    dns = [fn for fn 
            in [escape(os.path.join(dirname, fn)) 
                for fn in os.listdir(dirname)] 
            if os.path.isdir(fn)]
    if dirs==True:
        fns += dns
    for d in dns:
        fns += rglob(d, pattern)
    if sort==True:
        fns.sort()
    return fns
