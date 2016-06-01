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


class Secretkeyuser(object):

    '''
    The class definition for operations on 'Secretkeyuser'.
    '''

    # Commonly used URIs for the 'secretkeyuser' module

    URI_SERVICES_BASE = ''
    URI_SECRET_KEY = URI_SERVICES_BASE + '/object/secret-keys'
    URI_SECRET_KEY_USER = URI_SERVICES_BASE + '/object/user-secret-keys/{0}'
    URI_SECRET_KEY_USER_NS = URI_SERVICES_BASE + '/object/user-secret-keys/{0}/{1}'
    URI_DELETE_SECRET_KEY_USER = \
        URI_SERVICES_BASE + '/object/user-secret-keys/{0}/deactivate'
    URI_DELETE_SECRET_KEY = '/object/secret-keys/deactivate'


    def __init__(self, ipAddr, port):
        '''
        Constructor: takes IP address and port of the ECS instance. These are
        needed to make http requests for REST API
        '''
        self.__ipAddr = ipAddr
        self.__port = port


    def secretkey_show(self, uid, namespace):
        '''
        Gets all secret keys for the specific user identifier.
        If namespace is specified, gets all secret keys in NAMSPACE scope.
        '''

        if(namespace != None):
            uri = self.URI_SECRET_KEY_USER_NS.format(uid, namespace)
        else:
            uri = self.URI_SECRET_KEY_USER.format(uid)

        (s, h) = common.service_json_request(self.__ipAddr,
                                             self.__port, "GET",
                                             uri, None)
        o = common.json_decode(s)

        return o


    def secretkey_add(self, uid, namespace, expiry, secretkey):
        '''
        Creates a secret key with the given details for the specific user identifier.
        '''

        # Checks if UID/namespace params are valid
        from objectuser import Objectuser
        objObjUser = Objectuser(self.__ipAddr, self.__port)

        try:
            if namespace != None:
                objuserval = objObjUser.objectuser_query(uid, namespace)
            else:
                objuserval = objObjUser.objectuser_query(uid)
                namespace = objuserval['namespace']
        except SOSError as e:
            raise e

        # Checks if UID is allowed an additional secret key
        try:
            secretkeyrslt = self.secretkey_show(uid, namespace)
            if ((secretkeyrslt['secret_key_1'] != "") and
                    (secretkeyrslt['secret_key_2'] != "")):
                raise SOSError(SOSError.MAX_COUNT_REACHED,
                               "Already two secret keys exist for the uid " + uid)
        except SOSError as e:
            if("Not Found" not in e.err_text):
                raise e

        uri = self.URI_SECRET_KEY_USER.format(uid)

        parms = {
            'existing_key_expiry_time_mins': expiry,
            'namespace': namespace
        }

        if (secretkey is not None):
            parms['secretkey'] = secretkey

        body = json.dumps(parms)

        (s, h) = common.service_json_request(self.__ipAddr,
                                             self.__port, "POST",
                                             uri, body)
        o = common.json_decode(s)

        return o


    def secretkey_delete(self, uid, secretkey, namespace):
        '''
        Deletes a secret keys for the specific user identifier.
        '''

        #Checks if UID/namespace params are valid
        from objectuser import Objectuser
        objObjUser = Objectuser(self.__ipAddr, self.__port)

        try:
            if namespace != None:
                objuserval = objObjUser.objectuser_query(uid, namespace)
            else:
                objuserval = objObjUser.objectuser_query(uid)
        except SOSError as e:
            raise e

        uri = self.URI_DELETE_SECRET_KEY_USER.format(uid)

        parms = {
            'secret_key': secretkey,
            'namespace': namespace
        }

        body = json.dumps(parms)

        (s, h) = common.service_json_request(self.__ipAddr,
                                             self.__port, "POST",
                                             uri, body)
        return 


    def user_secretkey_show(self):
        '''
        Gets all configured secret keys for the authenticated
        user account that makes the request.
        '''

        (s, h) = common.service_json_request(self.__ipAddr,
                                             self.__port, "GET",
                                             self.URI_SECRET_KEY, None)
        o = common.json_decode(s)

        return o


    def user_secretkey_add(self, expiry):
        '''
        Create a secret key for the authenticated
        user account that makes the request.
        '''

        parms = {
            'existing_key_expiry_time_mins': expiry
        }

        body = json.dumps(parms)

        (s, h) = common.service_json_request(self.__ipAddr,
                                             self.__port, "POST",
                                             self.URI_SECRET_KEY, body)
        o = common.json_decode(s)

        return o


    def user_secretkey_delete(self, secretkey):
        '''
        Deletes the specified secret keys authenticated
        user account that makes the request.
        '''

        parms = {
            'secret_key': secretkey
        }

        body = json.dumps(parms)
        (s, h) = common.service_json_request(self.__ipAddr,
                                             self.__port, "POST",
                                             self.URI_DELETE_SECRET_KEY, body)
        return


