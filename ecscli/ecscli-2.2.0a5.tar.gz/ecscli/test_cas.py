from ecscli import runCmd
from ecscli import main_parser
import common
import sys
import inspect

from test_common import *

def case26():
    thelist = []
    sys.argv = ["", "cas", "get_pea", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-uid", "timbo", "-namespace", "nstim"]
    result = runCmd()
    printit(result)


