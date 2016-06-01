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


class Passwordgroup(object):

    '''
    The class definition for operations on 'Passwordgroup'.
    '''

    # Commonly used URIs for the 'passwordgroup' module

    URI_SERVICES_BASE = ''
    URI_USERPASS_BASE = URI_SERVICES_BASE + '/object/user-password'
    URI_USERPASS_INSTANCE = URI_USERPASS_BASE + '/{0}'
    URI_USERPASS_INSTANCE_NS = URI_USERPASS_INSTANCE + '/{1}'
    URI_USERPASS_DELETE = URI_USERPASS_INSTANCE + '/deactivate'


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


    def passwordgroup_list(self, uid, namespace):
        '''
        Gets all user groups for a specified user identifier
        (and namespace if provided).
        '''

        if(namespace is not None):
            uri = Passwordgroup.URI_USERPASS_INSTANCE_NS.format(uid, namespace)
        else:
            uri = Passwordgroup.URI_USERPASS_INSTANCE.format(uid)

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                                             uri, None)
        if(self.__format == "json"):
            o = common.json_decode(s)
            return o
        return s


    def passwordgroup_create(self, uid, namespace, password, groups_list):
        '''
        Creates user, password, group info for a specific user.
        '''

        parms = {
            'password': password,
            'groups_list': groups_list,
            'namespace': namespace
        }
        body = json.dumps(parms)

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, 'PUT',
                                             Passwordgroup.URI_USERPASS_INSTANCE.format(uid),
                                             body, None, xml)

        return

    def passwordgroup_update(self, uid, namespace, password, groups_list):
        '''
        Updates user, password, group info for a specific user identifier.
        '''

        parms = {
            'password': password,
            'groups_list': groups_list,
            'namespace': namespace
        }
        body = json.dumps(parms)

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, 'POST',
                                             Passwordgroup.URI_USERPASS_INSTANCE.format(uid),
                                             body, None, xml)

        return

    def passwordgroup_delete(self, uid, namespace):
        '''
        Deletes password group for a specified user.
        '''

        parms = { 'namespace': namespace }

        body = json.dumps(parms)

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "POST",
                                             Passwordgroup.URI_USERPASS_DELETE.format(uid),
                                             body, None, xml)

        return

def create_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'create',
        description='ECS Passwordgroup Create CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Create a passwordgroup')

    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-uid',
                                help='User identifer',
                                metavar='<uid>',
                                dest='uid',
                                required=True)

    mandatory_args.add_argument('-namespace', '-ns',
                                help='namespace of object stores',
                                dest='namespace',
                                required=True)

    mandatory_args.add_argument('-password', '-pw',
                                help='password for user',
                                dest='password',
                                required=True)

    mandatory_args.add_argument('-groups_list', '-gl',
                                help='space-delimited groups list',
                                nargs='*',
                                dest='groups_list',
                                required=True)

    create_parser.set_defaults(func=passwordgroup_create)

def passwordgroup_create(args):

    obj = Passwordgroup(args.ip, args.port)

    try:
        obj.passwordgroup_create(args.uid, args.namespace, args.password, args.groups_list)
        return
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Passwordgroup " +
                           args.uid + ": Create user failed\n" + e.err_text)
        else:
            raise e


def update_parser(subcommand_parsers, common_parser):
    # update command parser
    update_parser = subcommand_parsers.add_parser(
        'update',
        description='ECS Passwordgroup Update CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Update a passwordgroup')

    mandatory_args = update_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-uid',
                                help='User identifer',
                                metavar='<uid>',
                                dest='uid',
                                required=True)

    mandatory_args.add_argument('-namespace', '-ns',
                                help='namespace of object stores',
                                dest='namespace',
                                required=True)

    mandatory_args.add_argument('-password', '-pw',
                                help='password for user',
                                dest='password',
                                required=True)

    mandatory_args.add_argument('-groups_list', '-gl',
                                help='space-delimited groups list',
                                nargs='*',
                                dest='groups_list',
                                required=True)

    update_parser.set_defaults(func=passwordgroup_update)

def passwordgroup_update(args):
    obj = Passwordgroup(args.ip, args.port)
    try:
        obj.passwordgroup_update(args.uid, args.namespace, args.password, args.groups_list)
        return
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Passwordgroup " +
                           args.uid + ": Update user failed\n" + e.err_text)
        else:
            raise e


def delete_parser(subcommand_parsers, common_parser):
    # delete command parser
    delete_parser = subcommand_parsers.add_parser(
        'delete',
        description='ECS Passwordgroup delete CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Delete a passwordgroup')

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
                                dest='namespace')

    delete_parser.set_defaults(func=passwordgroup_delete)

def passwordgroup_delete(args):

    obj = Passwordgroup(args.ip, args.port)

    try:
        obj.passwordgroup_delete(args.uid, args.namespace)
        return
    except SOSError as e:
        if(e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "Passwordgroup delete failed: " + e.err_text)
        else:
            raise e


def list_parser(subcommand_parsers, common_parser):
    # list command parser
    list_parser = subcommand_parsers.add_parser(
        'list',
        description='ECS Passwordgroup List CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Show Passwordgroup(s)')

    mandatory_args = list_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-uid',
                                help='User identifer',
                                metavar='<uid>',
                                dest='uid',
                                required=True)

    list_parser.add_argument('-namespace', '-ns',
                             help='Namespace for user. Required if scope is NAMESPACE',
                             default=None,
                             dest='namespace')

    list_parser.add_argument('-format', '-f',
                            metavar='<format>', dest='format',
                            help='response format: xml or json (default:json)',
                            choices=['xml', 'json'],
                            default="json")

    list_parser.set_defaults(func=passwordgroup_list)

def passwordgroup_list(args):

    obj = Passwordgroup(args.ip, args.port, args.format)

    try:
        res = obj.passwordgroup_list(args.uid, args.namespace)
        return res
    except SOSError as e:
        if(e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "Passwordgroup list failed: " + e.err_text)
        else:
            raise e


# Passwordgroup Main parser routine
def passwordgroup_parser(parent_subparser, common_parser):
    # main passwordgroup parser
    parser = parent_subparser.add_parser(
        'passwordgroup',
        description='ECS Passwordgroup CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Operations on Passwordgroup')
    subcommand_parsers = parser.add_subparsers(help='Use One Of Commands')

    # create command parser
    create_parser(subcommand_parsers, common_parser)

    # update command parser
    update_parser(subcommand_parsers, common_parser)

    # delete command parser
    delete_parser(subcommand_parsers, common_parser)

    # list command parser
    list_parser(subcommand_parsers, common_parser)