def add_parser(subcommand_parsers, common_parser):
    # add command parser
    add_parser = subcommand_parsers.add_parser(
        'user-add',
        description='ECS Secretkeyuser Create CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Create a secretkey for an user')

    mandatory_args = add_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-uid',
                                help='UID',
                                metavar='<uid>',
                                dest='uid',
                                required=True)

    add_parser.add_argument('-namespace', '-ns',
                            help='Namespace for user.  Required if userscope is NAMESPACE.',
                            default=None,
                            metavar='<namespace>',
                            dest='namespace')

    add_parser.add_argument('-existingkeyexpiry',
                            help='Key expiry in minutes',
                            default=None,
                            metavar='<existingkeyexpiry>',
                            dest='existingkeyexpiry')

    add_parser.add_argument('-secretkey', '-sk',
                            help='value to use as new secret key',
                            default=None,
                            metavar='<secretkey>',
                            dest='secretkey')


    add_parser.set_defaults(func=secretkey_add)

def secretkey_add(args):

    obj = Secretkeyuser(args.ip, args.port)

    try:
        res = obj.secretkey_add(args.uid, args.namespace, args.existingkeyexpiry, args.secretkey)
    except SOSError as e:
        if (e.err_code in [SOSError.NOT_FOUND_ERR,
                           SOSError.ENTRY_ALREADY_EXISTS_ERR,
                           SOSError.MAX_COUNT_REACHED]):
            raise SOSError(e.err_code, "Secret key " +
                           ": Add secret key failed\n" + e.err_text)
        else:
            raise e


def delete_parser(subcommand_parsers, common_parser):
    # delete command parser
    delete_parser = subcommand_parsers.add_parser(
        'user-delete',
        description='ECS secretkeyuser delete CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Delete a secretkey for a user')

    mandatory_args = delete_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-uid',
                                help='UID',
                                metavar='<uid>',
                                dest='uid',
                                required=True)

    mandatory_args.add_argument('-secretkey', '-sk',
                                help='Secret Key to delete',
                                metavar='<secretkey>',
                                dest='secretkey',
                                required=True)

    delete_parser.add_argument('-namespace', '-ns',
                               help='Namespace for user.',
                               default=None,
                               metavar='<namespace>',
                               dest='namespace')

    delete_parser.set_defaults(func=secretkey_delete)

def secretkey_delete(args):

    obj = Secretkeyuser(args.ip, args.port)

    try:
        res = obj.secretkey_delete(args.uid, args.secretkey, args.namespace)
    except SOSError as e:
        if(e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "Secretkey delete failed: " + e.err_text)
        else:
            raise e


