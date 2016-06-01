#!/usr/bin/python

# Copyright (c) 2012 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

import common
import json
import ConfigParser
from common import SOSError


class Bucket(object):
    '''
    The class definition for operations on 'Bucket'.
    '''

    # Commonly used URIs for the 'bucket' module

    URI_SERVICES_BASE = ''
    URI_BUCKET = '/object/bucket'
    URI_BUCKET_INSTANCE = URI_BUCKET + '/{0}'
    URI_BUCKET_DEACTIVATE = URI_BUCKET_INSTANCE + '/deactivate'
    URI_BUCKET_RETENTION = URI_BUCKET_INSTANCE + '/retention'
    URI_BUCKET_INFO = URI_BUCKET_INSTANCE + '/info'
    URI_BUCKET_OWNER = URI_BUCKET_INSTANCE + '/owner'
    URI_BUCKET_STALE = URI_BUCKET_INSTANCE + '/isstaleallowed'
    URI_BUCKET_LOCK = URI_BUCKET_INSTANCE + '/lock'
    URI_BUCKET_ACL = URI_BUCKET + '/acl'
    URI_BUCKET_INSTANCE_ACL = URI_BUCKET_INSTANCE + '/acl'
    URI_BUCKET_QUOTA = URI_BUCKET_INSTANCE + '/quota'
    URI_BUCKET_TAGS = URI_BUCKET_INSTANCE + '/tags'
    URI_BUCKET_META = URI_BUCKET_INSTANCE + '/metadata'
    URI_BUCKET_SEARCHMETA = URI_BUCKET + '/searchmetadata'
    URI_BUCKET_DEL_SEARCHMETA = URI_BUCKET_INSTANCE + '/searchmetadata'


    def __init__(self, ipAddr, port, output_format=None):
        '''
        Constructor: takes IP address and port of the ECS instance. These are
        needed to make http requests for REST API
        '''
        self.__ipAddr = ipAddr
        self.__port = port
        self.__format = "json"
        if (output_format == 'xml'):
           self.__format = "xml"


    def bucket_create(self, bucket_id, vpool_id, fs_enable, headtype, namespace, stale_enable, args):
        '''
        Creates a bucket which could be used by users to create objects.
        '''

        if (namespace is None) :
            ou = Objectuser(self.__ipAddr, self.__port, self.__format)
            namespace = ou.objectuser_query('')['namespace']

        parms = {
            'name': bucket_id,
            'vpool': vpool_id,
            'filesystem_enabled': fs_enable,
            'head_type': headtype,
            'namespace': namespace,
            'is_stale_allowed': stale_enable
        }

        if (args.block is not None):
            parms['blockSize'] = args.block

        if (args.notification is not None):
            parms['notificationSize'] = args.notification

        parms['is_encryption_enabled'] = args.enc_enable

        if (args.retention is not None):
            parms['retention'] = args.retention

        if(args.tagset is not None):
            parms['TagSet'] = []
            for ts in args.tagset:
                pair = ts.split('^')
                if (len(pair)<2):
                    raise SOSError(SOSError.SOS_FAILURE_ERR, "A tagset must be a key value pair string delimited by '^'")
                parms['TagSet'].append({"Key" : pair[0], "Value" : pair[1]})

        if(args.searchmeta is not None):
            parms['search_metadata'] = []
            for ts in args.searchmeta:
                pair = ts.split('^')
                if (len(pair)<3):
                    raise SOSError(SOSError.SOS_FAILURE_ERR, "A tagset must be a key value pair string delimited by '^'")
                parms['search_metadata'].append({"name" : pair[0], "type" : pair[1], "datatype" : pair[2]})


        body = json.dumps(parms)

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "POST",
                                             Bucket.URI_BUCKET, body, None, xml)


        if(self.__format == "json"):
            o = common.json_decode(s)
            if (not o):
                return {}
            return o

        return s

    def bucket_delete(self, bucket_id, namespace=None):
        '''
        Deletes the specified bucket.
        '''

        uri = Bucket.URI_BUCKET_DEACTIVATE.format(bucket_id)
        if (namespace):
            uri += "?namespace=" + namespace     

        xml = False
        if self.__format == "xml":
            xml = True

        (s,h) = common.service_json_request(self.__ipAddr, self.__port, "POST",
                                            uri, None, None, xml)


        return


    def bucket_list(self, namespace, marker, limit):
        '''
        Lists all configured buckets associated with a namespace
        '''

        uri = Bucket.URI_BUCKET

        # appends query parameters
        if ((namespace is not None) or (marker is not None) or (limit is not None)):

            uri = uri + '?'
            f = 0

            if (namespace is not None):
                uri = uri + 'namespace=' + namespace
                f += 1
            if (marker is not None):
                if (f != 0):
                    uri = uri + '&'
                uri = uri + 'marker=' + marker
                f += 1
            if (limit is not None):
                if (f != 0):
                    uri = uri + '&'
                uri = uri + 'limit=' + limit

        xml = False
        if self.__format == "xml":
            xml = True

        (s,h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                                            uri, None, None, xml)


        if(self.__format == "json"):
            o = common.json_decode(s)
            return o
        return s

    def get_bucket_info(self, bucket_id, namespace=None):
        '''
        Gets bucket information for the specified bucket
        '''
        uri = Bucket.URI_BUCKET_INFO.format(bucket_id)
        if (namespace is not None):
            uri = uri + '?namespace=' + namespace

        xml = False
        if self.__format == "xml":
            xml = True

        (s,h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                                            uri, None, None, xml)


        o = common.json_decode(s)
        if (not o):
            return {}

        return o


    def get_lock(self, bucket_id, namespace=None):
        '''
        Gets lock information for the specified bucket and
        namespace. If namespace is null, then current
        user's namespace is used.
        '''

        if (namespace is None):
            uri = Bucket.URI_BUCKET_INFO.format(bucket_id)

            (s,h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                                        uri, None)
            o = common.json_decode(s)

            if('namespace' in o):
                namespace = o['namespace']

            #else you aren't authenticated in the correct namespace and you need didn't pass in a namespace arg either
            else:
                return {}

        uri = Bucket.URI_BUCKET_LOCK.format(bucket_id) + '?namespace=' + namespace
        #uri = Bucket.URI_BUCKET_LOCK.format(bucket_id)
        
        xml = False
        if self.__format == "xml":
            xml = True

        (s,h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                                            uri.format(bucket_id), None, None, xml)


        if(self.__format == "json"):
            o = common.json_decode(s)
            if (not o):
                return {}
            return o

        return s


    def lock_bucket(self, bucket_id, lock):
        '''
        Locks or unlocks specified bucket.
        '''

        parms = { }
        (s,h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                                            Bucket.URI_BUCKET_INFO.format(bucket_id), None)
        o = common.json_decode(s)

        if('namespace' in o):
            parms['namespace'] = o['namespace']

        body = json.dumps(parms)

        uri = Bucket.URI_BUCKET_LOCK + '/{1}'
        (s,h) = common.service_json_request(self.__ipAddr, self.__port, "PUT",
                                            uri.format(bucket_id, lock), body)
        return


    def update_owner(self, bucket_id, namespace, owner):
        '''
        Updates the owner for the specified bucket.
        '''

        parms = {
            'namespace': namespace,
            'new_owner': owner
        }
        body = json.dumps(parms)


        xml = False
        if self.__format == "xml":
            xml = True

        (s,h) = common.service_json_request(self.__ipAddr, self.__port, "POST",
                                            Bucket.URI_BUCKET_OWNER.format(bucket_id), body, None, xml)

        if(self.__format == "json"):
            o = common.json_decode(s)
            if (not o):
                return {}
            return o

        return s


    def update_stale(self, bucket_id, namespace, stale_allowed):
        '''
        Updates isStaleAllowed details for the specified bucket.
        '''

        parms = { 'is_stale_allowed': stale_allowed }

        # If namespace not defined by user, uses bucket default.
        if (namespace is not None):
            parms['namespace'] = namespace
        else:
            (s,h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                                                Bucket.URI_BUCKET_INFO.format(bucket_id), None, None, False)
            o = common.json_decode(s)
            if('namespace' in o):
                parms['namespace'] = o['namespace']

        body = json.dumps(parms)

        xml = False
        if self.__format == "xml":
            xml = True

        (s,h) = common.service_json_request(self.__ipAddr, self.__port, "POST",
                                            Bucket.URI_BUCKET_STALE.format(bucket_id), body, None, xml)

        if(self.__format == "json"):
            o = common.json_decode(s)
            if (not o):
                return {}
            return o

        return s


    def get_retention_period(self, bucket_id, namespace=None):
        '''
        Gets the default retention setting for the specified bucket
        '''

        uri = Bucket.URI_BUCKET_RETENTION.format(bucket_id)

        if (namespace):
            uri += "?namespace=" + namespace

        xml = False
        if self.__format == "xml":
            xml = True

        (s,h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                                            uri, None, None, xml)

        if(self.__format == "json"):
            o = common.json_decode(s)
            if (not o):
                return {}
            return o

        return s


    def update_retention_period(self, bucket_id, period, namespace=None):
        '''
        Updates the default retention setting for the specified bucket
        '''

        parms = { 'period': period }
        if (namespace):
            parms['namespace'] = namespace

        body = json.dumps(parms)

        (s,h) = common.service_json_request(self.__ipAddr, self.__port, "PUT",
                                            Bucket.URI_BUCKET_RETENTION.format(bucket_id), body)
        return


    def get_quota(self, bucket_id, namespace):
        '''
        Gets the quota for the given bucket and namespace.
        '''

        uri = Bucket.URI_BUCKET_QUOTA.format(bucket_id)

        '''
        #get quota uri from urihelper
        from quota import Quota
        quota_obj = Quota(self.__ipAddr, self.__port)
        uri = quota_obj.__get_quota_uri("bucket", bucket_id)
        '''

        if (namespace is not None):
            uri = uri + "?namespace=" + namespace


        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr,
                self.__port, "GET", uri, None, None, xml)

        if(self.__format == "json"):
            o = common.json_decode(s)
            if (not o):
                return {}
            return o

        return s


    def update_quota(self, bucket_id, block, notification, namespace):
        '''
        Updates the quota for the specified bucket
        '''

        uri = Bucket.URI_BUCKET_QUOTA.format(bucket_id)

        parms = {
            'blockSize': block,
            'notificationSize': notification,
            'namespace': namespace
        }
        body = json.dumps(parms)
  
        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "PUT", uri, body, None, xml)

        # there is no body returned
        return

    def delete_quota(self, bucket_id, namespace):
        '''
        Deletes the quota setting for the given bucket and namespace.
        '''
        uri = Bucket.URI_BUCKET_QUOTA.format(bucket_id)

        if (namespace is not None):
            uri = uri + "?namespace=" + namespace

        (s, h) = common.service_json_request(self.__ipAddr,
                                             self.__port, "DELETE", uri, None)

        return


    def get_acl(self, bucket_id, namespace):
        '''
        Gets the ACL for the given bucket. User's current namespace is used
        '''

        if (namespace is None):
            (s,h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                                                Bucket.URI_BUCKET_INFO.format(bucket_id), None, None, False)
            o = common.json_decode(s)

            if('namespace' in o):
                namespace = o['namespace']

        uri = Bucket.URI_BUCKET_INSTANCE_ACL.format(bucket_id) 
        if (namespace):
            uri += '?namespace=' + namespace

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                                             uri, None, None, xml)

        if(self.__format == "json"):
            o = common.json_decode(s)
            if (not o):
                return {}
            return o
        return s


    def set_acl(self, bucket_id, namespace, owner, user, userperm, group,
                groupperm, customgroup, cgperm, permission):
        '''
        Updates the ACL for the given bucket. If namespace is not specified
        in the payload, the current user's namespace is used.
        '''

        #retrieve existing namespace if not provided
        if (namespace is None):
            (s,h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                                                Bucket.URI_BUCKET_INFO.format(bucket_id), None, None, False)
            o = common.json_decode(s)

            if('namespace' in o):
                namespace = o['namespace']

        #retrieve existing permissions if unchanged
        if (permission is None):
            (s,h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                    (Bucket.URI_BUCKET_INSTANCE_ACL.format(bucket_id) + '?namespace=' + namespace), None, None, False)
            o = common.json_decode(s)

            if('permission' in o and permission is not None):
                permission = o['permission']

        parms = {
            'bucket': bucket_id,
            'acl': None
            }

        if (namespace):
            parms['namespace'] = namespace
        if (permission):
            parms['permission'] = [permission]

        acl = dict()
        acl['owner'] = owner

        user_acl = dict()
        group_acl = dict()
        customgroup_acl = dict()

        acl['user_acl'] = []
        if ((user != None) and (len(user) > 0)):
            user_acl['user'] = user
            user_acl['permission'] = userperm.split(',')
            acl['user_acl'] = [user_acl]

        acl['group_acl'] = []
        if ((group != None) and (len(group) > 0)):
            group_acl['group'] = group
            group_acl['permission'] = groupperm.split(',')
            acl['group_acl'] = [group_acl]

        acl['customgroup_acl'] = []
        if ((customgroup != None) and (len(customgroup) > 0)):
            customgroup_acl['customgroup'] = customgroup
            customgroup_acl['permission'] = cgperm.split(',')
            acl['customgroup_acl'] = [customgroup_acl]

        parms['acl'] = acl


        body = json.dumps(parms)
        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "PUT",
                                             Bucket.URI_BUCKET_INSTANCE_ACL.format(bucket_id), body)
        return s


    def get_permissions(self):
        '''
        Gets all ACL permissions
        '''

        uri = Bucket.URI_BUCKET_ACL + '/permissions'

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                                             uri, None, None, xml)

        if(self.__format == "json"):
            o = common.json_decode(s)
            if (not o):
                return {}
            return o
        return s

    def get_groups(self):
        '''
        Gets all ACL groups
        '''

        uri = Bucket.URI_BUCKET_ACL + '/groups'

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                                             uri, None, None, xml)

        if(self.__format == "json"):
            o = common.json_decode(s)
            if (not o):
                return {}
            return o

        return s

    def add_update_tags(self, args, addTags):
        uri = Bucket.URI_BUCKET_TAGS.format(args.name)
        parms = {
            'namespace': args.namespace
        }

        if(args.tagset is not None):
            parms['TagSet'] = []
            for ts in args.tagset:
                pair = ts.split('^')
                if (len(pair)<2):
                    raise SOSError(SOSError.SOS_FAILURE_ERR, "A tagset must be a key value pair string delimited by '^'")
                parms['TagSet'].append({"Key" : pair[0], "Value" : pair[1]})

        body = json.dumps(parms)
 
        xml = False
        if self.__format == "xml":
            xml = True

        verb = "PUT"
        if (addTags == True):
            verb = "POST"

        print("body: " + body)
        print("uri: ") + uri
        (s, h) = common.service_json_request(self.__ipAddr, self.__port, verb, uri, body, None, xml)
        return s

    def delete_tags(self, args):
        uri = Bucket.URI_BUCKET_TAGS.format(args.name)
        parms = {
            'namespace': args.namespace
        }

        if(args.tagset is not None):
            parms['TagSet'] = []
            for ts in args.tagset:
                pair = ts.split('^')
                if (len(pair)<2):
                    raise SOSError(SOSError.SOS_FAILURE_ERR, "A tagset must be a key value pair string delimited by '^'")
                parms['TagSet'].append({"Key" : pair[0], "Value" : pair[1]})

        body = json.dumps(parms)

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "DELETE", uri, body, None, xml)

        return s

    def get_meta(self, args):
        uri = Bucket.URI_BUCKET_META.format(args.name)

        if (args.namespace is not None):
            uri += "?namespace=" + args.namespace

        if (args.headtype is not None):
            if (args.namespace is not None):
                uri += "&"
                uri += "headType=" + args.headtype
            else:
                uri += "?headType=" + args.headtype

        body = None
        xml = False
        if self.__format == "xml":
            xml = True
        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "GET", uri, body, None, xml)
 
        if(self.__format == "json"):
            o = common.json_decode(s)
            if (not o):
                return {}
            return o
        return s


    def set_meta(self, args):
        uri = Bucket.URI_BUCKET_META.format(args.name)

        parms = {}

        if (args.namespace is not None):
            parms["namespace"] = args.namespace

        if (args.headtype is not None):
            parms["head_type"] = args.headtype

        if(args.metaset is not None):
            parms['metadata'] = []
            for ts in args.metaset:
                pair = ts.split('^')
                if (len(pair)<2):
                    raise SOSError(SOSError.SOS_FAILURE_ERR, "A tagset must be a key value pair string delimited by '^'")
                parms['metadata'].append({"name" : pair[0], "value" : pair[1]})

        body = json.dumps(parms)

        xml = False
        if self.__format == "xml":
            xml = True
        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "PUT", uri, body, None, xml)

        return

    def delete_meta(self, args):
        uri = Bucket.URI_BUCKET_META.format(args.name)

        if (args.namespace is not None):
            uri += "?namespace=" + args.namespace

        if (args.headtype is not None):
            if (args.namespace is not None):
                uri += "&"
                uri += "headType=" + args.headtype
            else:
                uri += "?headType=" + args.headtype

        body = None
        xml = False
        if self.__format == "xml":
            xml = True
        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "DELETE", uri, body, None, xml)

        return

    def list_search_meta(self, args):
        uri = Bucket.URI_BUCKET_SEARCHMETA

        body = None
        xml = False
        if self.__format == "xml":
            xml = True
        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "GET", uri, body, None, xml)

        if(self.__format == "json"):
            o = common.json_decode(s)
            if (not o):
                return {}
            return o
        return s

    def del_search_meta(self, args):
        uri = Bucket.URI_BUCKET_DEL_SEARCHMETA.format(args.name)

        if (args.namespace is not None):
            uri += "?namespace=" + args.namespace

        body = None
        xml = False
        if self.__format == "xml":
            xml = True
        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "DELETE", uri, body, None, xml)
                                
        return              



