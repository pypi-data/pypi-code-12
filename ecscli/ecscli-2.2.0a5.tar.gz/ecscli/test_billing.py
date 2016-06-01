from ecscli import runCmd
from ecscli import main_parser
import common
import sys
import inspect

from test_common import *


def sample1(silent=False):
    sys.argv = ["", "billing",  "sample", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-ns", "ns1", "-d", "true", "-st", "2015-06-18T1:00Z", "-e", "15-06-25T12:00Z"]
    result = runCmd()
    printit(result, silent)
    return result


def sample2(silent=False):
    sys.argv = ["", "billing", "sample", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE,  "-ns", "jason", "-d", "true", "-st", "2015-06-18T1:00Z", "-et", "2015-06-25T12:00Z"]
    result = runCmd()
    printit(result, silent)
    return result

def sample_namespace(silent=False):
    sys.argv = ["", "billing", "sample", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE,  "-ns", "ns1", "-st", "2015-06-18T1:00Z", "-et", "2015-06-25T12:00Z"]
    result = runCmd()
    printit(result, silent)
    return result

def sample_namespace_and_bucket(silent=False):
    sys.argv = ["", "billing", "sample", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE,  "-ns", "ns1", "-bucket", "buk_59", "-st", "2015-06-18T1:00Z", "-et", "2015-06-25T12:00Z"]
    result = runCmd()
    printit(result, silent)
    return result



def info(silent=False):
    sys.argv = ["", "billing", "info", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-ns", "ns1"]
    result = runCmd()
    printit(result, silent)
    return result


def info2(silent=False):
    sys.argv = ["", "billing", "info", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-ns", "ns1", "-bd", "true"]
    result = runCmd()
    printit(result, silent)
    return result

def info3(silent=False):
    sys.argv = ["", "billing", "info", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-ns", "ns1", "-bucket", "buk_59"]
    result = runCmd()
    printit(result, silent)
    return result
