from ecscli import runCmd
from ecscli import main_parser
import common
import sys
import inspect

from test_common import *


def case10(silent=False):
    thelist = []
    sys.argv = ["", "datastore", "bulk-get", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-ids", HOSTIP]

    result = runCmd()
    printit(result, silent)

def case9(silent=False):
    thelist = []
    #sys.argv = ["", "datastore", "show", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-name", "ecs-obj-1-1.plylab.local"]
    sys.argv = ["", "datastore", "show", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-name", HOSTIP]

    result = runCmd()
    printit(result, silent)


def case8(silent=False):
    thelist = []
    sys.argv = ["", "datastore", "create", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-name","teststore",\
               "-varray", "urn:storageos:VirtualArray:b17d28fa-7fc3-465e-9f43-281e72a349eb", "-datastoreid", HOSTIP]
    result = runCmd()
    printit(result, silent)

def case6(silent=False):
    thelist = []
    sys.argv = ["", "datastore", "list", "-hostname", HOSTIP, "-cf", COOKIE_FILE]
    result = runCmd()
    printit(result, silent)


def case11(silent=False):
    thelist = []
    sys.argv = ["", "datastore", "tasks", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-name", HOSTIP, "-id", "CREATE"]

    result = runCmd()
    printit(result, silent)


