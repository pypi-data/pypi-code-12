"""
This package contains a set of plugins that add basic python support to
HackEdit.
"""
import os
import sys

__version__ = '1.0a2'


vendor = os.path.join(os.path.dirname(__file__), 'vendor')
sys.path.insert(0, vendor)


try:
    # make sure our icons are imported
    from .forms import hackedit_python_rc
except ImportError:
    # not generated yet
    hackedit_python_rc = None
