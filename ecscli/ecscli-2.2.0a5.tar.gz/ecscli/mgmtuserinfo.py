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


class Mgmtuserinfo(object):

    '''
    The class definition for operations on 'Mgmtuserinfo'.
    '''

    # Commonly used URIs for the 'mgmtuserinfo' module

    URI_SERVICES_BASE = ''

    URI_WEBSTORAGE_USER = URI_SERVICES_BASE + '/vdc/users'

    def __init__(self, ipAddr, port, output_format):
        '''
        Constructor: takes IP address and port of the ECS instance. These are
        needed to make http requests for REST API
        '''
        self.__ipAddr = ipAddr
        self.__port = port
        self.__format = "json"
        if (output_format == "xml" ):
            self.__format = output_format

    
    def mgmtuserinfo_list(self, userId=None):
        '''
        Makes a REST API call to retrieve details of a mgmtuserinfo
        based on its UUID
        '''
        uri = self.URI_WEBSTORAGE_USER 

        if (userId):
            uri += "/" + userId

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr,
                                             self.__port, "GET",
                                             uri,
                                             None, None, xml)

        if (self.__format == "json"):
            o = common.json_decode(s)
            return o

        return s


    def mgmtuserinfo_query(self, uid, namespace=None):
        users = self.mgmtuserinfo_list()

        for user in users:
            if( (user['userid'] == uid) and 
               ( (namespace is None) or (user['namespace'] == namespace) ) ):
                return user

        err_str = "Object user query failed: object user with name " + \
                   uid + " not found"

        if(namespace is not None):
            err_str = err_str + " with namespace "+namespace

        raise SOSError(SOSError.NOT_FOUND_ERR, err_str)
                     

    def mgmtuserinfo_add(self, uid, password, isSystemAdmin, isSystemMonitor, isExternalGroup):
        uri = self.URI_WEBSTORAGE_USER
        users = self.mgmtuserinfo_list()
        for user in users:
            if(user == uid):
                raise SOSError(SOSError.ENTRY_ALREADY_EXISTS_ERR,
                               "Mgmtuserinfo  create failed: object user " +
                               "with same name already exists")

        parms = {
            'userId': uid,
            'password': password,
            'isSystemAdmin': isSystemAdmin,
            'isSystemMonitor': isSystemMonitor,
            'is_external_group': isExternalGroup
        }
        body = None
        if (parms):
            body = json.dumps(parms)

        (s, h) = common.service_json_request(self.__ipAddr,
                                             self.__port, "POST",
                                             uri, body)
        o = common.json_decode(s)
        return o


    def mgmtuserinfo_update(self, uid, password, isSystemAdmin, isSystemMonitor):
        uri = self.URI_WEBSTORAGE_USER + "/" + uid
        parms = {
            'password': password,
            'isSystemAdmin': isSystemAdmin,
            'isSystemMonitor': isSystemMonitor
        }
        body = None
        if (parms):
            body = json.dumps(parms)

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr,
                                             self.__port, "PUT",
                                             uri, body, None, xml)
        return 


    def mgmtuserinfo_delete(self, uid):
        '''
        Makes a REST API call to delete a mgmtuserinfo by its UUID
        '''
        uri = self.URI_WEBSTORAGE_USER + "/" + uid + '/deactivate'

        #JMC query might need fixing because of the namespace, but it's not required. the server will reject if it's a bad uid
        #userval = self.mgmtuserinfo_query(uid, namespace)

        body = None
        (s, h) = common.service_json_request(self.__ipAddr,
                                             self.__port, "POST",
                                             uri,
                                             body)

        return str(s) + " ++ " + str(h)


def add_parser(subcommand_parsers, common_parser):
    # add command parser
    add_parser = subcommand_parsers.add_parser(
        'add',
        description='ECS Mgmtuserinfo Create CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Create an mgmtuserinfo')

    mandatory_args = add_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-uid',
                                help='UID',
                                metavar='<uid>',
                                dest='uid',
                                required=True)

    '''
    mandatory_args.add_argument('-namespace', '-ns',
                                help='namespace',
                                metavar='<namespace>',
                                dest='namespace',
                                required=True)
    '''
    mandatory_args.add_argument('-password',
                                help='user password',
                                metavar='<password>',
                                dest='password',
                                required=True)

    add_parser.add_argument('-isSystemAdmin',
                                help='boolean if true, assigns the user to a system admin role',
                                dest='isSystemAdmin',
                                choices=['true', 'false'],
                                default='true')

    add_parser.add_argument('-isSystemMonitor',
                                help='assigns mgmt user to the system monitor role',
                                dest='isSystemMonitor',
                                choices=['true', 'false'],
                                default='false')

    add_parser.add_argument('-isExternalGroup',
                                help='If set to true, its a domain',
                                dest='isExternalGroup',
                                choices=['true', 'false'],
                                default='false')

    add_parser.set_defaults(func=mgmtuserinfo_add)


