from ecscli import runCmd
from ecscli import main_parser
import common
import sys
import inspect

from test_common import *



def update1(silent=False):
    sys.argv = ["", "passwordgroup", "update", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-uid", "joeouser",\
        "-namespace", "conerj", "-password", "ChangeMe", "-gl", "admin"]
    result = runCmd()
    printit(result, silent)
    return result

#PasswordGroup (returning to it after creating a secret key )
#GET /object/user-password/{uid}
def list(silent=False):
    sys.argv = ["", "passwordgroup", "list", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-uid", "joeouser"]
    result = runCmd()
    printit(result, silent)
    return result


#GET /object/user-password/{uid}/{namespace}
def list2(silent=False):
    sys.argv = ["", "passwordgroup", "list", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-uid", "joeouser", "-namespace", "conerj"]
    result = runCmd()
    printit(result, silent)
    return result

