#!/usr/bin/python
# Copyright (c)2012 EMC Corporation
# All Rights Reserved

# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

import json
import common

from common import SOSError


class Objectuser(object):

    '''
    The class definition for operations on 'Objectuser'.
    '''

    # Commonly used URIs for the 'objectuser' module

    URI_SERVICES_BASE = ''
    URI_WEBSTORAGE_USER = URI_SERVICES_BASE + '/object/users'
    URI_WEBSTORAGE_USER_DEACTIVATE = URI_WEBSTORAGE_USER + '/deactivate'
    URI_WEBSTORAGE_USER_INFO = URI_WEBSTORAGE_USER + '/{0}/info'
    URI_WEBSTORAGE_USER_NS_INFO = URI_WEBSTORAGE_USER + '/{0}'
    URI_WEBSTORAGE_USER_LOCK = URI_WEBSTORAGE_USER + '/lock'
    URI_WEBSTORAGE_USER_LOCK_INSTANCE = URI_WEBSTORAGE_USER_LOCK + '/{0}'


    def __init__(self, ipAddr, port, output_format = None):
        '''
        Constructor: takes IP address and port of the ECS instance. These are
        needed to make http requests for REST API
        '''
        self.__ipAddr = ipAddr
        self.__port = port
        self.__format = "json"
        if (output_format == 'xml'):
           self.__format = "xml"


    def objectuser_list(self, uid=None, namespace=None):
        '''
        Gets details for the specified user identifier and namespace.

        If no user identifier is provided, gets all identifiers for
        the given namespace.

        If neither user identifier nor namespace is provided, gets
        identifiers for all configured users.
        '''

        # info on single user
        if (uid is not None and namespace is not None):
            uri = Objectuser.URI_WEBSTORAGE_USER_INFO.format(uid) \
                  + "?namespace=" + namespace

        # info on all users in namespace
        elif (uid is None and namespace is not None):
            uri = Objectuser.URI_WEBSTORAGE_USER_NS_INFO.format(namespace)

        # info on all users
        else:
            uri = Objectuser.URI_WEBSTORAGE_USER

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                                             uri, None, None, xml)
        if(self.__format == "json"):
            o = common.json_decode(s)
            return o
        return s


    def objectuser_query(self, uid, namespace=None):
        '''
        Gets user from UID.
        '''
        users = self.objectuser_list(None, namespace)

        for user in users['blobuser']:
            if( (user['userid'] == uid) and 
               ( (namespace is None) or (user['namespace'] == namespace) ) ):
                return user

        err_str = "Object user query failed: object user with name " + \
                   uid + " not found"

        if(namespace is not None):
            err_str = err_str + " with namespace "+namespace

        raise SOSError(SOSError.NOT_FOUND_ERR, err_str)


    def objectuser_create(self, uid, namespace, tag):
        '''
        Create user with the given details, which can
        subsequently be used to create its secret key.
        '''

        # users = self.objectuser_list(namespace)
        # for user in users:
        #     if(user == uid):
        #         raise SOSError(SOSError.ENTRY_ALREADY_EXISTS_ERR,
        #                        "Objectuser  create failed: object user " +
        #                        "with same name already exists")

        tags = []
        if (tag):
            for t in tag:
                tags.append(t)

        parms = {
            'user': uid,
            'namespace': namespace,
            'tags': tags
        }

        body = json.dumps(parms)

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "POST",
                                             Objectuser.URI_WEBSTORAGE_USER, body, None, xml)

        if(self.__format == "json"):
            o = common.json_decode(s)
            return common.format_json_object(o)
        return s


    def objectuser_delete(self, uid, namespace):
        '''
        Deletes user and all its associated
        secret keys for the specified user details.
        '''

        # Return value is irrelevant - used to ensure user exists.
        #userval = self.objectuser_query(uid, namespace)

        parms = {
            'user': uid,
            'namespace': namespace
        }

        body = json.dumps(parms)

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "POST",
                                             self.URI_WEBSTORAGE_USER_DEACTIVATE,
                                             body, None, xml)

        if(self.__format == "json"):
            o = common.json_decode(s)
            return common.format_json_object(o)
        return s


    def objectuser_lock(self, uid, namespace):
        return self.objectuser_locker(uid, namespace, 'true')


    def objectuser_unlock(self, uid, namespace):
        return self.objectuser_locker(uid, namespace, 'false')


    def objectuser_locker(self, uid, namespace, locked):
        '''
        Locks or unlocks specified user.
        '''

        # Return value is irrelevant - used to ensure user exists.
        #userval = self.objectuser_query(uid, namespace)

        parms = {
            'user': uid,
            'namespace': namespace,
            'isLocked': locked
        }

        body = json.dumps(parms)

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "PUT",
                                             self.URI_WEBSTORAGE_USER_LOCK,
                                             body, None, xml)

        return 


    def objectuser_getlock(self, uid, namespace=None):
        '''
        Gets the user lock details for the specified user name.
        '''

        uri = Objectuser.URI_WEBSTORAGE_USER_LOCK_INSTANCE.format(uid)

        if(namespace is not None):
            uri = uri + '/' + namespace

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                                             uri, None, None, xml)

        if(self.__format == "json"):
            o = common.json_decode(s)
            return common.format_json_object(o)
        return s


