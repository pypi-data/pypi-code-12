from ecscli import runCmd
from ecscli import main_parser
import common
import sys
import inspect

from test_common import *


def case28():
    thelist = []
    sys.argv = ["", "vdc", "get_local", "-hostname", HOSTIP, "-cf", COOKIE_FILE]
    result = runCmd()
    printit(result)
    return result

def case29(silent=False):
    thelist = []
    sys.argv = ["", "vdc", "list", "-hostname", HOSTIP, "-cf", COOKIE_FILE]
    result = runCmd()
    printit(result, silent)
    return result

def case30():
    ans = case29(True)
    vdcList = ans['vdc']
    if len(vdcList) == 0:
        return

    vdc = vdcList[0]
    name = vdc['name']
    sys.argv = ["", "vdc", "show", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-name", name]
    result = runCmd()
    printit(result)

def case31():
    ans = case29(True)
    vdcList = ans['vdc']
    if len(vdcList) == 0:
        return

    vdc = vdcList[0]
    vdcId = vdc['vdcId']
    sys.argv = ["", "vdc", "show", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-vdcid", vdcId]
    result = runCmd()
    printit(result)


def case27():
    thelist = []
    sys.argv = ["", "vdc", "get_secretkey", "-hostname", HOSTIP, "-cf", COOKIE_FILE]
    result = runCmd()
    printit(result)
    return result

