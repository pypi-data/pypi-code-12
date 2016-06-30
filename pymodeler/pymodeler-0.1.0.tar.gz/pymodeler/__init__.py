#!/usr/bin/env python
"""
Infrastructure for creating parametrized models in python.
"""
__author__ = "Alex Drlica-Wagner"


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from .parameter import Property, Derived, Parameter, Param
from .model import Model
