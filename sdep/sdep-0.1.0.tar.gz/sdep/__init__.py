"""
The base module file for `sdep`.
"""

from .app import Sdep
from .config import Config
from .cli import cli

# The version for `sdep` package, which we read in from `setup.py`.
__version__ = "0.1.0"
