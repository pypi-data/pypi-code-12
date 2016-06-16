from .client import PingboardClient

__version__ = '0.0.2'

import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
   class NullHandler(logging.Handler):
       def emit(self, record):
           pass

logging.getLogger('pyngboard').addHandler(NullHandler())
