from ecscli import runCmd
from ecscli import main_parser
import common
import sys
import types
import inspect

import test_baseurl
import test_bucket
import test_billing
import test_cas
import test_dashboard
import test_datastore
import test_failedzones
import test_keystore
import test_mgmtuserinfo
import test_namespace
import test_objectuser
import test_objectvpool
import test_passwordgroup
import test_secretkeyuser
import test_system
import test_varray
import test_vdc
import test_transformation
import test_virtualdatacenterdata
import test_datafabric
import test_vdckeystore

from test_common import *


def docurl():
    sys.argv = ["","objectuser","list", "-hostname", HOSTIP, "-cf", COOKIE_FILE]
    args = runCmd_parser.parse_args()
    common.COOKIE = args.cookiefile
    #uri = '/block/volume/tasks/CREATE'
    uri = '/vdc/object-pools/10.4.0.101'
    uri = '/vdc/data-stores/10.4.0.101/tasks/CREATE'
    print("JMC uri: " + uri)
    (s, h) = common.service_json_request(HOSTIP, 4443, 'GET',
                                            uri, None, None, False)
    print s
    o = common.json_decode(s)



'''
def printit(result, silent=False):
    if silent == True:
        return
    if(result):
        if isinstance(result, list):
            print("ITS A LIST")
            for record in result:
                print record
        else:
            print result
'''

def objUsersWhoAreMgmtUsers():
    objectUsers = test_objectuser.case5()
    mgmtUsers = test_mgmtuserinfo.case4()

    print("LIST OF OBJECT USERS WHO ARE ALSO MGMT USERS")
    for o in objectUsers:
        if o in mgmtUsers:
            print(o)

'''
{
   "task": [
      {
         "associated_resources": [], 
         "global": null, 
         "link": {
            "href": "/vdc/data-stores/10.4.0.101/tasks/CREATE", 
            "rel": "self"
         }, 
         "name": "CREATE", 
         "op_id": "CREATE", 
         "remote": null, 
         "resource": {
            "id": HOSTIP, 
            "link": {
               "href": "/vdc/object-pools/10.4.0.101", 
               "rel": "self"
            }, 
            "name": HOSTIP
         }, 
         "restLink": null, 
         "state": "pending", 
         "tags": [], 
         "vdc": null
      }
   ]
}
'''

methods = { 'docurl':docurl, 'objUsersWhoAreMgmtUsers':objUsersWhoAreMgmtUsers}
testmodules = []


def importlist():
    for name, val in globals().items():
        if isinstance(val, types.ModuleType):
            if ("test_" in name):
                testmodules.append(name)

def build_dict():
    for m_name in testmodules:
        m = sys.modules[m_name]
        build_module_dict(m, m_name)

def build_module_dict(m, m_name):
    all_functions = inspect.getmembers(m, inspect.isfunction)
    for t in all_functions:
        methods[m_name + '.' + t[0]] = t[1]



def doTest():
    importlist()
    build_dict()

    if sys.argv[1] in methods:
        method_name = sys.argv[1]
        methods[method_name]() # + argument list of course
    else:
        raise Exception("Method %s not implemented" % method_name)

if __name__ == "__main__":
    doTest()
