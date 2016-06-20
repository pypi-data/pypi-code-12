"""fuss library.

fuss is a library to benchmark any function
and tell howmuch time it took to execute.

:copyright: (c) 2016 by Rohit Laddha.
"""

__title__ = 'fuss'
__version__ = '0.1.5'
__author__ = 'Rohit Laddha'
__copyright__ = 'Copyright 2016 Rohit Laddha'

from .decorator import measure
from .benchmark import benchmark
