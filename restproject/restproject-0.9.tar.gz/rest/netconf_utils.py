from pprint import pprint
from ctypes import cdll
from .mode_utils import mode

import logging
import platform
import os

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

platform = platform.architecture()
if(platform[0] == '32bit'):
    #lib32 = os.path.abspath('lib/netconf/netopeer/lib32/libmtxnetconfclient.1.0.0.so')
    lib32 = "/auto/kdp-nxos/otm/lib32/libmtxnetconfclient.1.0.0.so"
    lib = cdll.LoadLibrary(lib32)
elif(platform[0] == '64bit'):
    #lib64 = os.path.abspath('lib/netconf/netopeer/lib64/libmtxnetconfclient.1.0.0.so')
    lib64 = "/auto/kdp-nxos/otm/lib64/libmtxnetconfclient.1.0.0.so"
    lib = cdll.LoadLibrary(lib64)

def printFile(file):
    #Print file content
    fRead = open(file,"r")
    log.info(fRead.read())
    fRead.close()

class netconf_utils(mode):
    
    def __init__(self,
                 mgmt_ip,
                 username,
                 password):
        self.mgmt_ip = bytes(str(mgmt_ip),'ascii')
        self.username = bytes(str(username),'ascii')
        self.password = bytes(str(password),'ascii')

    def netconf_connect(self):
        # Method for authenticating and connecting with the device over ssh
        print("###################")
        print("Connecting with DUT")
        print("###################")
        res=lib.cmd_connect(self.mgmt_ip,self.username,self.password)
        if(res != 0):
            log.info("SSH Connection failed")
        print("Session Info\n\r")
        lib.cmd_status();

    def netconf_disconnect(self):
        # Method for disconnecting with the device
        print("###################")
        print("Disconnect with DUT")
        print("###################")
        res=lib.cmd_disconnect()
        if(res != 0):
            log.info("SSH Disconnect failed")

    def netconf_editconfig(self, datastore, defop, error, test, reqFile, respFile):
        # Method for sending edit-config netconf operation
        print("###################")
        print("Sending edit-config to DUT")
        print("###################")
        log.info("edit-config request")
        printFile(reqFile)
        datastore = bytes(str(datastore),'ascii')
        defop = bytes(str(defop),'ascii')
        error = bytes(str(error),'ascii')
        test = bytes(str(test),'ascii')
        reqFile = bytes(str(reqFile),'ascii')
        respFile = bytes(str(respFile),'ascii')
        res=lib.cmd_editconfig(datastore, defop, error, test, reqFile, respFile)
        if(res != 0):
            log.info("Netconf edit-config failed")
        log.info("edit-config response:")
        printFile(respFile)

    def netconf_getconfig(self, datastore, reqFile, respFile, respFile_err):
        # Method for sending get-config netconf operation
        print("###################")
        print("Sending get-config to DUT")
        print("###################")
        log.info("get-config request")
        printFile(reqFile)
        datastore = bytes(str(datastore),'ascii')
        reqFile = bytes(str(reqFile),'ascii')
        respFile = bytes(str(respFile),'ascii')
        respFile_err = bytes(str(respFile_err),'ascii')
        res=lib.cmd_getconfig(datastore, reqFile, respFile, respFile_err)
        if(res != 0):
            log.info("Netconf get-config failed")
        log.info("get-config response:")
        printFile(respFile)

    def netconf_get(self, reqFile, respFile):
        # Method for sending get-config netconf operation
        print("###################")
        print("Sending get to DUT")
        print("###################")
        log.info("get request")
        printFile(reqFile)
        reqFile = bytes(str(reqFile),'ascii')
        respFile = bytes(str(respFile),'ascii')
        res=lib.cmd_get(reqFile, respFile)
        if(res != 0):
            log.info("Netconf get failed")
        log.info("get response:")
        printFile(respFile)
