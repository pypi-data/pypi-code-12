from ecscli import runCmd
from ecscli import main_parser
import common
import sys
import inspect

from test_common import *

def show(silent=False):
    sys.argv = ["", "keystore", "show", "-hostname", HOSTIP, "-cf", COOKIE_FILE]
    result = runCmd()
    printit(result, silent)


def update(silent=False):
    sys.argv = ["", "keystore", "update", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-pkvf", "myserver-rsa.key", "-cvf", "neptune-dev.pem", "-selfsign", "false"]
    result = runCmd()
    printit(result, silent)

def update_ss(silent=False):
    sys.argv = ["", "keystore", "update", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-pkvf", "domain-rsa.key", "-cvf", "domain.crt", "-selfsign", "true"]
    result = runCmd()
    printit(result, silent)


def update_ss_nokey(silent=False):
    sys.argv = ["", "keystore", "update", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-selfsign", "true"]
    result = runCmd()
    printit(result, silent)

def update_try(silent=False):
    sys.argv = ["", "keystore", "update", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-pkvf", "myserver_copy.key", "-cvf", "neptune-dev_copy.pem", "-selfsign", "false"]
    result = runCmd()
    printit(result, silent)

def update_domain(silent=False):
    sys.argv = ["", "keystore", "update", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-pkvf", "domain-rsa.key", "-cvf", "domain.crt", "-selfsign", "false"]
    result = runCmd()
    printit(result, silent)


def update_domain_selfsign(silent=False):
    sys.argv = ["", "keystore", "update", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-pkvf", "domain.key", "-cvf", "domain.crt", "-selfsign", "true"]
    result = runCmd()
    printit(result, silent)


def update_local(silent=False):
    sys.argv = ["", "keystore", "update", "-hostname", "localhost", "-port", "9999", "-cf", COOKIE_FILE, "-pkvf", "myserver.key", "-cvf", "neptune-dev.pem", "-selfsign", "false"]
    result = runCmd()
    printit(result, silent)

