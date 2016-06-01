from ecscli import runCmd
from ecscli import main_parser
import common
import sys
import inspect

from test_common import *


'''
def is_mod_function(mod, func):
    return inspect.isfunction(func) and inspect.getmodule(func) == mod

def list_functions(mod):
    return [func.__name__ for func in mod.__dict__.itervalues() 
            if is_mod_function(mod, func)]


def idk(silent=False):
    print("idk function")
    #print 'functions in current module:\n', list_functions(sys.modules[__name__])
    #print 'functions in inspect module:\n', list_functions(inspect)
    all_functions = inspect.getmembers(sys.modules[__name__], inspect.isfunction)
    for t in all_functions:
        print("JMC adding function name: " + __name__ + "." + t[0])
        #methods['test_bucket.' + t[0]] = t[1]
'''

def case23(silent=False):
    ans = case1(True)
    object_bucket = ans['object_bucket']
    for b in object_bucket:
        print("bucket name: " + b['name'])
        bucketName = b['name']
        sys.argv = ["", "bucket", "get-quota", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-namespace", "conerj", "-name",
                    bucketName]
        result = runCmd()
        printit(result, silent)


def delete_quota1(silent=False):
    sys.argv = ["", "bucket", "delete-quota", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "conerjbucket",
                "-ns", "conerj"]
    result = runCmd()
    printit(result, silent)
    return result

def case1(silent=False):
    print("JMC Entered case1")
    #sys.argv = ["", "bucket", "list", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-namespace", "conerj"]
    #sys.argv = ["", "bucket", "list", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-namespace", "s3"]
    sys.argv = ["", "bucket", "list", "-hostname", HOSTIP, "-cf", COOKIE_FILE, "-namespace", "ns1"]


    result = runCmd()
    printit(result, silent)

    object_bucket = result['object_bucket']
    for b in object_bucket:
        print("bucket name: " + b['name'])
    return result

#########################################################################
#in order to get bucket info, you must be the admin of the namespace where the bucket exists
#########################################################################
def info_all_in_namespace(silent=False):
    ans = case1(True)
    object_bucket = ans['object_bucket']

    for b in object_bucket:
        name = b['name']
        print("getting detailed info for bucket: " + name)
        sys.argv = ["", "bucket", "info", "-hostname", HOSTIP, "-cf", "/Users/conerj/ECS_COOKIEDIR/joecookie", "-name", name]
        result = runCmd()
        printit(result, silent)
    return result