def create_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'create',
        description='ECS Objectuser Create CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Create an objectuser')

    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-uid',
                                help='User identifier',
                                metavar='<uid>',
                                dest='uid',
                                required=True)


    mandatory_args.add_argument('-namespace', '-ns',
                                help='Namespace for user.',
                                default=None,
                                dest='namespace',
                                required=True)

    create_parser.add_argument('-tag', '-tag',
                                help='Space-delimited list of tags associated with user',
                                nargs='*',
                                dest='tags',
                                default=None)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=objectuser_create)

def objectuser_create(args):

    obj = Objectuser(args.ip, args.port, args.format)

    try:
        res = obj.objectuser_create(args.uid, args.namespace, args.tags)
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": Add user failed\n" + e.err_text)
        else:
            raise e


def delete_parser(subcommand_parsers, common_parser):
    # delete command parser
    delete_parser = subcommand_parsers.add_parser(
        'delete',
        description='ECS Objectuser Delete CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Delete an objectuser')

    mandatory_args = delete_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-uid',
                                help='User identifer',
                                metavar='<uid>',
                                dest='uid',
                                required=True)

    mandatory_args.add_argument('-namespace', '-ns',
                                help='Namespace for user.',
                                default=None,
                                metavar='<namespace>',
                                dest='namespace',
                                required=True)

    delete_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    delete_parser.set_defaults(func=objectuser_delete)

def objectuser_delete(args):

    obj = Objectuser(args.ip, args.port, args.format)

    try:
        res = obj.objectuser_delete(args.uid, args.namespace)
        return res
    except SOSError as e:
        if(e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "Objectuser delete failed: " + e.err_text)
        else:
            raise e


def list_parser(subcommand_parsers, common_parser):
    # list command parser
    list_parser = subcommand_parsers.add_parser(
        'list',
        description='ECS Objectuser List CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Show Objectuser(s)')

    list_parser.add_argument('-uid', '-uid',
                             help='User identifier. Required if scope is USER.',
                             default=None,
                             metavar='<uid>',
                             dest='uid')

    list_parser.add_argument('-namespace', '-ns',
                            help='Namespace for user. Required if scope is USER or NAMESPACE',
                            default=None,
                            metavar='<namespace>',
                            dest='namespace')

    list_parser.add_argument('-format', '-f',
                            metavar='<format>', dest='format',
                            help='response format: xml or json (default:json)',
                            choices=['xml', 'json'],
                            default="json")

    list_parser.set_defaults(func=objectuser_list)

