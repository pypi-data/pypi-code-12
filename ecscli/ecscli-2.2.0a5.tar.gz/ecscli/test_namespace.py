from ecscli import runCmd
from ecscli import main_parser
import common
import sys
import inspect
import test_objectvpool
import test_mgmtuserinfo

from test_common import *

def createNsReal1(silent=False):
    namespace = 'conerj'
    '''
    print("Current Namespaces:")
    currentNamespacesDict = list2()
    print("------------------------------------")
    currentNamespaces = currentNamespacesDict['namespace']
    for currentN in currentNamespaces:
        if currentN['id'] == namespace:
            print("Could NOT test as this namespace already exists")
            return
    '''

    #list objectvpools and use the first one as the default
    print("Here is a list of object vpools:")
    ovpList = test_objectvpool.list_vpools()
    print("------------------------------------")

    vpools = ovpList['data_service_vpool']
    if len(vpools) < 1:
        print("Could NOT test as there are no vpools to use as the default vpool")
        return
    ovp = vpools[0]
    ovpName = ovp['id']

    print("Here is a list of mgmt users to make one an admin")
    #returns and array not a dict
    mgmtUserList = test_mgmtuserinfo.case4()
    printit(mgmtUserList)
    print("------------------------------------")
    if len(mgmtUserList) < 1:
        print("Could NOT test as there are no mgmt users to set as namespace admin")
        return
    admin = mgmtUserList[0]

    sys.argv = ["", "namespace", "create", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-namespace", "conerj",
        "-ovp", ovpName, "-admin", admin, "-bs", "1"]

    print("TESTING with: ")
    printit(sys.argv)
    print("------------------------------------")

    #common.JMC_DRYRUN = True
    result = None
    result = runCmd()
    printit(result, silent)

#admin is optional, so test without it
def createNsReal2(silent=False):
    namespace = 'conerj'
    '''
    print("Current Namespaces:")
    currentNamespacesDict = list2()
    print("------------------------------------")
    currentNamespaces = currentNamespacesDict['namespace']
    for currentN in currentNamespaces:
        if currentN['id'] == namespace:
            print("Could NOT test as this namespace already exists")
            return
    '''

    #list objectvpools and use the first one as the default
    print("Here is a list of object vpools:")
    ovpList = test_objectvpool.list_vpools()
    print("------------------------------------")

    vpools = ovpList['data_service_vpool']
    if len(vpools) < 1:
        print("Could NOT test as there are no vpools to use as the default vpool")
        return
    ovp = vpools[0]
    ovpName = ovp['id']

    print("Here is a list of mgmt users to make one an admin")
    #returns and array not a dict
    mgmtUserList = test_mgmtuserinfo.case4()
    printit(mgmtUserList)
    print("------------------------------------")
    if len(mgmtUserList) < 1:
        print("Could NOT test as there are no mgmt users to set as namespace admin")
        return
    admin = mgmtUserList[0]

    sys.argv = ["", "namespace", "create", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-namespace", "conerj",
        "-ovp", ovpName, "-bs", "1"]

    print("TESTING with: ")
    printit(sys.argv)
    print("------------------------------------")

    #common.JMC_DRYRUN = True
    result = None
    result = runCmd()
    printit(result, silent)

def createNsReal3(silent=False):
    namespace = 'conerj'
    print("Current Namespaces:")
    currentNamespacesDict = list2()
    print("------------------------------------")
    currentNamespaces = currentNamespacesDict['namespace']
    for currentN in currentNamespaces:
        if currentN['id'] == namespace:
            print("Could NOT test as this namespace already exists")
            return

    #list objectvpools and use the first one as the default
    print("Here is a list of object vpools:")
    ovpList = test_objectvpool.list_vpools()
    print("------------------------------------")

    vpools = ovpList['data_service_vpool']
    if len(vpools) < 1:
        print("Could NOT test as there are no vpools to use as the default vpool")
        return
    ovp = vpools[0]
    ovpName = ovp['id']

    print("Here is a list of mgmt users to make one an admin")
    #returns and array not a dict
    mgmtUserList = test_mgmtuserinfo.case4()
    printit(mgmtUserList)
    print("------------------------------------")
    if len(mgmtUserList) < 1:
        print("Could NOT test as there are no mgmt users to set as namespace admin")
        return
    admin = mgmtUserList[0]

    sys.argv = ["", "namespace", "create", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-namespace", "conerj", "-admin", "joe",
        "-ovp", ovpName]

    print("TESTING with: ")
    printit(sys.argv)
    print("------------------------------------")

    #common.JMC_DRYRUN = True
    result = None
    result = runCmd()
 


def createNs1(silent=False):
    common.JMC_DRYRUN = True
    sys.argv = ["", "namespace", "create", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-namespace", "conerj",
        "-ovp", "defaultOVP", "-admin", "meatgrinder, someotherguy", 
        "-allowedVpools", "allowedvpool1", "allowedvpool2", "-dvp", "disvp1", "disvp2", "-bs", "1", 
        "-ga", "somega"]
    result = runCmd()
    printit(result, silent)

