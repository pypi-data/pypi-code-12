from ecscli import runCmd
from ecscli import main_parser
import common
import sys
import inspect

from test_common import *


def list_all(silent=False):
    thelist = []
    sys.argv = ["", "tenant", "list", "-hostname", HOSTIP, "-cf", COOKIE_FILE]

    result = runCmd()
    printit(result, silent)
    return result


def list_specific(silent=False):
    thelist = []
    sys.argv = ["", "varray", "list", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-uri", "urn:storageos:VirtualArray:0bd2e500-7708-48cc-9a42-c50a5c84e3b7"]

    result = runCmd()
    printit(result, silent)
    return result

