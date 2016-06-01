from ecscli import runCmd
from ecscli import main_parser
import common
import sys
import inspect

from test_common import *

def case4(silent=False):
    mgmtuserList = []
    sys.argv = ["", "mgmtuserinfo", "list", "-hostname", HOSTIP, "-cf", COOKIE_FILE]
    result = runCmd()
    #printit(result)
    toplevel = result['mgmt_user_info']
    for top in toplevel:
        userId = top['userId']
        mgmtuserList.append(userId)
        print(userId)
    return mgmtuserList


def list_uid(silent=False):
    mgmtuserList = []
    sys.argv = ["", "mgmtuserinfo", "list", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-userId", "root"]
    result = runCmd()
    printit(result, silent)


def add1(silent=False):
    sys.argv = ["", "mgmtuserinfo", "add", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-uid", "joe", "-password", "ChangeMe"]
    result = runCmd()


def delete1(silent=False):
    sys.argv = ["", "mgmtuserinfo", "delete", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-uid", "joe"]
    result = runCmd()


def update(silent=False):
    sys.argv = ["", "mgmtuserinfo", "update", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-uid", "joe", "-password", "ChangeMe", "-isSystemAdmin", "false"]
    result = runCmd()

def update2(silent=False):
    sys.argv = ["", "mgmtuserinfo", "update", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-uid", "joe", "-password", "ChangeMe", "-isSystemMonitor", "false"]
    result = runCmd()