def createNs2(silent=False):
    sys.argv = ["", "namespace", "create", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-namespace", "conerj",
        "-ovp", "defaultOVP", "-admin", "meatgrinder, someotherguy",
        "-dvp", "disvp1", "disvp2", "-bs", "1",
        "-ga", "somega"]
    result = runCmd()
    printit(result, silent)

def createNs3(silent=False):
    sys.argv = ["", "namespace", "create", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-namespace", "conerj",
        "-ovp", "defaultOVP", "-admin", "meatgrinder, someotherguy",
        "-allowedVpools", "allowedvpool1", "allowedvpool2", "-dvp", "allowedvpool2", "disvp1", "disvp2", "-bs", "1",
        "-ga", "somega"]
    result = runCmd()
    printit(result, silent)


def createNs4(silent=False):
    sys.argv = ["", "namespace", "create", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-namespace", "conerj",
        "-ovp", "defaultOVP", "-admin", "meatgrinder, someotherguy",
        "-allowedVpools", "allowedvpool1", "allowedvpool2", "disvp2", "-dvp", "disvp1", "disvp2", "-bs", "1",
        "-ga", "somega"]
    result = runCmd()
    printit(result, silent)


def delete(silent=False):
    sys.argv = ["", "namespace", "delete", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-namespace", "conerj"]
    result = runCmd()
    printit(result, silent)

def case3(silent=False):
    sys.argv = ["", "namespace", "show", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-namespace", "conerj"]
    result = runCmd()
    printit(result, silent)

def show_all(silent=False):
    ans = list2(True)
    namespaces = ans['namespace']
    print("----------------------")
    for n in namespaces:
        name = n['name']
        sys.argv = ["", "namespace", "show", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-namespace", name]
        resultstr = runCmd()
        result = common.json_decode(resultstr)
        name = result['name']
        print("name: " + name)

        if 'namespace_admins' in result:
            admins = result['namespace_admins']
            print("admins: " + admins)

        vpool = result['default_data_services_vpool']
        print("vpool: " + vpool)
        print("----------------------")
        

def list2(silent=False):
    sys.argv = ["", "namespace", "list", "-hostname", HOSTIP, "-cf", COOKIE_FILE]
    result = runCmd()
    printit(result, silent)
    namespaces = result['namespace']
    for n in namespaces:
        name = n['name']
        print("name: " + name)
    return result

def case19(silent=False):
    result = None
    sys.argv = ["", "namespace", "update", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-namespace", "conerj", "-update", "namespace_admins^root"]
    result = runCmd()
    printit(result, silent)
    return result


def case25(silent=False):
    result = None
    sys.argv = ["", "namespace", "delete-quota", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-namespace", "conerj"]
    result = runCmd()
    printit(result, silent)

def case24(silent=False):
    result = None
    sys.argv = ["", "namespace", "update-quota", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-namespace", "conerj", "-block", "2", "-notification", "2"]
    result = runCmd()
    printit(result, silent)

def case22(silent=False):
    result = None
    sys.argv = ["", "namespace", "get-quota", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-namespace", "conerj"]
    result = runCmd()
    printit(result, silent)


def case21(silent=False):
    result = None
    sys.argv = ["", "namespace", "update-ret", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-namespace", "conerj", "-class", "conerjret", "-period", "3"]
    result = runCmd()
    printit(result, silent)

def case18(silent=False):
    result = None
    sys.argv = ["", "namespace", "get-ret-period", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-namespace", "conerj", "-class", "conerjret"]
    result = runCmd()
    printit(result, silent)

def case20(silent=False):
    result = None
    sys.argv = ["", "namespace", "create-ret", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-namespace", "conerj", "-class", "conerjret", "-period", "2"]
    result = runCmd()
    printit(result, silent)


def case17(silent=False):
    result = None
    ans = case16(True)
    namespace = ans['namespace']
    for n in namespace:
        nsName = n['id']
        if nsName == 'conerj':
            sys.argv = ["", "namespace", "show", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-namespace", nsName]
            result = runCmd()
            printit(result, silent)
    return result

def case16(silent=False):
    thelist = []
    sys.argv = ["", "namespace", "list", "-hostname", HOSTIP, "-cf", COOKIE_FILE]

    result = runCmd()
    printit(result, silent)
    namespace = result['namespace']
    for n in namespace:
        name = n["name"]
        print(name)
    return result



def case3(silent=False):
    sys.argv = ["", "namespace", "show", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-namespace", "conerj"]
    result = runCmd()
    printit(result, silent)

def list(silent=False):
    sys.argv = ["", "namespace", "list", "-hostname", HOSTIP, "-cf", COOKIE_FILE]
    result = runCmd()
    printit(result, silent)


