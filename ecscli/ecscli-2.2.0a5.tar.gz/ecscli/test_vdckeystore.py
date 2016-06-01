from ecscli import runCmd
from ecscli import main_parser
import common
import sys
import inspect

from test_common import *

def update1(silent=False):
    sys.argv = ["", "vdc_keystore", "update", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-privateKey", "domain-rsa.key", "-certificateChain", "domain.crt"]

    result = runCmd()
    printit(result, silent)
    return result


#should fail - missing private key
def update2(silent=False):
    sys.argv = ["", "vdc_keystore", "update", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-certificateChain", "somecert"]

    result = runCmd()
    printit(result, silent)
    return result

#should faile - missing cert
def update3(silent=False):
    sys.argv = ["", "vdc_keystore", "update", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-privateKey", "somekey"]

    result = runCmd()
    printit(result, silent)
    return result



def get1(silent=False):
    sys.argv = ["", "vdc_keystore", "get", "-hostname", HOSTIP, "-cf", COOKIE_FILE]

    result = runCmd()
    printit(result, silent)
    return result