def mgmtuserinfo_add(args):
    obj = Mgmtuserinfo(args.ip, args.port, args.format)

    try:
        res = obj.mgmtuserinfo_add(args.uid, args.password, args.isSystemAdmin, args.isSystemMonitor, args.isExternalGroup)

    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Mgmtuserinfo " +
                           args.uid + ": Add user failed\n" + e.err_text)
        else:
            raise e


# NEIGHBORHOOD Delete routines

def delete_parser(subcommand_parsers, common_parser):
    # delete command parser
    delete_parser = subcommand_parsers.add_parser(
        'delete',
        description='ECS Mgmtuserinfo delete CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Delete an mgmtuserinfo')

    mandatory_args = delete_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-uid',
                                help='UID',
                                metavar='<uid>',
                                dest='uid',
                                required=True)

    delete_parser.set_defaults(func=mgmtuserinfo_delete)


def mgmtuserinfo_delete(args):
    obj = Mgmtuserinfo(args.ip, args.port, args.format)

    try:
        res = obj.mgmtuserinfo_delete(args.uid)
    except SOSError as e:
        if(e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "Mgmtuserinfo delete failed: " + e.err_text)
        else:
            raise e

# NEIGHBORHOOD Show routines


def list_parser(subcommand_parsers, common_parser):
    # list command parser
    list_parser = subcommand_parsers.add_parser(
        'list',
        description='ECS Mgmtuserinfo List CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Show an Mgmtuserinfo')

    list_parser.add_argument('-userId', 
                            help='for detailed information pertaining to specific userId',
                            default=None,
                            metavar='<userId>',
                            dest='userId')


    list_parser.set_defaults(func=mgmtuserinfo_list)


def mgmtuserinfo_list(args):
    obj = Mgmtuserinfo(args.ip, args.port, args.format)

    try:
        res = obj.mgmtuserinfo_list(args.userId)

    except SOSError as e:
        if(e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "Mgmtuserinfo list failed: " + e.err_text)
        else:
            raise e

    return res

def update_parser(subcommand_parsers, common_parser):
    # delete command parser
    update_parser = subcommand_parsers.add_parser(
        'update',
        description='ECS Mgmtuserinfo update CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='updates a mgmt user')

    mandatory_args = update_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-uid',
                                help='UID',
                                metavar='<uid>',
                                dest='uid',
                                required=True)

    mandatory_args.add_argument('-password',
                                help='user password',
                                metavar='<password>',
                                dest='password',
                                required=True)

    update_parser.add_argument('-isSystemAdmin',
                                help='boolean if true, assigns the user to a system admin role',
                                dest='isSystemAdmin',
                                choices=['true', 'false'],
                                default='true')

    update_parser.add_argument('-isSystemMonitor',
                                help='assigns mgmt user to the system monitor role',
                                dest='isSystemMonitor',
                                choices=['true', 'false'],
                                default='false')


    update_parser.set_defaults(func=mgmtuserinfo_update)


def mgmtuserinfo_update(args):
    obj = Mgmtuserinfo(args.ip, args.port, args.format)

    try:
        res = obj.mgmtuserinfo_update(args.uid, args.password, args.isSystemAdmin, args.isSystemMonitor)
    except SOSError as e:
        if(e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "Mgmtuserinfo delete failed: " + e.err_text)
        else:
            raise e


#
# Mgmtuserinfo Main parser routine
#
def mgmtuserinfo_parser(parent_subparser, common_parser):
    # main mgmtuserinfo parser
    parser = parent_subparser.add_parser(
        'mgmtuserinfo',
        description='ECS Mgmtuserinfo CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Operations on Mgmtuserinfo')

    parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    subcommand_parsers = parser.add_subparsers(help='Use One Of Commands')

    # add command parser
    add_parser(subcommand_parsers, common_parser)

    # delete command parser
    delete_parser(subcommand_parsers, common_parser)

    # list command parser
    list_parser(subcommand_parsers, common_parser)

    update_parser(subcommand_parsers, common_parser)

