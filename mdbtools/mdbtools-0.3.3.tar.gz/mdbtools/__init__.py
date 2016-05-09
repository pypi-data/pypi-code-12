from .MDBcli import *
from .MDBnetrc import *
from .MDBtool import *
from .MDButils import *
from .mdbcat import *
from .mdbcp import *
from .mdbls import *
from .mdbmv import *
from .mdbquery import *
from .mdbrm import *
from .mdbstats import *
from .mdbtouch import *
from .tictoc import *

# Simple func for each mdbtool to be used from the CLI: infer the tool name at
# runtime, instantiate an object of that class, then call its execute() method

def console():
    import os
    import sys
    import mdbtools
    tool = os.path.basename(sys.argv[0])
    klass = getattr(mdbtools, tool)
    klass().execute()
