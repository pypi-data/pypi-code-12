from ecscli import runCmd
from ecscli import main_parser
import common
import sys
import inspect

from test_common import *


def list_stores(silent=False):
    thelist = []
    sys.argv = ["", "datastore", "list", "-hostname", HOSTIP, "-cf", COOKIE_FILE]

    result = runCmd()
    printit(result, silent)
    return result

def list_store_tasks(silent=False):
    thelist = []
    sys.argv = ["", "datastore", "tasks", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-name", "ogden-lilac.hop.lab.emc.com"]

    result = runCmd()
    printit(result, silent)
    return result

def list_bulk(silent=False):
    thelist = []
    sys.argv = ["", "datastore", "bulk-get", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-ids", "ogden-lilac.hop.lab.emc.com"]

    result = runCmd()
    printit(result, silent)
    return result

