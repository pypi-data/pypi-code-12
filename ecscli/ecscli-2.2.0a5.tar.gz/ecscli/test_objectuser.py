from ecscli import runCmd
from ecscli import main_parser
import common
import sys
import inspect

from test_common import *

def objectuser_list_uid(silent=False):
    #case5(True)
    sys.argv = ["", "objectuser", "list", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-uid", "joeouser", "-namespace", "conerj"]
    result = runCmd()
    printit(result, silent)

def case5(silent=False):
    objectuserList = []
    sys.argv = ["", "objectuser", "list", "-hostname", HOSTIP, "-cf", COOKIE_FILE]
    result = runCmd()
    #printit(result)
    blobuser = result['blobuser']
    for b in blobuser:
        userid = b['userid']
        objectuserList.append(userid)
        print(userid)
    return objectuserList


