"""functions to simplify the testing of a module or package.
"""
import doctest, unittest, os, sys, inspect
from bl.rglob import rglob

def list_modules(path, exclude=[]):
    """return a list of modules under the given path
    """
    exclude = [os.path.normpath(os.path.abspath(fn)) for fn in exclude]
    name_prefix = ''
    for p in [p for p in sys.path if p.strip()!='']:
        if p in path:
            name_prefix = '.'.join(os.path.relpath(path, p).split(os.path.sep)) + '.'
            break
    modules = [
        name_prefix + '.'.join(
            os.path.normpath(
                os.path.splitext(
                    os.path.relpath(fn, path))[0]
                ).split(os.path.sep))
        for fn in rglob(path, '*.py')
        if os.path.normpath(os.path.abspath(fn)) not in exclude
    ]
    return modules
