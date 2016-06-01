from ecscli import runCmd
from ecscli import main_parser
import common
import sys
import inspect

import test_varray
import test_virtualdatacenterdata

from test_common import *


def case13(silent=False):
    ans = case12(True)
    data_service_vpool = ans['data_service_vpool']
    if len(data_service_vpool) > 0:
        item = data_service_vpool[0]
        repGrpId = item['id']

        sys.argv = ["", "objectvpool", "show", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-id", repGrpId]
        result = runCmd()
        printit(result, silent)
        return result


def list_vpools(silent=False):
    thelist = []
    sys.argv = ["", "objectvpool", "list", "-hostname", HOSTIP, "-cf", COOKIE_FILE]

    result = runCmd()
    printit(result, silent)
    return result

def create1(silent=False):
    vpoolName = 'jigitty'

    varrayResult = test_varray.listAll()
    varrays = varrayResult['varray']
    varray = varrays[0]
    varrayName = varray['name']
    print('Using varray name: ' + varrayName)

    vdcName = ''
    vdcResult = test_virtualdatacenterdata.list_all(True)
    vdcs = vdcResult['vdc']
    for v in vdcs:
        print("Investigating VDC:")
        printit(v, silent)
        if v['local'] == True:
            vdcName = v['name']
            print('Going to use VDC:' + vdcName)
            break

    if vdcName == '':
        print('Did NOT test. No local VDCs')
        return
    print('Using VDC name: ' + vdcName)

    zp = varrayName + '^' + vdcName
    sys.argv = ["", "objectvpool", "create", "-hostname", HOSTIP, "-cf", COOKIE_FILE, '-name', vpoolName, '-desc', 'just for testing and will be removed',
        '-zp', zp, '-allowallnamespaces', 'true']

    JMC_DRYRUN = False
    result = runCmd()
    printit(result, silent)
    return result

def update1(silent=False):
    vpoolNameNew = 'newjigitty'
    vpoolNameOld = 'jigitty'
    vpoolId = ''

    l = list_vpools(silent)
    pools = l['data_service_vpool']
    for p in pools:
        if p['name'] == vpoolNameOld:
            vpoolId = p['id']
            break


    sys.argv = ["", "objectvpool", "update", "-hostname", HOSTIP, "-cf", COOKIE_FILE, '-id', vpoolId, '-name', vpoolNameNew, '-d', 'updated for test and will be removed',
        '-allowallnamespaces', 'false']

    JMC_DRYRUN = False
    result = runCmd()
    printit(result, silent)
    return result

