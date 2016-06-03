from __future__ import print_function
from __future__ import absolute_import

import sys
import re
import os
import importlib
import inspect
import pyximport
from .version import __version__

pyximport.install()


# Operation defaults
USE_CYTHON = True
VERBOSE = False


def extract_cython(path_in, force=False, verbose=True):
    """Extract cython code from the .py file and create a _cy.pyx file.

    The script is called by the cythonize decorator.
    """

    if not path_in.endswith('.py'):
        raise ValueError("%s is not a python file" % path_in)

    path_out = path_in.replace('.py', '_cy.pyx')
    if (not force and os.path.exists(path_out) and
        os.path.getmtime(path_out) >= os.path.getmtime(path_in)):
        if verbose:
            print("File %s already exists" % path_out)
        return

    if verbose:
        print("Creating %s" % path_out)
    with open(path_out, 'w') as fobj:
        for line in open(path_in):
            line = line.rstrip()
            m = re.match(r'( *)(.*)#p *$', line)
            if m:
                line = m.group(1) + '#p ' + m.group(2)
            else:
                line = re.sub(r'#c ', '', line)
            fobj.write(line + '\n')


def import_module(name):
    """Import a Cython module via pyximport machinery."""
    path = name.split('.')
    package = '.'.join(path[:-1])
    name_last = path[-1]
    if package:
        # when there is a package, let's add a preceding dot (absolute_import)
        name_last = '.' + name_last
    return importlib.import_module(name_last, package)


def cythonize(func):
    "Function decorator for triggering the pyorcy mechanism."
    if USE_CYTHON:
        # inspect usage found in http://stackoverflow.com/a/7151403
        func_filepath = inspect.getframeinfo(inspect.getouterframes(
            inspect.currentframe())[1][0])[0]
        extract_cython(func_filepath, verbose=VERBOSE)
        module_name = func.__module__ + '_cy'
        module = import_module(module_name)
        func_cy = getattr(module, func.__name__)

    def wrapper(*arg, **kw):
        if USE_CYTHON:
            if VERBOSE:
                print("Running via Cython mode")
            return func_cy(*arg, **kw)
        else:
            if VERBOSE:
                print("Running via Python mode")
            return func(*arg, **kw)

    return wrapper


def test():
    "Programatically run tests."
    import pytest
    sys.exit(pytest.main())


if __name__ == '__main__':
    extract_cython(sys.argv[1])
