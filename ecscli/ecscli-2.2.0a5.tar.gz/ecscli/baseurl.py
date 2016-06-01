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
from common import SOSError


class BaseURL(object):
    '''
    The class definition for operations on 'Bucket'.
    '''

    # Commonly used URIs for the 'baseurl' module

    URI_SERVICES_BASE = ''
    URI_BASEURL = URI_SERVICES_BASE + '/object/baseurl'
    URI_BASEURL_INSTANCE = URI_BASEURL + '/{0}'
    URI_BASEURL_DELETE = URI_BASEURL_INSTANCE + '/deactivate'

    def __init__(self, ipAddr, port):
        '''
        Constructor: takes IP address and port of the ECS instance. These are
        needed to make http requests for REST API
        '''
        self.__ipAddr = ipAddr
        self.__port = port


    def baseurl_create(self, name, url, isnamespace):
        '''
        Creates a Base URL with the given details.
        '''

        parms = {
            'name': name,
            'base_url': url,
            'is_namespace_in_host': isnamespace
        }

        body = json.dumps(parms)

        (s,h) = common.service_json_request(self.__ipAddr, self.__port, "POST",
                                            BaseURL.URI_BASEURL, body)
        o = common.json_decode(s)

        if (not o):
            return {}
        return o


    def baseurl_update(self, id, name, url, isnamespace):
        '''
        Updates the Base URL for the specified Base URL identifier.
        '''

        parms = {
            'name': name,
            'base_url': url,
            'is_namespace_in_host': isnamespace
        }

        body = json.dumps(parms)

        (s,h) = common.service_json_request(self.__ipAddr, self.__port, "PUT",
                                            BaseURL.URI_BASEURL_INSTANCE.format(id), body)
        o = common.json_decode(s)

        if (not o):
            return {}
        return o


    def get_baseurl(self, id):
        '''
        Gets details for the specified Base URL.

        If no Base URL identifier is provided, lists details
        for all configured Base URLs.
        '''

        if (id is not None):
            url = BaseURL.URI_BASEURL_INSTANCE.format(id)
        else:
            url = BaseURL.URI_BASEURL

        (s,h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                                            url, None)

        o = common.json_decode(s)
        if (not o):
            return {}

        return o


    def baseurl_delete(self, id):
        '''
        Deletes the specified Base URL.
        '''

        (s,h) = common.service_json_request(self.__ipAddr, self.__port, "POST",
                                            BaseURL.URI_BASEURL_DELETE.format(id), None)
        o = common.json_decode(s)

        if (not o):
            return {}
        return o


def create_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'create',
        description='ECS Create Base URL CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='create base url')

    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-name',
                                help='Name of Base URL',
                                metavar='<name>',
                                dest='name',
				required=True)

    mandatory_args.add_argument('-baseurl', '-url',
                                help='Base URL to be used',
                                metavar='<baseurl>',
                                dest='baseurl', 
				required=True)

    create_parser.add_argument('-isnamespace', '-isns',
                               help='Boolean indicating whether namespace is in host',
                               default='false',
                               choices=['true', 'false'],
                               dest='isnamespace')

    create_parser.set_defaults(func=create_baseurl)

def create_baseurl(args):

    obj = BaseURL(args.ip, args.port)

    try:
        res = obj.baseurl_create(args.name,
                                 args.baseurl,
                                 args.isnamespace)
        return res
    except SOSError as e:
        raise e


def update_parser(subcommand_parsers, common_parser):
    # update command parser
    update_parser = subcommand_parsers.add_parser(
        'update',
        description='ECS Update Base URL CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='update base url')

    mandatory_args = update_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-id',
                                help='Base URL identifier',
                                metavar='<id>',
                                dest='id',
				required=True)

    mandatory_args.add_argument('-name',
                                help='Name of Base URL',
                                metavar='<name>',
                                dest='name',
				required=True)

    mandatory_args.add_argument('-baseurl', '-url',
                                help='Base URL to be used',
                                metavar='<baseurl>',
                                dest='baseurl',
				required=True)

    update_parser.add_argument('-isnamespace', '-isns',
                               help='Boolean indicating whether namespace is in host',
                               default='false',
                               choices=['true', 'false'],
                               dest='isnamespace')



    update_parser.set_defaults(func=update_baseurl)

def update_baseurl(args):

    obj = BaseURL(args.ip, args.port)

    try:
        res = obj.baseurl_update(args.id,
                                 args.name,
                                 args.baseurl,
                                 args.isnamespace)
        return res
    except SOSError as e:
        raise e


def get_parser(subcommand_parsers, common_parser):
    # get command parser
    get_parser = subcommand_parsers.add_parser(
        'get',
        description='ECS Get Base URL(s) CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='get base url(s)')

    get_parser.add_argument('-id',
                            help='Base URL identifier',
                            default=None,
                            metavar='<id>',
                            dest='id')

    get_parser.set_defaults(func=get_baseurl)

def get_baseurl(args):

    obj = BaseURL(args.ip, args.port)

    try:
        res = obj.get_baseurl(args.id)
        return res
    except SOSError as e:
        raise e


def delete_parser(subcommand_parsers, common_parser):
    # delete command parser
    delete_parser = subcommand_parsers.add_parser(
        'delete',
        description='ECS Delete Base URL CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='delete base url')

    mandatory_args = delete_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-id',
                               help='Base URL identifier',
                               metavar='<id>',
                               dest='id',
			       required=True)

    delete_parser.set_defaults(func=delete_baseurl)

def delete_baseurl(args):

    obj = BaseURL(args.ip, args.port)

    try:
        res = obj.baseurl_delete(args.id)
        return res
    except SOSError as e:
        raise e


def baseurl_parser(parent_subparser, common_parser):
    # main baseurl parser
    parser = parent_subparser.add_parser('baseurl',
                                         description='ECS Base URL CLI usage',
                                         parents=[common_parser],
                                         conflict_handler='resolve',
                                         help='Operations on Base URL')
    subcommand_parsers = parser.add_subparsers(help='Use One Of Commands')

    # create command parser
    create_parser(subcommand_parsers, common_parser)

    # update command parser
    update_parser(subcommand_parsers, common_parser)

    # list command parser
    get_parser(subcommand_parsers, common_parser)

    # delete command parser
    delete_parser(subcommand_parsers, common_parser)