def listpaging1(silent=False):
    sys.argv = ["", "bucket", "list", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-ns", "ns1", "-limit", "2", "-marker", "manyobjects-1"]
    result = runCmd()
    printit(result, silent)
    return result


#########################################################################
# currently failing...not sure if it's due to nonexistent vpool
# (also this bucket name already exists
#########################################################################
def create1(silent=False):
    sys.argv = ["", "bucket", "create", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "conerjbucket", "-vpool",
        "urn:storageos:VirtualArray:b17d28fa-7fc3-465e-9f43-281e72a349eb", "-fs", "true", "-ht", "SWIFT", "-stale_allowed",
        "false", "-ns", "conerj"]
    result = runCmd()
    printit(result, silent)

#########################################################################
# this just worked
#########################################################################
def create2(silent=False):
    sys.argv = ["", "bucket", "create", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "conerjbucket_11_30a", "-vpool",
        "urn:storageos:ReplicationGroupInfo:13a354bc-9197-487c-9fa9-bc0b3cec35b8:global", "-fs", "true", "-ht", "S3", "-stale_allowed",
        "false", "-ns", "conerj"]
    result = runCmd()
    printit(result, silent)

def create_160(silent=False):
    sys.argv = ["", "bucket", "create", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "conerjbucket_11_30a", "-vpool",
        "urn:storageos:ReplicationGroupInfo:b3bf2d47-d732-457c-bb9b-d260eb53a76b:global", "-fs", "true", "-ht", "S3", "-stale_allowed",
        "false", "-ns", "s3", "-enc_enable", "false"]
    result = runCmd()
    printit(result, silent)

def create_160b(silent=False):
    sys.argv = ["", "bucket", "create", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "conerjbucket_11_30b", "-vpool",
        "urn:storageos:ReplicationGroupInfo:b3bf2d47-d732-457c-bb9b-d260eb53a76b:global", "-fs", "true", "-ht", "S3", "-stale_allowed",
        "false", "-ns", "s3"]
    result = runCmd()
    printit(result, silent)

def create_160c(silent=False):
    sys.argv = ["", "bucket", "create", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "conerjbucket_11_30b", "-vpool",
        "urn:storageos:ReplicationGroupInfo:b3bf2d47-d732-457c-bb9b-d260eb53a76b:global", "-fs", "true", "-ht", "S3", "-stale_allowed",
        "false", "-ns", "s3", "-block","1"]
    result = runCmd()
    printit(result, silent)

def create_160d(silent=False):
    sys.argv = ["", "bucket", "create", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "conerjbucket_11_30b", "-vpool",
        "urn:storageos:ReplicationGroupInfo:b3bf2d47-d732-457c-bb9b-d260eb53a76b:global", "-fs", "true", "-ht", "S3", "-stale_allowed",
        "false", "-ns", "s3", "-retention","60"]
    result = runCmd()
    printit(result, silent)


def create_160e(silent=False):
    sys.argv = ["", "bucket", "create", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "conerjbucket_11_30b", "-vpool",
        "urn:storageos:ReplicationGroupInfo:b3bf2d47-d732-457c-bb9b-d260eb53a76b:global", "-fs", "true", "-ht", "S3", "-stale_allowed",
        "false", "-ns", "s3", "-notification","1", "-ts", "tag1^val1", "-ts", "tag2^val2"]
    result = runCmd()
    printit(result, silent)

def add_tags(silent=False):
    sys.argv = ["", "bucket", "add-tags", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "conerjbucket_11_30b", "-ns", "s3",
        "-ts", "tag3^val3", "tag4^tag4"]
    result = runCmd()
    printit(result, silent)

def update_tags(silent=False):
    sys.argv = ["", "bucket", "update-tags", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "conerjbucket_11_30b", "-ns", "s3",
        "-ts", "tag3^val3_updated"]
    result = runCmd()
    printit(result, silent)

def delete_tags(silent=False):
    sys.argv = ["", "bucket", "delete-tags", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "conerjbucket_11_30b", "-ns", "s3",
        "-ts", "tag3^val3"]
    result = runCmd()
    printit(result, silent)


def delete_quota_160(silent=False):
    sys.argv = ["", "bucket", "delete-quota", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "conerjbucket_11_30b",
                "-ns", "s3"]
    result = runCmd()
    printit(result, silent)
    return result

def bucket_tag_info(silent=False):
    sys.argv = ["", "bucket", "info", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "conerjbucket_11_30b", "-ns", "s3"]
    result = runCmd()
    printit(result, silent)
#
#bucket delete failed because I needed to auth with a cookie file from the namespace admin (of the ns that the bucket is in) i.e. joe/ChangeMe
#
def delete1(silent=False):
    sys.argv = ["", "bucket", "delete", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "conerjbucket"] 
    result = runCmd()

def delete2(silent=False):
    sys.argv = ["", "bucket", "delete", "-hostname", HOSTIP, "-cookiefile", "/Users/conerj/ECS_COOKIEDIR/joecookie", "-name", "conerjbucket"]
    result = runCmd()

def delete_160a(silent=False):
    sys.argv = ["", "bucket", "delete", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "conerjbucket_11_30a"]
    result = runCmd()


def delete_160b(silent=False):
    sys.argv = ["", "bucket", "delete", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "conerjbucket_11_30b"]
    result = runCmd()
#1. lock-info from correct namespace user without using namespace arg:
def lock_info1(silent=False):
    sys.argv = ["", "bucket", "lock-info", "-hostname",HOSTIP, "-cookiefile", "/Users/conerj/ECS_COOKIEDIR/joecookie", "-name", "conerjbucket"]
    result = runCmd()
    printit(result, silent)
    return result



#2. lock-info from different namespace user without using namespace arg (should fail)
def lock_info2(silent=False):
    sys.argv = ["", "bucket", "lock-info",  "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "conerjbucket"]
    result = runCmd()
    printit(result, silent)
    return result


#3. lock-info from different namespace user, but passing in namespace arg
def lock_info3(silent=False):
    sys.argv=["", "bucket", "lock-info", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "conerjbucket", "-namespace", "conerj"]
    result = runCmd()
    printit(result, silent)
    return result


#result: failed (not sure that it should as root is the current bucket owner)
def update_owner1(silent=False):
    sys.argv = ["", "bucket", "update-owner", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-ns", "conerj", "-name", "conerjbucket", "-owner", "joe"]
    result = runCmd()
    printit(result, silent)
    return result


def update_owner2(silent=False):
    sys.argv = ["", "bucket", "update-owner", "-hostname", HOSTIP, "-cookiefile", "/Users/conerj/ECS_COOKIEDIR/joecookie", "-ns",
        "conerj", "-name", "conerjbucket", "-owner", "jason"]
    result = runCmd()
    printit(result, silent)
    return result


def update_stale1(silent=False):
    sys.argv =["", "bucket", "update-stale", "-hostname", "10.4.0.102", "-cookiefile", COOKIE_FILE, "-ns", "conerj", "-name", "conerjbucket",\
        "-stale", "true"]
    result = runCmd()
    printit(result, silent)
    return result


def get_acl1(silent=False):
    sys.argv = ["", "bucket", "get-acl", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-ns", "conerj", "-name", "conerjbucket"]
    result = runCmd()
    printit(result, silent)
    return result


'''
see ~/ECS_COOKIEDIR/aclfile.cfg
[main]
owner: stu
user: stu
userperm: full_control
group:
groupperm:
customgroup:
cgperm:
permission: full_control
'''
def set_acl1(silent=False):
    sys.argv = ["", "bucket", "set-acl", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-ns", "conerj", "-name",
        "conerjbucket", i, "-configfile", "/Users/conerj/ECS_COOKIEDIR/aclfile.cfg"]
    result = runCmd()
    printit(result, silent)
    return result


def get_permissions(silent=False):
    sys.argv = ["", "bucket", "get-permissions", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE]
    result = runCmd()
    printit(result, silent)
    return result


def get_groups(silent=False):
    sys.argv = ["", "bucket", "get-groups", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE]
    result = runCmd()
    printit(result, silent)
    return result

'''
def get_bucket_meta(silent=False):
    sys.argv = ["", "bucket", "get-metadata", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "conerjbucket_11_30b",
        "-ht", "S3", "-namespace", "s3"]
    result = runCmd()
    printit(result, silent)
    return result
'''

def get_bucket_meta(silent=False):
    sys.argv = ["", "bucket", "get-metadata", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "casbucket",
        "-ht", "CAS", "-namespace", "s3"]
    result = runCmd()
    printit(result, silent)
    return result

def get_bucket_meta_no_namespace(silent=False):
    sys.argv = ["", "bucket", "get-metadata", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "casbucket",
        "-ht", "CAS"]
    result = runCmd()
    printit(result, silent)
    return result

def set_bucket_meta(silent=False):
    sys.argv = ["", "bucket", "set-metadata", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "casbucket",
        "-ht", "CAS", "-namespace", "s3", "-metaset", "metaName1^metaVal1", "metaName2^metaVal2"]
    result = runCmd()
    printit(result, silent)
    return result

def set_bucket_meta_b(silent=False):
    sys.argv = ["", "bucket", "set-metadata", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "casbucket",
        "-ht", "CAS", "-namespace", "s3", "-metaset", "metaName3^metaVal3", "metaName4^metaVal4"]
    result = runCmd()
    printit(result, silent)
    return result


def del_bucket_meta(silent=False):
    sys.argv = ["", "bucket", "delete-metadata", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "casbucket",
        "-ht", "CAS", "-namespace", "s3"]
    result = runCmd()
    printit(result, silent)
    return result

def list_searchmeta(silent=False):
    sys.argv = ["", "bucket", "list-searchmetadata", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE]
    result = runCmd()
    printit(result, silent)
    return result




def create_searchbucket(silent=False):
    sys.argv = ["", "bucket", "create", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "conerj_searchmeta", "-vpool",
        "urn:storageos:ReplicationGroupInfo:b3bf2d47-d732-457c-bb9b-d260eb53a76b:global", "-fs", "true", "-ht", "S3", "-stale_allowed",
        "false", "-ns", "s3"]
    result = runCmd()
    printit(result, silent)


def create_searchbucket_with_searchmeta(silent=False):
    sys.argv = ["", "bucket", "create", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "conerj_searchmeta", "-vpool",
        "urn:storageos:ReplicationGroupInfo:b3bf2d47-d732-457c-bb9b-d260eb53a76b:global", "-fs", "true", "-ht", "S3", "-stale_allowed",
        "false", "-ns", "s3", "-sm", "CreateTime^System^datetime"]
    result = runCmd()
    printit(result, silent)

def delete_searchmeta(silent=False):
    sys.argv = ["", "bucket", "deactivate-searchmetadata", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, 
        "-name", "conerj_searchmeta","-ns", "s3"]
    result = runCmd()
    printit(result, silent)
    return result

def delete_searchmeta_no_namespace(silent=False):
    sys.argv = ["", "bucket", "deactivate-searchmetadata", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE,
        "-name", "conerj_searchmeta"]
    result = runCmd()
    printit(result, silent)
    return result



def delete_bucket_searchmeta(silent=False):
    sys.argv = ["", "bucket", "delete", "-hostname", HOSTIP, "-cookiefile", COOKIE_FILE, "-name", "conerj_searchmeta"]
    result = runCmd()









