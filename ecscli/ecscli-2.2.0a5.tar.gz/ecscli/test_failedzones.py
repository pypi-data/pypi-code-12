from ecscli import runCmd
from ecscli import main_parser
import common
import sys
import inspect

from test_common import *
import test_objectvpool


def case15(silent=False):
    ans = test_objectvpool.case12(True)
    data_service_vpool = ans['data_service_vpool']
    if len(data_service_vpool) > 0:
        item = data_service_vpool[0]
        repGrpId = item['id']

        print("JMC getting failed zone for repGrpId: " + repGrpId)
        sys.argv = ["", "failedzones", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-repGrpId", repGrpId]

        result = runCmd()
        printit(result, silent)
        return result

def case14(silent=False):
    thelist = []
    sys.argv = ["", "failedzones", "-hostname", HOSTIP, "-cf", COOKIE_FILE]

    result = runCmd()
    printit(result, silent)
    return result

