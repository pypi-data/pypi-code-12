from ecscli import runCmd
from ecscli import main_parser
import common
import sys
import inspect

from test_common import *



def user_add1(silent=False):
    sys.argv = ["", "secretkeyuser",  "user-add", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-uid", "joeouser"]
    result = runCmd()
    printit(result, silent)
    return result



def user_show1(silent=False):
    sys.argv = ["", "secretkeyuser", "user-show", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-uid", "joeouser"]
    result = runCmd()
    printit(result, silent)
    return result


def user_delete1(silent=False):
    sys.argv = ["", "secretkeyuser", "user-delete", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-uid", "joeouser",
        "-sk", "3rl9fmV+s0y2wMbPllVjw0KuQ+X0Lq+Uj+PpWV6Z"]
    result = runCmd()
    printit(result, silent)
    return result


def add1(silent=False):
    sys.argv = ["", "secretkeyuser", "add", "-hostname", HOSTIP, "-cookiefile", "/Users/conerj/ECS_COOKIEDIR/joecookie"]
    result = runCmd()
    printit(result, silent)
    return result


def delete1(silent=False):
    sys.argv = ["", "secretkeyuser", "delete", "-hostname", HOSTIP, "-cookiefile", "/Users/conerj/ECS_COOKIEDIR/joecookie",
        "-sk", "SpUIGJ3enHyWCIbvHT6Su0Idqtds4utlN3zeDpaQ"]
    result = runCmd()
    printit(result, silent)
    return result


#SecretKeyUser - fill both keys and try to add a third (should fail and does)
def user_show2(silent=False):
    sys.argv = ["", "secretkeyuser", "user-show", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-uid", "joeouser"]
    result = runCmd()
    printit(result, silent)
    return result


def user_add2(silent=False):
    sys.argv = ["", "secretkeyuser", "user-add", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-uid", "joeouser"]
    result = runCmd()
    printit(result, silent)
    return result


def user_delete2(silent=False):
    sys.argv = ["", "secretkeyuser", "user-delete", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-uid", "joeouser",
        "-sk", "xegS5TsDqLYYrltv6VFCryrbyb4+VndQ1ZUXe4eo"]
    result = runCmd()
    printit(result, silent)
    return result


def user_add3(silent=False):
    sys.argv = ["", "secretkeyuser", "user-add", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-uid", "joeouser", "-sk", "myownsecretkey"]
    result = runCmd()
    printit(result, silent)
    return result


