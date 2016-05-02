from .spec import resolve
from .loaders import *
from ._version import get_versions

__all__ = ['resolve'] + loaders.__all__
__version__ = get_versions()['version']

del get_versions
