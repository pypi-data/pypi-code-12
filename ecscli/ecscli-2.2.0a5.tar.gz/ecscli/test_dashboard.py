from ecscli import runCmd
from ecscli import main_parser
import common
import sys
import inspect

from test_common import *



#GET /dashboard/zones/localzone    Gets the local VDC details
def list_localzone1(silent=False):
    sys.argv = ["", "dashboard", "list-localzone", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE]
    result = runCmd()
    printit(result, silent)
    return result



#GET /dashboard/zones/localzone/replicationgroups    Gets the local VDC replication groups details
def list_lzrepgroup(silent=False):
    sys.argv = ["", "dashboard", "list-lzrepgroup", "-hostname", "10.247.7.161", "-cookiefile", COOKIE_FILE]
    result = runCmd()
    printit(result, silent)
    return result


#GET /dashboard/zones/localzone/rglinksFailed    Gets the local VDC replication groups failed links details
def list_lzrglinksfailed(silent=False):
    sys.argv = ["", "dashboard", "list-lzrglinksfailed", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE]
    result = runCmd()
    printit(result, silent)
    return result


#GET /dashboard/zones/localzone/storagepools    Gets the local VDC storage pools details
def list_lzstoragepools(silent=False):
    sys.argv = ["", "dashboard", "list-lzstoragepools", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE]
    result = runCmd()
    printit(result, silent)
    return result


#GET /dashboard/zones/localzone/nodes    Gets the local VDC nodes details
def list_lznodes(silent=False):
    sys.argv = ["", "dashboard", "list-lznodes", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE]
    result = runCmd()
    printit(result, silent)
    return result


#GET /dashboard/storagepools/{id}    Gets storage pool details
def list_storagepools(silent=False):
    sys.argv = ["", "dashboard", "list-storagepools", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-id", "urn:storageos:VirtualArray:b17d28fa-7fc3-465e-9f43-281e72a349eb"]
    result = runCmd()
    printit(result, silent)
    return result



#GET /dashboard/nodes/{id}    Gets node instance details
def list_nodes(silent=False):
    sys.argv = ["", "dashboard", "list-nodes", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-id", "10.4.0.101"]
    result = runCmd()
    printit(result, silent)
    return result



#GET /dashboard/disks/{id}    Gets disk instance details
def list_disk(silent=False):
    sys.argv = ["", "dashboard", "list-disk", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-id", "10.4.0.101-PD-c4aac2f7-b06d-40e5-960d-97da30fbdb8d"]
    result = runCmd()
    printit(result, silent)
    return result



#GET /dashboard/processes/{id}    Gets process instance details
def list_process(silent=False):
    sys.argv = ["", "dashboard", "list-process", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-id", "10.4.0.101-cas"]
    result = runCmd()
    printit(result, silent)
    return result



#GET /dashboard/nodes/{id}/processes    Gets node instance process details
def list_nodeprocesses(silent=False):
    sys.argv = ["", "dashboard", "list-nodeprocesses", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-id", "10.4.0.101"]
    result = runCmd()
    printit(result, silent)
    return result



#GET /dashboard/nodes/{id}/disks    Gets node instance disk details
def list_nodedisks(silent=False):
    sys.argv = ["", "dashboard", "list-nodedisks", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-id", "10.4.0.101"]
    result = runCmd()
    printit(result, silent)
    return result



#GET /dashboard/storagepools/{id}/nodes    Gets storage pool node details
def list_storagepoolnodes(silent=False):
    sys.argv = ["", "dashboard", "list-storagepoolnodes", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-id", "urn:storageos:VirtualArray:b17d28fa-7fc3-465e-9f43-281e72a349eb"]
    result = runCmd()
    printit(result, silent)
    return result




#GET /dashboard/zones/localzone/rglinksBootstrap    Gets the local VDC replication group bootstrap links details
def list_lzrglinkbootstrap1(silent=False):
    sys.argv = ["", "dashboard", "list-lzrglinkbootstrap", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE]
    result = runCmd()
    printit(result, silent)
    return result

#GET /dashboard/replicationgroups/{id}    Gets the replication group instance details
def list_repgroup1(silent=False):
    sys.argv = ["", "dashboard", "list-repgroup",  "-hostname", "10.247.7.161", "-cookiefile", COOKIE_FILE,
        "-id", "Replication_Group:urn:storageos:ReplicationGroupInfo:1789b18f-ee13-4b5c-b76f-cd378cf1b00a:global"]
    result = runCmd()
    printit(result, silent)
    return result


#GET /dashboard/rglinks/{id}    Gets the replication group link instance details
def list_rglinks(silent=False):
    sys.argv = ["", "dashboard", "list-rglinks",  "-hostname", "10.247.7.161", "-cookiefile", COOKIE_FILE,
        "-id", "urn:storageos:ReplicationGroupInfo:1789b18f-ee13-4b5c-b76f-cd378cf1b00a:global"]
    result = runCmd()
    printit(result, silent)
    return result


#GET /dashboard/replicationgroups/{id}/rglinks    Gets the replication group instance associated link 
def list_repgrouprglinks(silent=False):
    sys.argv = ["", "dashboard", "list-repgrouprglinks", "-hostname", "10.247.7.161", "-cookiefile", COOKIE_FILE,
        "-id", "urn:storageos:ReplicationGroupInfo:1789b18f-ee13-4b5c-b76f-cd378cf1b00a:global"]
    result = runCmd()
    printit(result, silent)
    return result