def create_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'create',
        description='ECS Bucket Create CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='create bucket')

    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-name', '-n',
                                help='Name of Bucket',
                                metavar='<bucketname>',
                                dest='name',
                                required=True)

    mandatory_args.add_argument('-vpool', '-vp',
                                help='bucket vPool ID',
                                dest='vpool', metavar='<vpool>',
                                required=True)

    mandatory_args.add_argument('-fs_enable', '-fs',
                                help='flag indicating whether file-system is enabled for bucket',
                                dest='fs_enable', metavar='<filesystem_enabled>',
                                required=True)

    mandatory_args.add_argument('-headtype', '-ht',
                                help='object head type allowed to access bucket',
                                dest='headtype', metavar='<head_type>',
                                required=True)

    mandatory_args.add_argument('-stale_allowed', '-stale', '-sa',
                                help='tag to allow stale data in bucket',
                                dest='stale_allowed', metavar='<is_stale_allowed>',
                                required=True)

    mandatory_args.add_argument('-namespace', '-ns',
                                help='namespace associated with bucket user/tenant',
                                dest='namespace', metavar='<namespace>',
                                default=None, required=True)

    create_parser.add_argument('-block', '-blk',
                                help='block size in GB',
                                metavar='<block>',
                                dest='block')

    create_parser.add_argument('-notification', '-not',
                                help='notification size in GB',
                                metavar='<notification>',
                                dest='notification')

    create_parser.add_argument('-enc_enable', '-enc',
                                help='flag indicating whether encryption is enabled for bucket',
                                dest='enc_enable', metavar='<is_encryption_enabled>',
                                default='false',
                                choices=['true', 'false']) 
                                
    create_parser.add_argument('-retention', '-ret', 
                                help='retention period in seconds',
                                metavar='<retention>',
                                dest='retention')


    create_parser.add_argument('-tagset','-ts',
                                help='List of one or more tagset tagname^tagvalue tuples ' +
                                     'eg list of tag^value',
                                metavar='<tagset>',
                                dest='tagset',
                                nargs='+')
 
    create_parser.add_argument('-searchmeta','-sm',
                                help='List of one or more searchmeta name^type^datatype tuples ',
                                metavar='<searchmeta>',
                                dest='searchmeta',
                                nargs='+')

    create_parser.set_defaults(func=bucket_create)

