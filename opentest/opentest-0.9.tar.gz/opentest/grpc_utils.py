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
    #lib32 = os.path.abspath('lib/grpc/lib32/libgrpcclient.so')
    lib32 = "/auto/kdp-nxos/otm/lib32/libgrpcclient.so"
    lib = cdll.LoadLibrary(lib32)
elif(platform[0] == '64bit'):
    #lib64 = os.path.abspath('lib/grpc/lib64/libgrpcclient.so')
    lib64 = "/auto/kdp-nxos/otm/lib64/libgrpcclient.so"
    lib = cdll.LoadLibrary(lib64)

class gRPCclient(object):

    def __init__(self,server_address,cafile,tls,hostoverride):
        self.obj = lib.gRPCclient_new(server_address,cafile,bool(tls),hostoverride)

    def GetConfig(self,uname,pwd,YangPath_filename,output_filename,ReqID,Source):
        lib.GetConfig(self.obj,uname,pwd,YangPath_filename,output_filename,ReqID,Source)
    def GetOper(self,uname,pwd,YangPath_filename,output_filename,ReqID):
        lib.GetOper(self.obj,uname,pwd,YangPath_filename,output_filename,ReqID)
    def EditConfig(self,uname,pwd,YangPath_filename,output_filename,Operation,SessionID,ReqID,Target,DefOp,ErrorOp):
        lib.EditConfig(self.obj,uname,pwd,YangPath_filename,output_filename,Operation,SessionID,ReqID,Target,DefOp,ErrorOp)
    def StartSession(self,uname,pwd,output_filename,ReqID):
        lib.StartSession(self.obj,uname,pwd,output_filename,ReqID)
    def CloseSession(self,uname,pwd,output_filename,ReqID,SessionID):
        lib.CloseSession(self.obj,uname,pwd,output_filename,ReqID,SessionID)
    def KillSession(self,uname,pwd,output_filename,ReqID,SessionID,SessionIDToKill):
        lib.KillSession(self.obj,uname,pwd,output_filename,ReqID,SessionID,SessionIDToKill)
    def DeleteConfig(self,uname,pwd,output_filename,SessionID,ReqID,Target):
        lib.DeleteConfig(self.obj,uname,pwd,output_filename,SessionID,ReqID,Target)
    def CopyConfig(self,uname,pwd,output_filename,SessionID,ReqID,Target,Source):
        lib.CopyConfig(self.obj,uname,pwd,output_filename,SessionID,ReqID,Target,Source)


def printFile(file):
    #Print file content
    fRead = open(file,"r")
    log.info(fRead.read())
    fRead.close()

class grpc_utils(mode,gRPCclient):
    
    def __init__(self,
                 mgmt_ip,
                 username,
                 password,
                 tls,
                 grpcPort):
        self.mgmt_ip = mgmt_ip
        self.username = bytes(str(username),'ascii')
        self.password = bytes(str(password),'ascii')
        cafile_tmp = '/auto/kdp-nxos/otm/grpc.pem'
        cafile = bytes(str(cafile_tmp),'ascii')
        hostoverride = bytes(str("ems.cisco.com"),'ascii')
        server_address = self.mgmt_ip+":"+grpcPort
        server_address = bytes(str(server_address),'ascii')
        gRPCclient.__init__(self,server_address,cafile,tls,hostoverride)

    def grpc_editconfig(self, reqFile, respFile, Operation, SessionID, ReqID, datastore, defop, error):
        # Method for sending edit-config grpc operation
        print("###################")
        print("Sending edit-config to DUT")
        print("###################")
        log.info("edit-config request")
        printFile(reqFile)
        uname = self.username
        pwd = self.password
        Operation = bytes(str(Operation),'ascii')
        Target = bytes(str(datastore),'ascii')
        DefOp = bytes(str(defop),'ascii')
        ErrorOp = bytes(str(error),'ascii')
        YangPath_filename = bytes(str(reqFile),'ascii')
        SessionID = bytes(str(SessionID),'ascii')
        ReqID = bytes(str(ReqID),'ascii')
        output_filename = bytes(str(respFile),'ascii')
        self.EditConfig(uname,pwd,YangPath_filename,output_filename,Operation,SessionID,ReqID,Target,DefOp,ErrorOp)
        log.info("edit-config response:")
        printFile(respFile)

    def grpc_get(self, reqFile, respFile, ReqID):
        # Method for sending edit-config grpc operation
        print("###################")
        print("Sending get to DUT")
        print("###################")
        log.info("get request")
        printFile(reqFile)
        uname = self.username
        pwd = self.password
        YangPath_filename = bytes(str(reqFile),'ascii')
        ReqID = bytes(str(ReqID),'ascii')
        output_filename = bytes(str(respFile),'ascii')
        self.GetOper(uname,pwd,YangPath_filename,output_filename,ReqID)
        log.info("get response:")
        printFile(respFile)
