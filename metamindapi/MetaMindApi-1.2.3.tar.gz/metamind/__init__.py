# Python 3 compatibility hack
import sys
if sys.version_info[0] == 3:
  raise NotImplementedError("MetaMindAPI does not support Python 3 at this time. Python 2 can be found here: https://www.python.org/downloads/")
  from types import ModuleType
  if isinstance(__builtins__, ModuleType):
    __builtins__.xrange = range
    __builtins__.basestring = str
    __builtins__.unicode = str
  elif isinstance(__builtins__, dict):
    __builtins__['xrange'] = range
    __builtins__['basestring'] = str
    __builtins__['unicode'] = str
  else:
    print("WARNING: unable to activate Python 3 compatibility")