def show_parser(subcommand_parsers, common_parser):
    # show command parser
    show_parser = subcommand_parsers.add_parser(
        'user-show',
        description='ECS Secretkeyuser Show CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Show a Secretkey of a user')

    mandatory_args = show_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-uid',
                                help='UID',
                                metavar='<uid>',
                                dest='uid',
                                required=True)

    show_parser.add_argument('-namespace', '-ns',
                             help='Namespace for user - sets userscope to NAMESPACE.',
                             default=None,
                             metavar='<namespace>',
                             dest='namespace')

    show_parser.set_defaults(func=secretkey_show)

def secretkey_show(args):

    obj = Secretkeyuser(args.ip, args.port)

    try:
        res = obj.secretkey_show(args.uid, args.namespace)
        return common.format_json_object(res)
    except SOSError as e:
        if(e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "Secret key show failed: " + e.err_text)
        else:
            raise e


def user_add_parser(subcommand_parsers, common_parser):
    # user-add command parser
    user_add_parser = subcommand_parsers.add_parser(
        'add',
        description='ECS Secretkeyuser User-Create CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Create a secretkey for current user')

    mandatory_args = user_add_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-existingkeyexpiry',
                            help='Key expiry in minutes',
                            default=None,
                            metavar='<existingkeyexpiry>',
                            dest='existingkeyexpiry')

    user_add_parser.set_defaults(func=user_secretkey_add)

def user_secretkey_add(args):

    obj = Secretkeyuser(args.ip, args.port)

    try:
        obj.user_secretkey_add(args.existingkeyexpiry)
    except SOSError as e:
        if (e.err_code in [SOSError.NOT_FOUND_ERR,
                           SOSError.ENTRY_ALREADY_EXISTS_ERR,
                           SOSError.MAX_COUNT_REACHED]):
            raise SOSError(e.err_code, "Secret key " +
                           ": Add secret key failed\n" + e.err_text)
        else:
            raise e


def user_delete_parser(subcommand_parsers, common_parser):
    # user-delete command parser
    user_delete_parser = subcommand_parsers.add_parser(
        'delete',
        description='ECS secretkeyuser user-delete CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Delete a secretkey for current user')

    mandatory_args = user_delete_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-secretkey', '-sk',
                                help='Secret Key to delete',
                                metavar='<secretkey>',
                                dest='secretkey',
                                required=True)

    user_delete_parser.set_defaults(func=user_secretkey_delete)

def user_secretkey_delete(args):

    obj = Secretkeyuser(args.ip, args.port)

    try:
        obj.user_secretkey_delete(args.secretkey)
    except SOSError as e:
        if(e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "Secretkey delete failed: " + e.err_text)
        else:
            raise e


def user_show_parser(subcommand_parsers, common_parser):
    # user-show command parser
    user_show_parser = subcommand_parsers.add_parser(
        'show',
        description='ECS Secretkeyuser User-Show CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Show all secret keys for current user')

    user_show_parser.set_defaults(func=user_secretkey_show)

def user_secretkey_show(args):

    obj = Secretkeyuser(args.ip, args.port)

    try:
        res = obj.user_secretkey_show()
        return common.format_json_object(res)
    except SOSError as e:
        if(e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "Secret key show failed: " + e.err_text)
        else:
            raise e


def secretkeyuser_parser(parent_subparser, common_parser):
    # main secretkeyuser parser
    parser = parent_subparser.add_parser(
        'secretkeyuser',
        description='ECS Secretkeyuser CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Operations on Secretkeyuser')
    subcommand_parsers = parser.add_subparsers(help='Use One Of Commands')

    # add command parser
    add_parser(subcommand_parsers, common_parser)

    # delete command parser
    delete_parser(subcommand_parsers, common_parser)

    # show command parser
    show_parser(subcommand_parsers, common_parser)

    # user-add command parser
    user_add_parser(subcommand_parsers, common_parser)

    # user-delete command parser
    user_delete_parser(subcommand_parsers, common_parser)

    # user-show command parser
    user_show_parser(subcommand_parsers, common_parser)

