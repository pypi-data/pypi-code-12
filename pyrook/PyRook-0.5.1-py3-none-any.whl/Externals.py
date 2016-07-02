import os
import sys

try: import pygeoip
except ImportError: pygeoip = None
if os.path.split(sys.path[0])[1].startswith("_MEI"): sys.executable = os.path.join(sys.path[0], "pyrook.exe")
try: import hunspell_cffi as hunspell
except ImportError: hunspell = None
try: import enchant
except ImportError: enchant = None


# wrapper for optional external libraries needed from multiple files
# to avoid circular imports
