import os
import six
from fnmatch import fnmatch

_str_types = (str,)
if six.PY2:
    _str_types = (str, unicode)

#-------------------------------------------------------------------------------
# Exclusion/Inclusion Utilities

def excluded(names, excludes):
    for name in names:
        for pattern in excludes:
            if fnmatch(name, pattern):
                yield name
                break

def applicable(names, patterns, excludes):
    excl = set(excluded(names, excludes))

    for name in names:
        if name in excl:
            continue

        for pattern in patterns:
            if fnmatch(name, pattern):
                yield name
                break

#-------------------------------------------------------------------------------
# Application functions

def apply_callable(cmd, base, names, patterns, excludes):
    for name in applicable(names, patterns, excludes):
        cmd(name)

def apply_command(command, base, names, patterns, excludes, preview=False, 
                  verbose=False):
    if not isinstance(command, _str_types):
        apply_callable(command, base, names, patterns, excludes)
        return

    for name in applicable(names, patterns, excludes):
        path = os.path.join(base, name)
        cmd = command.format(path)
        if verbose:
            print(cmd)
        if not preview:
            os.system(cmd)

#-------------------------------------------------------------------------------

def fmap(root='', command='', patterns=None, excludes=None, max_depth=-1,
         top_down=True, preview=False, verbose=False, apply_dirs=False, 
         follow_links=False):
    
    if patterns is None:
        patterns = ['*']
    if excludes is None:
        excludes = []

    depth = 0
    for base, dirs, files in os.walk(root, topdown=top_down, 
                                     followlinks=follow_links):
        if max_depth >= 0:
            if depth > max_depth:
                return

        if top_down:
            for exdir in list(excluded(dirs, excludes)):
                dirs.remove(exdir)

        apply_command(command, base, files, patterns, excludes, preview, 
                      verbose)
        if apply_dirs:
            apply_command(command, base, dirs, patterns, excludes, preview, 
                          verbose)
        depth += 1
    
#-------------------------------------------------------------------------------

__all__ = ['fmap']

#-------------------------------------------------------------------------------
