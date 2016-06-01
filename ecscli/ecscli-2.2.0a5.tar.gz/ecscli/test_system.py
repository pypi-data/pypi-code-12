from ecscli import runCmd
from ecscli import main_parser
import common
import sys
import inspect

from test_common import *


def case33(silent=False):
    thelist = []
    sys.argv = ["", "system", "get-license", "-hostname", HOSTIP, "-cf", COOKIE_FILE]
    result = runCmd()
    printit(result, silent)
    return result


def case32(silent=False):
    thelist = []
    sys.argv = ["", "system", "add-license", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-ltf", "/Users/conerj/ECS_COOKIEDIR/license.txt",\
        "-lff","/Users/conerj/ECS_COOKIEDIR/license_feature.txt"]
    result = runCmd()
    printit(result, silent)
    return result

def case39(silent=False):
    thelist = []
    sys.argv = ["", "system", "add-license", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-ltf", "/Users/conerj/ECS_COOKIEDIR/license.txt"]
    result = runCmd()
    printit(result, silent)
    return result

