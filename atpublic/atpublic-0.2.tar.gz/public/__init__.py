# Copyright (C) 2016 Barry Warsaw
#
# This project is licensed under the terms of the Apache 2.0 License.  See
# LICENSE.txt for details.

"""@public -- populate __all__"""

from _public import public as c_public
from public.public import public as py_public

__version__ = '0.2'


c_public(public=c_public)
c_public(py_public=py_public)


def _install(which):
    import builtins
    builtins.public = which


def install():
    """Install @public into builtins."""
    _install(c_public)


def py_install():
    """Install the pure-Python @public into builtins."""
    _install(py_public)