def bucket_create(args):

    obj = Bucket(args.ip, args.port)

    try:
        res = obj.bucket_create(args.name,
                                args.vpool,
                                args.fs_enable,
                                args.headtype,
                                args.namespace,
                                args.stale_allowed, args)
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.NOT_FOUND_ERR,
                           SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Bucket " +
                           args.name + ": Create failed\n" + e.err_text)
        else:
            raise e


def delete_parser(subcommand_parsers, common_parser):
    # delete command parser
    delete_parser = subcommand_parsers.add_parser(
        'delete',
        description='ECS Bucket Delete CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='delete bucket')

    mandatory_args = delete_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-name', '-n',
                                help='Name of Bucket',
                                metavar='<bucketname>',
                                dest='name',
                                required=True)


    delete_parser.add_argument('-namespace', '-ns',
                             help='Namespace of bucket being deleted if it is not in the namespace where current user is admin',
                             metavar='<namespace>',
                             default=None,
                             dest='namespace')


    delete_parser.set_defaults(func=bucket_delete)

def bucket_delete(args):

    obj = Bucket(args.ip, args.port)

    try:
        obj.bucket_delete(args.name, args.namespace)
    except SOSError as e:
        if (e.err_code in [SOSError.NOT_FOUND_ERR,
                           SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "Bucket delete failed\n" + e.err_text)
        else:
            raise e


def list_parser(subcommand_parsers, common_parser):
    # list command parser
    list_parser = subcommand_parsers.add_parser(
        'list',
        description='ECS Bucket List CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='list buckets')

    list_parser.add_argument('-namespace', '-ns',
                             help='Namespace of Buckets',
                             metavar='<namespace>',
                             default=None,
                             dest='namespace')

    list_parser.add_argument('-marker', '-m',
                             help='Reference to Last Object Returned',
                             metavar='<marker>',
                             default=None,
                             dest='marker')

    list_parser.add_argument('-limit', '-l',
                             help='Number of Objects to List',
                             metavar='<limit>',
                             default=None,
                             dest='limit')

    list_parser.set_defaults(func=bucket_list)

def bucket_list(args):
    obj = Bucket(args.ip, args.port)

    try:
        res = obj.bucket_list(args.namespace,
                              args.marker,
                              args.limit)
        return res

    except SOSError as e:
        if(e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "Bucket list failed: " + e.err_text)
        else:
            raise e


def get_info_parser(subcommand_parsers, common_parser):
    # info command parser
    get_info_parser = subcommand_parsers.add_parser(
        'info',
        description='ECS Bucket Info CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='get bucket info')

    mandatory_args = get_info_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-name', '-n',
                            help='Name of Bucket',
                            metavar='<bucketname>',
                            dest='name',
                            required=True)

    get_info_parser.add_argument('-namespace', '-ns',
                                 help='Namespace of Bucket',
                                 metavar='<namespace>',
                                 dest='namespace')

    get_info_parser.set_defaults(func=get_info)

def get_info(args):

    obj = Bucket(args.ip, args.port)

    try:
        res = obj.get_bucket_info(args.name, args.namespace)
        return res
    except SOSError as e:
        if(e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "Bucket retrieval failed: " + e.err_text)
        else:
            raise e


def get_lock_parser(subcommand_parsers, common_parser):
    # lock-info command parser
    get_lock_parser = subcommand_parsers.add_parser(
        'lock-info',
        description='ECS Bucket Lock Info CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='get bucket lock info')

    mandatory_args = get_lock_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-name', '-n',
                                help='Name of Bucket',
                                metavar='<bucketname>',
                                dest='name',
                                required=True)

    get_lock_parser.add_argument('-namespace', '-ns',
                                 help='Namespace of Bucket',
                                 metavar='<namespace>',
                                 dest='namespace')

    get_lock_parser.set_defaults(func=get_lock)

def get_lock(args):

    obj = Bucket(args.ip, args.port)

    try:
        res = obj.get_lock(args.name,
                           args.namespace)
        return res
    except SOSError as e:
        if(e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "Bucket retrieval failed: " + e.err_text)
        else:
            raise e


def lock_bucket_parser(subcommand_parsers, common_parser):
    # lock command parser
    lock_bucket_parser = subcommand_parsers.add_parser(
        'lock',
        description='ECS Bucket Lock CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='lock/unlock bucket')

    mandatory_args = lock_bucket_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-name', '-n',
                                help='Name of Bucket',
                                metavar='<bucketname>',
                                dest='name',
                                required=True)

    mandatory_args.add_argument('-lock', '-l',
                                 help='"true" to lock bucket, "false" to unlock',
                                 metavar='<lock>',
                                 dest='lock',
                                 required=True)

    lock_bucket_parser.set_defaults(func=lock_bucket)

def lock_bucket(args):

    obj = Bucket(args.ip, args.port)

    try:
        obj.lock_bucket(args.name, args.lock)
    except SOSError as e:
        if(e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "Bucket retrieval failed: " + e.err_text)
        else:
            raise e


def update_owner_parser(subcommand_parsers, common_parser):
    # update-owner command parser
    update_owner_parser = subcommand_parsers.add_parser(
        'update-owner',
        description='ECS Update Bucket Owner CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='update bucket owner')

    mandatory_args = update_owner_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-name', '-n',
                                help='name of Bucket',
                                dest='name',
                                metavar='<name>',
                                required=True)

    mandatory_args.add_argument('-namespace', '-ns',
                                help='namespace allowed to access Bucket',
                                dest='namespace',
                                metavar='<namespace>',
                                required=True)

    mandatory_args.add_argument('-owner', '-o',
                                help='new object user owner for this bucket',
                                dest='owner',
                                metavar='<owner>',
                                required=True)

    update_owner_parser.set_defaults(func=update_owner)

def update_owner(args):

    obj = Bucket(args.ip, args.port)

    try:
        obj.update_owner(
            args.name,
            args.namespace,
            args.owner)
    except SOSError as e:
        raise e


def update_stale_parser(subcommand_parsers, common_parser):
    # update-stale command parser
    update_stale_parser = subcommand_parsers.add_parser(
        'update-stale',
        description='ECS Update Bucket isStaleAllowed CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='update isStaleAllowed flag')

    mandatory_args = update_stale_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-name', '-n',
                                help='name of Bucket',
                                dest='name',
                                metavar='<name>',
                                required=True)

    mandatory_args.add_argument('-stale_allowed', '-stale', '-sa',
                                help='tag to allow stale data in bucket',
                                dest='stale_allowed', metavar='<is_stale_allowed>',
                                required=True)

    update_stale_parser.add_argument('-namespace', '-ns',
                                     help='Namespace of Bucket',
                                     metavar='<namespace>',
                                     dest='namespace')

    update_stale_parser.set_defaults(func=update_stale)

def update_stale(args):

    obj = Bucket(args.ip, args.port)

    try:
        obj.update_stale(args.name, args.namespace, args.stale_allowed)
    except SOSError as e:
        raise e


def get_retention_period_parser(subcommand_parsers, common_parser):
    # get-retention command parser
    get_retention_period_parser = subcommand_parsers.add_parser(
        'get-ret-period',
        description='ECS Get Bucket Retention Period CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='get retention period')

    mandatory_args = get_retention_period_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-name', '-n',
                                help='name of Bucket',
                                dest='name',
                                metavar='<name>',
                                required=True)

    get_retention_period_parser.add_argument('-namespace', '-ns',
                             help='Namespace of Buckets',
                             metavar='<namespace>',
                             default=None,
                             dest='namespace')

    get_retention_period_parser.set_defaults(func=get_retention_period)

def get_retention_period(args):

    obj = Bucket(args.ip, args.port)

    try:
        return obj.get_retention_period(
            args.name, args.namespace)
    except SOSError as e:
        raise e


def update_retention_period_parser(subcommand_parsers, common_parser):
    # update-retention command parser
    update_retention_period_parser = subcommand_parsers.add_parser(
        'update-ret',
        description='ECS Update Bucket Retention Period CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='update retention period')

    mandatory_args = update_retention_period_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-name', '-n',
                                help='name of Bucket',
                                dest='name',
                                metavar='<name>',
                                required=True)

    mandatory_args.add_argument('-period', '-p',
                                help='default retention period in seconds',
                                dest='period',
                                metavar='<period>',
                                required=True)

    update_retention_period_parser.add_argument('-namespace', '-ns',
                             help='Namespace of Buckets',
                             metavar='<namespace>',
                             default=None,
                             dest='namespace')

    update_retention_period_parser.set_defaults(func=update_retention_period)

def update_retention_period(args):

    obj = Bucket(args.ip, args.port)

    try:
        return obj.update_retention_period( args.name, args.period, args.namespace)
    except SOSError as e:
        raise e


def get_quota_parser(subcommand_parsers, common_parser):
    # get-quota command parser
    get_quota_parser = subcommand_parsers.add_parser(
        'get-quota',
        description='ECS Get Bucket Quota CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='get bucket quota')

    mandatory_args = get_quota_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-name', '-n',
                                help='name of Bucket',
                                dest='name',
                                metavar='<name>',
                                required=True)

    get_quota_parser.add_argument('-namespace', '-ns',
                                 help='Namespace of Bucket',
                                 metavar='<namespace>',
                                 dest='namespace')

    get_quota_parser.set_defaults(func=get_quota)

def get_quota(args):

    obj = Bucket(args.ip, args.port)

    try:
        return obj.get_quota(args.name, args.namespace)
    except SOSError as e:
        raise e


def update_quota_parser(subcommand_parsers, common_parser):
    # update-quota command parser
    update_quota_parser = subcommand_parsers.add_parser(
        'update-quota',
        description='ECS Update Bucket Quota CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='update quota')

    mandatory_args = update_quota_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-name', '-n',
                                help='name of Bucket',
                                dest='name',
                                metavar='<name>',
                                required=True)

    update_quota_parser.add_argument('-block', '-blk',
                                               help='block size in GB',
                                               metavar='<block>',
                                               dest='block',
                                               required=True)

    update_quota_parser.add_argument('-notification', '-not',
                                               help='notification size in GB',
                                               metavar='<notification>',
                                               dest='notification',
                                               required=True)

    update_quota_parser.add_argument('-namespace', '-ns',
                                 help='Namespace of Bucket',
                                 metavar='<namespace>',
                                 dest='namespace')

    update_quota_parser.set_defaults(func=update_quota)

def update_quota(args):

    obj = Bucket(args.ip, args.port)

    try:
        return obj.update_quota(
            args.name,
            args.block,
            args.notification,
            args.namespace)
    except SOSError as e:
        raise e


def delete_quota_parser(subcommand_parsers, common_parser):
    # delete-quota command parser
    delete_quota_parser = subcommand_parsers.add_parser(
        'delete-quota',
        description='ECS Delete Bucket Quota CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='delete bucket quota')

    mandatory_args = delete_quota_parser.add_argument_group(
        'mandatory arguments')

    mandatory_args.add_argument('-name', '-n',
                                help='name of Bucket',
                                dest='name',
                                metavar='<name>',
                                required=True)

    delete_quota_parser.add_argument('-namespace', '-ns',
                                     help='Namespace of Bucket',
                                     metavar='<namespace>',
                                     dest='namespace')

    delete_quota_parser.set_defaults(func=delete_quota)

def delete_quota(args):

    obj = Bucket(args.ip, args.port)

    try:
        obj.delete_quota(args.name,
                         args.namespace)
    except SOSError as e:
        raise e


def get_acl_parser(subcommand_parsers, common_parser):
    # get-acl command parser
    get_acl_parser = subcommand_parsers.add_parser(
        'get-acl',
        description='ECS Get Bucket ACL CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='get bucket ACL')

    mandatory_args = get_acl_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-name', '-n',
                                help='name of Bucket',
                                dest='name',
                                metavar='<name>',
                                required=True)

    get_acl_parser.add_argument('-namespace', '-ns',
                                     help='Namespace of Bucket',
                                     metavar='<namespace>',
                                     dest='namespace')

    get_acl_parser.set_defaults(func=get_acl)

def get_acl(args):

    obj = Bucket(args.ip, args.port)

    try:
        return obj.get_acl( args.name, args.namespace)
    except SOSError as e:
        raise e


def set_acl_parser(subcommand_parsers, common_parser):
    # set-acl command parser
    set_acl_parser = subcommand_parsers.add_parser(
        'set-acl',
        description='ECS Set Bucket ACL CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='set bucket ACL')

    mandatory_args = set_acl_parser.add_argument_group(
        'mandatory arguments')

    mandatory_args.add_argument('-name', '-n',
                                help='name of Bucket',
                                dest='name',
                                metavar='<name>',
                                required=True)

    mandatory_args.add_argument('-configfile',
                                metavar='<configfile>',
                                help='config file for authentication provider',
                                dest='configfile',
                                required=True)

    set_acl_parser.add_argument('-namespace', '-ns',
                                help='Namespace of Bucket',
                                metavar='<namespace>',
                                dest='namespace')

    set_acl_parser.set_defaults(func=set_acl)


def get_attribute_value(config, sectioniter, attrname):

    try:
        val = config.get(sectioniter, attrname)
        if(val is ''):
            return None
        else:
            return val

    except SOSError as e:
        raise e

    except ConfigParser.NoOptionError as e:
        raise e

    except (ConfigParser.ParsingError, ConfigParser.Error) as e:
        raise e

def set_acl(args):

    obj = Bucket(args.ip, args.port)

    try:
        # read authentication provider  parameters from configuration file
        config = ConfigParser.RawConfigParser()
        try:
            inif = open(args.configfile, 'rb')
            config.readfp(inif)
        except IOERROR as e:
            print "Error: File does not appear to exist."
            raise e

        sectionslst = config.sections()

        if(len(sectionslst) == 0):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                "Authentication Provider configuration file is empty")

        owner = None
        user = None
        userpermission = None
        group = None 
        grouppermission = None

        customgroup = None
        customgrouppermission = None 
        permission = None

        for sectioniter in sectionslst:

            owner = get_attribute_value(config, sectioniter, 'owner')

            user = config.get(sectioniter, "user")
            userpermission = config.get(sectioniter, "userperm")
            group = config.get(sectioniter, 'group')
            grouppermission = config.get(sectioniter, 'groupperm')
            customgroup = config.get(sectioniter, 'customgroup')
            customgrouppermission = config.get(sectioniter, 'cgperm')

            if config.has_option(sectioniter, "permission"):
                #permission = get_attribute_value(config, sectioniter, 'permission')
                permission = config.get(sectioniter, "permission")

        return obj.set_acl(args.name, args.namespace, owner, user,
            userpermission, group, grouppermission, customgroup,
            customgrouppermission, permission)
    except SOSError as e:
        raise e


def get_permissions_parser(subcommand_parsers, common_parser):
    # get-permissions command parser
    get_permissions_parser = subcommand_parsers.add_parser(
        'get-permissions',
        description='ECS Get Bucket ACL Permissions CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='get bucket ACL permissions')

    get_permissions_parser.set_defaults(func=get_permissions)

def get_permissions(args):

    obj = Bucket(args.ip, args.port)

    try:
        return obj.get_permissions( )
    except SOSError as e:
        raise e


def get_groups_parser(subcommand_parsers, common_parser):
    # get-groups command parser
    get_groups_parser = subcommand_parsers.add_parser(
        'get-groups',
        description='ECS Get Bucket ACL Groups CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='get bucket ACL groups')

    get_groups_parser.set_defaults(func=get_groups)

def get_groups(args):

    obj = Bucket(args.ip, args.port)

    try:
        return obj.get_groups( )
    except SOSError as e:
        raise e



def update_tags_parser(subcommand_parsers, common_parser):
    # update-quota command parser
    update_tags_parser = subcommand_parsers.add_parser(
        'update-tags',
        description='ECS Update Bucket Tags CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='update tag key value pairs for a bucket')

    mandatory_args = update_tags_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-name', '-n',
                                help='name of Bucket',
                                dest='name',
                                metavar='<name>',
                                required=True)

    update_tags_parser.add_argument('-namespace', '-ns',
                                 help='Namespace of Bucket',
                                 metavar='<namespace>',
                                 dest='namespace',
                                 required=True)

    update_tags_parser.add_argument('-tagset','-ts',
                                help='List of one or more tagset tagname^tagvalue tuples ' +
                                     'eg list of tag^value',
                                metavar='<tagset>',
                                dest='tagset',
                                nargs='+')

    update_tags_parser.set_defaults(func=update_tags)


def update_tags(args):
    obj = Bucket(args.ip, args.port)

    try:
        add = False
        return obj.add_update_tags(args, add)
    except SOSError as e:
        raise e

def add_tags_parser(subcommand_parsers, common_parser):
    # update-quota command parser
    add_tags_parser = subcommand_parsers.add_parser(
        'add-tags',
        description='ECS Update Bucket Tags CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='add tag key value pairs for a bucket')

    mandatory_args = add_tags_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-name', '-n',
                                help='name of Bucket',
                                dest='name',
                                metavar='<name>',
                                required=True)

    add_tags_parser.add_argument('-namespace', '-ns',
                                 help='Namespace of Bucket',
                                 metavar='<namespace>',
                                 dest='namespace',
                                 required=True)

    add_tags_parser.add_argument('-tagset','-ts',
                                help='List of one or more tagset tagname^tagvalue tuples ' +
                                     'eg list of tag^value',
                                metavar='<tagset>',
                                dest='tagset',
                                nargs='+')

    add_tags_parser.set_defaults(func=add_tags)


def add_tags(args):
    obj = Bucket(args.ip, args.port)

    try:
        add = True
        return obj.add_update_tags(args, add)
    except SOSError as e:
        raise e


def delete_tags_parser(subcommand_parsers, common_parser):
    # update-quota command parser
    delete_tags_parser = subcommand_parsers.add_parser(
        'delete-tags',
        description='ECS Delete Bucket Tags CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='delete specific tag key value pairs for a bucket')

    mandatory_args = delete_tags_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-name', '-n',
                                help='name of Bucket',
                                dest='name',
                                metavar='<name>',
                                required=True)

    delete_tags_parser.add_argument('-namespace', '-ns',
                                 help='Namespace of Bucket',
                                 metavar='<namespace>',
                                 dest='namespace',
                                 required=True)

    delete_tags_parser.add_argument('-tagset','-ts',
                                help='List of one or more tagset tagname^tagvalue tuples ' +
                                     'eg list of tag^value',
                                metavar='<tagset>',
                                dest='tagset',
                                nargs='+')

    delete_tags_parser.set_defaults(func=delete_tags)


def delete_tags(args):
    obj = Bucket(args.ip, args.port)

    try:
        return obj.delete_tags(args)
    except SOSError as e:
        raise e


def get_metadata_parser(subcommand_parsers, common_parser):
    # create command parser
    meta_parser = subcommand_parsers.add_parser(
        'get-metadata',
        description='ECS Bucket Metadata CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='create bucket')

    mandatory_args = meta_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-name', '-n',
                                help='Name of Bucket',
                                metavar='<bucketname>',
                                dest='name',
                                required=True)

    mandatory_args.add_argument('-headtype', '-ht',
                                help='object head type allowed to access bucket',
                                dest='headtype', metavar='<head_type>', 
                                required=True)

    mandatory_args.add_argument('-namespace', '-ns',
                                help='namespace associated with bucket user/tenant',
                                dest='namespace', metavar='<namespace>',
                                required=True)

    meta_parser.set_defaults(func=bucket_get_meta)

def bucket_get_meta(args):
    obj = Bucket(args.ip, args.port)
    try:
        return obj.get_meta(args)
    except SOSError as e:
        raise e

def set_metadata_parser(subcommand_parsers, common_parser):
    # create command parser
    set_metadata_parser = subcommand_parsers.add_parser(
        'set-metadata',
        description='ECS Bucket Metadata CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='create bucket')

    mandatory_args = set_metadata_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-name', '-n',
                                help='Name of Bucket',
                                metavar='<bucketname>',
                                dest='name',
                                required=True)

    mandatory_args.add_argument('-headtype', '-ht',
                                help='object head type allowed to access bucket',
                                dest='headtype', metavar='<head_type>',
                                required=True)

    mandatory_args.add_argument('-namespace', '-ns',
                                help='namespace associated with bucket user/tenant',
                                dest='namespace', metavar='<namespace>',
                                default=None, required=True)

    set_metadata_parser.add_argument('-metaset','-ms',
                                help='List of one or more metadata metaname^metavalue tuples ' +
                                     'eg list of name^value',
                                metavar='<metadata>',
                                dest='metaset',
                                nargs='+')
    set_metadata_parser.set_defaults(func=bucket_set_meta)

def bucket_set_meta(args):
    obj = Bucket(args.ip, args.port)
    try:
        return obj.set_meta(args)
    except SOSError as e:
        raise e

def delete_metadata_parser(subcommand_parsers, common_parser):
    # create command parser
    meta_parser = subcommand_parsers.add_parser(
        'delete-metadata',
        description='ECS Bucket Metadata CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='create bucket')

    mandatory_args = meta_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-name', '-n',
                                help='Name of Bucket',
                                metavar='<bucketname>',
                                dest='name',
                                required=True)

    mandatory_args.add_argument('-headtype', '-ht',
                                help='object head type allowed to access bucket',
                                dest='headtype', metavar='<head_type>',
                                required=True)

    mandatory_args.add_argument('-namespace', '-ns',
                                help='namespace associated with bucket user/tenant',
                                dest='namespace', metavar='<namespace>',
                                default=None, required=True)

    meta_parser.set_defaults(func=bucket_delete_meta)

def bucket_delete_meta(args):
    obj = Bucket(args.ip, args.port)
    try:
        return obj.delete_meta(args)
    except SOSError as e:
        raise e

def get_searchmetadata_parser(subcommand_parsers, common_parser):
    # create command parser
    meta_parser = subcommand_parsers.add_parser(
        'list-searchmetadata',
        description='ECS Bucket Metadata CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='create bucket')

    meta_parser.set_defaults(func=list_searchmeta)

def list_searchmeta(args):
    obj = Bucket(args.ip, args.port)
    try:
        return obj.list_search_meta(args)
    except SOSError as e:
        raise e

def delete_searchmetadata_parser(subcommand_parsers, common_parser):
    # create command parser
    meta_parser = subcommand_parsers.add_parser(
        'deactivate-searchmetadata',
        description='ECS Bucket SearchMetadata deactivation for a specific bucket.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='create bucket')

    mandatory_args = meta_parser.add_argument_group('mandatory arguments')
                               
    mandatory_args.add_argument('-name', '-n',
                                help='Name of Bucket',
                                metavar='<bucketname>',
                                dest='name',
                                required=True)


    meta_parser.add_argument('-namespace', '-ns',
                             help='Namespace of bucket being for which searchmetadata is being deactivated if it is not in the namespace where current user is admin',
                             metavar='<namespace>',
                             default=None,
                             dest='namespace')

    meta_parser.set_defaults(func=delete_searchmeta)

def delete_searchmeta(args):
    obj = Bucket(args.ip, args.port)
    try:
        return obj.del_search_meta(args)
    except SOSError as e:
        raise e


def bucket_parser(parent_subparser, common_parser):
    # main bucket parser
    parser = parent_subparser.add_parser('bucket',
                                         description='ECS Bucket CLI usage',
                                         parents=[common_parser],
                                         conflict_handler='resolve',
                                         help='Operations on Bucket')
    subcommand_parsers = parser.add_subparsers(help='Use One Of Commands')

    # create command parser
    create_parser(subcommand_parsers, common_parser)

    # delete command parser
    delete_parser(subcommand_parsers, common_parser)

    # list command parser
    list_parser(subcommand_parsers, common_parser)

    # get bucket info parser
    get_info_parser(subcommand_parsers, common_parser)

    # get bucket lock info parser
    get_lock_parser(subcommand_parsers, common_parser)

    # luck/unlock bucket parser
    lock_bucket_parser(subcommand_parsers, common_parser)

    # update owner parser
    update_owner_parser(subcommand_parsers, common_parser)

    # update isStaleAllowed parser
    update_stale_parser(subcommand_parsers, common_parser)

    # get retention period parser
    get_retention_period_parser(subcommand_parsers, common_parser)

    # update retention period parser
    update_retention_period_parser(subcommand_parsers, common_parser)

    # get bucket quota parser
    get_quota_parser(subcommand_parsers, common_parser)

    # update bucket quota parser
    update_quota_parser(subcommand_parsers, common_parser)

    # delete bucket quota parser
    delete_quota_parser(subcommand_parsers, common_parser)

    # get bucket acl acl parser
    get_acl_parser(subcommand_parsers, common_parser)

    # set bucket acl parser
    set_acl_parser(subcommand_parsers, common_parser)

    # get bucket acl permissions parser
    get_permissions_parser(subcommand_parsers, common_parser)

    # get bucket acl groups parser
    get_groups_parser(subcommand_parsers, common_parser)

    update_tags_parser(subcommand_parsers, common_parser)

    add_tags_parser(subcommand_parsers, common_parser)

    delete_tags_parser(subcommand_parsers, common_parser)

    get_metadata_parser(subcommand_parsers, common_parser)

    set_metadata_parser(subcommand_parsers, common_parser)

    delete_metadata_parser(subcommand_parsers, common_parser)

    get_searchmetadata_parser(subcommand_parsers, common_parser)

    delete_searchmetadata_parser(subcommand_parsers, common_parser)

