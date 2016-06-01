from ecscli import runCmd
from ecscli import main_parser
import common
import sys
import inspect

from test_common import *


def case37(silent=False):
    result = None
    ans = case34(True)
    base_url = ans['base_url']
    for b in base_url:
        if "conerj" in b['name']:
            testname = b['name']
            testid = b['id']
            print("updating baseurl named: " + testname)
            print("it has id: " + testid)
            sys.argv = ["", "baseurl", "update", "-hostname", HOSTIP, "-cf", COOKIE_FILE, \
                "-id", testid, "-name", "conerj_baseurl_updated", "-url", "jmcupdated.com"]
            result = runCmd()
            printit(result, silent)
    return result


def case38(silent=False):
    result = None
    ans = case34(True)
    base_url = ans['base_url']
    for b in base_url:
        if "conerj" in b['name']:
            testname = b['name']
            testid = b['id']
            print("deleting baseurl named: " + testname)
            print("it has id: " + testid)
            sys.argv = ["", "baseurl", "delete", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-id", testid]
            result = runCmd()
            printit(result, silent)
    return result

def case34(silent=False):
    thelist = []
    sys.argv = ["", "baseurl", "get", "-hostname", HOSTIP, "-cf", COOKIE_FILE]
    result = runCmd()
    printit(result, silent)
    return result


def case35(silent=False):
    thelist = []
    sys.argv = ["", "baseurl", "create", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-name", "conerj_baseurl", "-baseurl", "jmc.com" ]
    result = runCmd()
    printit(result, silent)
    return result

def jira_10595_A2(silent=False):
    thelist = []    
    sys.argv = ["", "baseurl", "create", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-baseurl", "jmc.com"]
    result = runCmd()
    printit(result, silent)
    return result

def jira_10595_A1(silent=False):
    thelist = []    
    sys.argv = ["", "baseurl", "create", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-name", "conerj_baseurl"]
    result = runCmd()
    printit(result, silent)
    return result

def jira_10595_A(silent=False):
    thelist = []
    sys.argv = ["", "baseurl", "create", "-hostname", HOSTIP, "-cf", COOKIE_FILE]
    result = runCmd()
    printit(result, silent)
    return result

def case36(silent=False):
    result = None
    ans = case34(True)
    base_url = ans['base_url']
    for b in base_url:
        if "conerj" in b['name']:
            testname = b['name']
            testid = b['id']
            print("getting details of baseurl named: " + testname)
            print("it has id: " + testid)
            sys.argv = ["", "baseurl", "get", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-id", testid]
            result = runCmd()
            printit(result, silent)
    return result

