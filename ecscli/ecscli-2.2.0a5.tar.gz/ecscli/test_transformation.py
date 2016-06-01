
from ecscli import runCmd
from ecscli import main_parser
import common
import os
import sys
import inspect
import json
import time

from email.mime.text import MIMEText
from subprocess import Popen, PIPE

from test_common import *

testNumber = "test2_"
confirmWithMail = True
#emailToList = "joseph.conery@emc.com; yohannes.altaye@emc.com; brian.giracca@emc.com"
emailToList = "joseph.conery@emc.com"

JMC_LOUD = True
JMC_DRYRUN = True



def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

#http://effbot.org/pyfaq/how-do-i-send-mail-from-a-python-script.htm
#http://stackoverflow.com/questions/73781/sending-mail-via-sendmail-from-python
def doMail(subject, msg):
    print('Entered doMail')
    global confirmWithMail

    if confirmWithMail == False:
        return

    sendMailWithPath = which('sendmail')
    if sendMailWithPath is not None:
        print("sendMailWithPath: " + sendMailWithPath)
    else:
        print("sendMailWithPath is None")
        confirmWithMail = False
        return

    msg = MIMEText(msg)
    msg["From"] = "joseph.conery@emc.com"
    msg["To"] = emailToList
    #msg["To"] = "joseph.conery@emc.com"

    msg["Subject"] = subject
    #p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
    p = Popen([sendMailWithPath, "-t", "-oi"], stdin=PIPE)
    p.communicate(msg.as_string())

def testMail():
    doMail("test subject ", "Testing body")

#http://kaira.sgo.fi/2014/05/saving-and-loading-data-in-python-with.html
def saveVar(data, varName):
    varFilename = testNumber + "trans_" + varName + ".json"
    out_file = open(varFilename,"w")
    json.dump(data,out_file, indent=4)
    out_file.close()

def loadVar(varName):
    varFileName = testNumber + "trans_"+varName+".json"
    print("loading " + varName + " from file: " + varFileName )
    in_file = open(varFileName,"r")
    result = json.load(in_file)
    in_file.close()
    return result


def setupVars_test0():
    instanceInfo={
        "type":              "centera",
        "name":              "Centera Transformation",
        "description":       "Centera transformation",
        "replication_group": "urn:storageos:ReplicationGroupInfo:4e64fdb6-f238-4f78-af7b-5032655f92a0:global",
        "admin":             "admin",
        "password":          "migration",
        "management_ip":     "10.247.197.23",
        "port":              3682,
        "access_ip":         "10.247.197.23",
        "datagram_port":     3218
    }
    mappingsInfo={
        "mappings": [
            {
                "source_id": "caspool005/casprofile005",
                "target_user": "casprofile005",
                "target_bucket": "caspool005",
                "target_namespace": "centera_02009a9e-1dd2-11b2-924a-b2660af80a0e"
            }, {
                "source_id": "caspool006/casprofile006",
                "target_user": "ecs_casprofile006",
                "target_bucket": "ecs_caspool006",
                "target_namespace": "centera_02009a9e-1dd2-11b2-924a-b2660af80a0e"
            }
        ]
    }
    sourceIdsInfo={
        "source_ids":
            [
                "caspool005/casprofile005",
                "caspool006/casprofile006"
            ]
    }
    saveVar(instanceInfo, "instanceInfo")
    saveVar(mappingsInfo, "mappingsInfo")
    saveVar(sourceIdsInfo, "sourceIdsInfo")


def setupVars_test1():
    instanceInfo={
        "type":              "centera",
        "name":              "Centera Transformation",
        "description":       "Centera transformation",
        "replication_group": "urn:storageos:ReplicationGroupInfo:d5a678eb-8f04-4a92-ab09-29bed09a5dc7:global",
        "admin":             "admin",
        "password":          "migration",
        "management_ip":     "10.247.197.23",
        "port":              3682,
        "access_ip":         "10.247.197.23",
        "datagram_port":     3218
    }
    mappingsInfo={
        "mappings": [
            {
                "source_id": "caspool001/casprofile001",
                "target_user": "casprofile001",
                "target_bucket": "caspool001",
                "target_namespace": "centera_02009a9e-1dd2-11b2-924a-b2660af80a0e"
            }
        ]
    }
    sourceIdsInfo={
        "source_ids":
        [
                "caspool001/casprofile001",
        ]

    }
    saveVar(instanceInfo, "instanceInfo")
    saveVar(mappingsInfo, "mappingsInfo")
    saveVar(sourceIdsInfo, "sourceIdsInfo")