def objectuser_list(args):
    obj = Objectuser(args.ip, args.port, args.format)
    try:
        res = obj.objectuser_list(args.uid, args.namespace)
        '''
        # COMMENT PRE-04/18/2015
        #this is a pretty print output when a json object is received
        #it should probably be in its own function as it's not even for xml type results
        #I'm not sure that formatting is desired either
        res = res['blobuser']
        output = []

        for iter in res:
            tmp = dict()
            tmp['userid'] = iter['userid']
            tmp['namespace'] = iter['namespace']
            output.append(tmp)

        if(res):
            from common import TableGenerator
            TableGenerator(output, ['userid', 'namespace']).printTable()
        '''
        return res
    except SOSError as e:
        if(e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "Objectuser list failed: " + e.err_text)
        else:
            raise e


def lock_parser(subcommand_parsers, common_parser):
    # lock command parser
    lock_parser = subcommand_parsers.add_parser(
        'lock',
        description='ECS Objectuser Lock CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Lock an objectuser')

    mandatory_args = lock_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-uid',
                                help='User identifier',
                                metavar='<uid>',
                                dest='uid',
                                required=True)

    mandatory_args.add_argument('-namespace', '-ns',
                                help='namespace',
                                metavar='<namespace>',
                                dest='namespace',
                                required=True)

    lock_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    lock_parser.set_defaults(func=objectuser_lock)

def objectuser_lock(args):

    obj = Objectuser(args.ip, args.port, args.format)

    try:
        res = obj.objectuser_lock(args.uid, args.namespace)
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": Add user lock failed\n" + e.err_text)
        else:
            raise e


def unlock_parser(subcommand_parsers, common_parser):
    # add command parser
    unlock_parser = subcommand_parsers.add_parser(
        'unlock',
        description='ECS Objectuser unlock CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='unlock on an object user')

    mandatory_args = unlock_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-uid',
                                help='UID',
                                metavar='<uid>',
                                dest='uid',
                                required=True)

    mandatory_args.add_argument('-namespace', '-ns',
                                help='namespace',
                                metavar='<namespace>',
                                dest='namespace',
                                required=True)

    unlock_parser.add_argument('-format', '-f',
                               metavar='<format>', dest='format',
                               help='response format: xml or json (default:json)',
                               choices=['xml', 'json'],
                               default="json")

    unlock_parser.set_defaults(func=objectuser_unlock)

def objectuser_unlock(args):
    obj = Objectuser(args.ip, args.port, args.format)
    try:
        res = obj.objectuser_unlock(args.uid, args.namespace)
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": user unlock failed\n" + e.err_text)
        else:
            raise e


def getlock_parser(subcommand_parsers, common_parser):
    # get-lock command parser
    getlock_parser = subcommand_parsers.add_parser(
        'get-lock',
        description='ECS Objectuser get lock info CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Show the lock for an Objectuser')

    mandatory_args = getlock_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-uid',
                                help='User identifier',
                                metavar='<uid>',
                                dest='uid',
                                required=True)

    getlock_parser.add_argument('-namespace', '-ns',
                                help='Namespace identifier for user',
                                default=None,
                                metavar='<namespace>',
                                dest='namespace')

    getlock_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    getlock_parser.set_defaults(func=objectuser_getlock)

def objectuser_getlock(args):

    obj = Objectuser(args.ip, args.port, args.format)

    try:
        res = obj.objectuser_getlock(args.uid, args.namespace)
        return res
    except SOSError as e:
        if(e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "Objectuser delete failed: " + e.err_text)
        else:
            raise e


# Objectuser Main parser routine
def objectuser_parser(parent_subparser, common_parser):
    # main objectuser parser
    parser = parent_subparser.add_parser(
        'objectuser',
        description='ECS Objectuser CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Operations on Objectuser')
    subcommand_parsers = parser.add_subparsers(help='Use One Of Commands')

    # create command parser
    create_parser(subcommand_parsers, common_parser)

    # delete command parser
    delete_parser(subcommand_parsers, common_parser)

    # list command parser
    list_parser(subcommand_parsers, common_parser)

    # lock command parser
    lock_parser(subcommand_parsers, common_parser)

    # get-lock command parser
    getlock_parser(subcommand_parsers, common_parser)

    # unlock command parser
    unlock_parser(subcommand_parsers, common_parser)
