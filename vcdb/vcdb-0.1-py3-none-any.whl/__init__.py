"""
Vcdb module initialization.
"""
# Copyright (C) 2016 Thomas Aglassinger.
# Distributed under the GNU Lesser General Public License v3 or later.

# Ensure minimum Python version.
import sys
if sys.version_info[:2] < (3, 4):
    sys.exit('Module vcdb requires Python version 3.4 or later')


__version__ = '0.1'