def setupVars():
    status = False

    if testNumber == "test0_":
        setupVars_test0()
        status = True
    elif testNumber == "test1_":
        setupVars_test1()
        status=True
    else:
        print("Could not find proper test number to initialize setup vars")
        status = False
    return status
    
#########################################################################
# this function just shows the setup vars used for the transformation to the user
# it is not used for transformation itself
#########################################################################
def showTransVars(silent=False):
    instanceInfo = loadVar("instanceInfo")
    printit(instanceInfo, silent)
    mappingsInfo = loadVar("mappingsInfo")
    printit(mappingsInfo, silent)
    sourceIdsInfo = loadVar("sourceIdsInfo")
    printit(sourceIdsInfo, silent)

#########################################################################
# use objectvpool to get the rep group id
# python test.py test_objectvpool.list
#########################################################################
def trans_create(silent=False):
    #o = common.json_decode(instanceInfo)
    o = loadVar("instanceInfo")
    printit(o, silent) 
    sys.argv = ["", "transformation", "create", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE,
        "-type", o['type'], "-admin", o['admin'], "-pw", o['password'], "-mgmt_ip", o['management_ip'], "-access_ip", o['access_ip'],
        "-mgmt_port", str(o['port']), "-datagram_port", str(o['datagram_port']), "-name", o['name'], "-d", o['description'],
        "-rg", o['replication_group']]

    result = runCmd()
    saveVar(result, "create_output")
    printit(result, silent)
    return result


def trans_list(silent=False):
    sys.argv = ["", "transformation", "get", "-hostname", HOSTIP, "-port", "4443", "-cookiefile", COOKIE_FILE,]
    result = None
    result = runCmd()
    printit(result, silent)
    return result

def trans_list_id(silent=False):
    transInfo = loadVar("create_output")
    TRANSID_CURRENT = transInfo['transformation_id']
    sys.argv = ["", "transformation", "get", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, 
        "-transId", TRANSID_CURRENT]
    result = None
    result = runCmd()
    saveVar(result, "trans_list_id_output")
    printit(result, silent)
    return result

######################################################
#
#######################################################
def trans_get_profile_mapping(silent=False):
    transInfo = loadVar("create_output")
    TRANSID_CURRENT = transInfo['transformation_id']
    sys.argv = ["", "transformation", "get-profile-mapping", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE,
        "-transId", TRANSID_CURRENT]
    result = runCmd()
    saveVar(result, "get_profile_mapping_output")
    printit(result, silent)
    return result

######################################################
# internal method 
# to validate the do_profile_mapping
#######################################################
def local_validate_mappings(mapping, silent=False):
    print("Validating the following mapping:")
    printit(mapping)
    conflicts = None
    result = trans_get_profile_mapping(True)
    ecsMappings = result['mappings']
    for ecsMapping in ecsMappings:
        ecsM = ecsMapping['profile_mapping']
        if (mapping['source_id']==ecsM['source_id'] and
             mapping['target_bucket']==ecsM['target_bucket'] and
             mapping['target_namespace']==ecsM['target_namespace'] and
             mapping['target_user']==ecsM['target_user']):
            #found the matching mapping now check for conflicts
            print("found the following matching mapping now check for conflicts")
            printit(ecsMapping)
            conflicts = ecsMapping['conflict']
            if (len(conflicts) == 0):
                return (True, None)
            else:
                print("found a mapping conflict")
                printit(ecsMapping, silent)
                return (False, conflicts)
    return (False, None)
    
    


