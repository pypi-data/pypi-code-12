from ecscli import runCmd
from ecscli import main_parser
import common
import sys
import inspect

from test_common import *



def listAll(silent=False):
    thelist = []
    sys.argv = ["", "varray", "list", "-hostname", HOSTIP, "-cf", COOKIE_FILE]
    result = runCmd()
    printit(result, silent)
    return result