######################################################
# tuple: source_id^target_user^target_bucket^target_namespace
#######################################################
def trans_do_profile_mapping(silent=False):
    status = False
    result = None
    transInfo = loadVar("create_output")
    printit(transInfo, True)
    TRANSID_CURRENT = transInfo['transformation_id']
    mappingsInfo = loadVar("mappingsInfo")
    mappings = mappingsInfo['mappings']
    printit(mappingsInfo, True)

    if len(mappings) < 1:
        print("ERROR: You need at least one mapping")
        return None

    tmpArr = ["", "transformation", "do-profile-mapping", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-transId", TRANSID_CURRENT, "-mp"]

    for mapping in mappings:
        #let's validate the mapping to make sure it can be found and to make sure there are no conflicts
        isValid, conflicts = local_validate_mappings(mapping)
        if (isValid == False):
            print("The following mapping had a problem:")
            printit(mapping, silent)
            if conflicts is None:
                print("transformation can not continue because the mapping could not be found")
            else:
                print("transformation can not continue due to the following conflict in the profile mapping")
                printit(conflicts, silent)
            return status, conflicts

        mp_arg = mapping['source_id'] + '^' + mapping['target_user'] + '^' + mapping['target_bucket'] + '^' + mapping['target_namespace']
        tmpArr.append(mp_arg)

    sys.argv = tmpArr
    print("All mappings have been validated. The mappings were found and contained no conflicts")
    result = runCmd()
    #printit(result, silent)
    return status

def trans_do_sources(silent=False):
    transInfo = loadVar("create_output")
    TRANSID_CURRENT = transInfo['transformation_id']

    sourceIdsInfo = loadVar("sourceIdsInfo")
    source_ids = sourceIdsInfo['source_ids']
    if len(source_ids) < 1:
        print("ERROR: You need at least one source id")
        return None

    tmpArr = ["", "transformation", "do-trans-sources", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE,
        "-transId", TRANSID_CURRENT, "-si"]

    for si in source_ids:
        tmpArr.append(si)

    sys.argv = tmpArr
    result = runCmd()
    printit(result, silent)
    saveVar(result, "trans_do_sources_output")
    return result

def trans_do_prechecks(silent=False):
    transInfo = loadVar("create_output")
    TRANSID_CURRENT = transInfo['transformation_id']

    sys.argv = ["", "transformation", "do-precheck", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE,
        "-transId", TRANSID_CURRENT]
    result = runCmd()
    printit(result, silent)
    return result


def trans_get_prechecks(silent=False):
    transInfo = loadVar("create_output")
    TRANSID_CURRENT = transInfo['transformation_id']

    sys.argv = ["", "transformation", "get-precheck", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE,
        "-transId", TRANSID_CURRENT]
    result = runCmd()
    printit(result, silent)
    return result

def trans_get_prechecks_loop(silent=False):
    result = None
    isRunning = True
    while isRunning:
        result = trans_get_prechecks(True)
        status = result['status']
        if ((status == "InProgress") or (status == "Pending")):
            print("still running prechecks...")
            time.sleep(10)
        else:
            print("prechecks completed")
            isRunning = False
            saveVar(result, "trans_get_prechecks_output")
            printit(result, silent)
    return result

def trans_do_enum(silent=False):
    transInfo = loadVar("create_output")
    TRANSID_CURRENT = transInfo['transformation_id']

    sys.argv = ["", "transformation", "do-enum", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE,
        "-transId", TRANSID_CURRENT]
    result = runCmd()
    printit(result, silent)
    return result

def trans_get_enum(silent=False):
    #transInfo = loadVar("create_output")
    #TRANSID_CURRENT = transInfo['transformation_id']
    TRANSID_CURRENT = 'JMC'

    sys.argv = ["", "transformation", "get-enum", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE,
        "-transId", TRANSID_CURRENT]
    result = runCmd()
    printit(result, silent)
    return result


def trans_get_enum_loop(silent=False):
    result = None
    isRunning = True
    while isRunning:
        result = trans_get_enum(True)
        status = result['status']
        if ((status == "InProgress") or (status == "Pending")):
            print("still running enumeration...")
            time.sleep(10)
        else:
            print("enumeration completed")
            isRunning = False
            saveVar(result, "trans_get_enum_output")
            printit(result, silent)
    return result




def trans_do_index(silent=False):
    transInfo = loadVar("create_output")
    TRANSID_CURRENT = transInfo['transformation_id']

    sys.argv = ["", "transformation", "do-index", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE,
        "-transId", TRANSID_CURRENT]
    result = runCmd()
    printit(result, silent)
    return result

def trans_get_indexing(silent=False):
    transInfo = loadVar("create_output")
    TRANSID_CURRENT = transInfo['transformation_id']

    sys.argv = ["", "transformation", "get-indexing", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE,
        "-transId", TRANSID_CURRENT]
    result = runCmd()
    printit(result, silent)
    return result

def trans_get_indexing_loop(silent=False):
    result = None
    isRunning = True
    while isRunning:
        result = trans_get_indexing(True)
        status = result['status']
        if ((status == "InProgress") or (status == "Pending")):
            print("still running indexing...")
            time.sleep(10)
        else:
            print("indexing completed")
            #doMail("indexing completed with status: " + status, common.format_json_object(result))
            isRunning = False
            saveVar(result, "trans_get_indexing_output")
            printit(result, silent)
    return result

def trans_do_migration(silent=False):
    transInfo = loadVar("create_output")
    TRANSID_CURRENT = transInfo['transformation_id']

    sys.argv = ["", "transformation", "do-migration", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE,
        "-transId", TRANSID_CURRENT]
    result = runCmd()
    printit(result, silent)
    return result

def trans_get_migration(silent=False):
    transInfo = loadVar("create_output")
    TRANSID_CURRENT = transInfo['transformation_id']

    sys.argv = ["", "transformation", "get-migration", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE,
        "-transId", TRANSID_CURRENT]
    result = runCmd()
    printit(result, silent)
    return result

def trans_get_migration_loop(silent=False):
    result = None
    isRunning = True
    while isRunning:
        print("calling trans_get_migration")
        result = trans_get_migration(True)
        status = result['status']
        if ((status == "InProgress") or (status == "Pending")):
            print("still running migration...")
            time.sleep(10)
        else:
            print("migration completed")
            mailMsg = ""
            isRunning = False
            saveVar(result, "trans_get_migration_output")
            printit(result, silent)
    return result

def trans_do_recon(silent=False):
    transInfo = loadVar("create_output")
    TRANSID_CURRENT = transInfo['transformation_id']

    sys.argv = ["", "transformation", "do-reconcile", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE,
        "-transId", TRANSID_CURRENT]
    result = runCmd()
    printit(result, silent)
    return result

def trans_get_recon(silent=False):
    transInfo = loadVar("create_output")
    TRANSID_CURRENT = transInfo['transformation_id']

    sys.argv = ["", "transformation", "get-recon", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE,
        "-transId", TRANSID_CURRENT]
    result = runCmd()
    printit(result, silent)
    return result

def trans_get_recon_mismatches(silent=False):
    transInfo = loadVar("create_output")
    TRANSID_CURRENT = transInfo['transformation_id']

    sys.argv = ["", "transformation", "get-recon-mismatches", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE,
        "-transId", TRANSID_CURRENT]
    result = runCmd()
    printit(result, silent)
    return result

def trans_cancel_migration(silent=False):
    transInfo = loadVar("create_output")
    TRANSID_CURRENT = transInfo['transformation_id']

    sys.argv = ["", "transformation", "cancel-migration", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE,
        "-transId", TRANSID_CURRENT]
    result = runCmd()
    printit(result, silent)
    return result

def trans_delete_transformation(silent=False):
    transInfo = loadVar("create_output")
    TRANSID_CURRENT = transInfo['transformation_id']

    sys.argv = ["", "transformation", "delete-transformation", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE,
        "-transId", TRANSID_CURRENT]
    result = runCmd()
    printit(result, silent)
    return result


def doTransformation():
    runTransId = ""

    print("THIS IS A SANITY CHECK OF THE SETUP VARS USED IN THIS RUN: " + testNumber)
    print("IT WILL SIMPLY LOAD AND PRINT THE JSON OBJECTS THAT WILL BE USED")
    showTransVars()

    print("\n\n\n")
    print("THIS IS TRANSFORMATION RUN: " + testNumber)
    print("IT WILL USE THE FOLLOWING INFORMATION TO PERFORM A TRANSFORMATION: ")
    showTransVars()
    result = trans_create()
    runTransId = result['transformation_id']
    doMail("transformation was created: " + runTransId, "that is all you need to know")

    print("\n\n\n")
    print("LISTING ALL TRANSFORMATIONS CURRENTLY CREATED")
    result = trans_list()

    print("\n\n\n")
    print("LISTING DETAILS FOR THE CURRENT TRANSFORMATION")
    result = trans_list_id()


    print("\n\n\n")
    print("GETTING THE PROFILE MAPPING")
    result = trans_get_profile_mapping()


    print("\n\n\n")
    print("DOING THE PROFILE MAPPING")
    result = trans_do_profile_mapping()
    if result == None:
        doMail("profile mapping did NOT complete. There is an issue with the user input mapping ", "no message")
        print("profile mapping did NOT complete. There is an issue with the user input mapping")
        return
    if result == False:
        doMail("profile mapping did NOT complete. There appears to be a mapping conflict", "no message")
        print("profile mapping did NOT complete. There appears to be a mapping conflict")
        return


    print("\n\n\n")
    print("DOING THE SOURCES")
    result = trans_do_sources()
    if result == None:
        print("The transformation process is stopping due to the above error")
        return


    print("\n\n\n")
    print("DOING THE PRECHECKS")
    result = trans_do_prechecks()

    print("\n\n\n")
    print("PRECHECKS IS AN ASYNC PROCESS. THIS SCRIPT WILL PERIODICALLY POLL PRECHECKS UNTIL THE STATUS IS NO LONGER InProgress")
    result = trans_get_prechecks_loop()
    status = result['status']
    doMail("precheck completed with status: " + status, common.format_json_object(result))
    if result['status'] != "Succeeded":
        print("prechecks did not seem to succeed. this transformation is stopping")
        return
   
    print("\n\n\n")
    print("DOING THE ENUMERATION")
    result = trans_do_enum()


    print("\n\n\n")
    print("ENUMERATION IS AN ASYNC PROCESS. THIS SCRIPT WILL PERIODICALLY POLL ENUMERATION UNTIL THE STATUS IS NO LONGER InProgress")
    result = trans_get_enum_loop()
    status = result['status']
    doMail("enumeration completed with status: " + status, common.format_json_object(result))
    if result['status'] != "Succeeded":
        print("enumeration did not seem to succeed. this transformation is stopping")
        return


    print("\n\n\n")
    print("DOING THE INDEXING")
    result = trans_do_index()

    print("\n\n\n")
    print("INDEXING IS AN ASYNC PROCESS. THIS SCRIPT WILL PERIODICALLY POLL INDEXING UNTIL THE STATUS IS NO LONGER InProgress")
    result = trans_get_indexing_loop()
    status = result['status']
    doMail("indexing completed with status: " + status, common.format_json_object(result))
    if result['status'] != "Succeeded":
        print("indexing did not seem to succeed. this transformation is stopping")
        return


    print("\n\n\n")
    print("DOING THE MIGRATION!!!!")
    result = trans_do_migration()

    print("\n\n\n")
    print("MIGRATION IS AN ASYNC PROCESS. THIS SCRIPT WILL PERIODICALLY POLL IT UNTIL THE STATUS IS NO LONGER InProgress")
    result = trans_get_migration_loop()
    if result['status'] != "Succeeded":
        print("migration did not seem to succeed. this transformation is stopping")
        print("However, this process will continue to reconcile and look at mismatches ")
        print("as migration is the last functional step in the migration process")
    status = result['status']
    doMail("migration completed with status: " + status, common.format_json_object(result))


    print("\n\n\n")
    print("DOING RECONCILIATION")
    result = trans_do_recon()

    print("\n\n\n")
    print("GETTING RECONCILIATION RESULTS: ")
    result = trans_get_recon()
    doMail("reconconiliation completed", common.format_json_object(result))

    print("\n\n\n")
    print("GETTING RECONCILIATION MISMATCHES: ")
    result = trans_get_recon_mismatches()
    doMail("reconconiliation mismatch check completed", common.format_json_object(result))







def trans_get_inc_enums(silent=False):
    transInfo = loadVar("create_output")
    TRANSID_CURRENT = transInfo['transformation_id']

    sys.argv = ["", "transformation", "get_inc_enums", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE,
        "-transId", TRANSID_CURRENT]
    result = runCmd()
    printit(result, silent)
    return result
