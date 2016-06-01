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

class VdcKeystore(object):

    '''
    The class definition for operations on 'VDC keystore ie UI/Admin api certificate'.
    '''

    URI_SERVICES_BASE = ''
    URI_VDC_KEYSTORE_BASE = URI_SERVICES_BASE + '/vdc/keystore'


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


    def create(self, args):
        certificateChain = None
        privateKey = None

        try:
            f1 = open(args.certificateChain, 'r')
            certificateChain = f1.read()
        except IOError as e:
            raise SOSError(e.errno, e.strerror)


        try:
            f1 = open(args.privateKey, 'r')
            privateKey = f1.read()
        except IOError as e:
            raise SOSError(e.errno, e.strerror)


        key_and_certificate = {}
        key_and_certificate['private_key'] = privateKey
        key_and_certificate['certificate_chain'] = certificateChain
    
        parms = {
            "key_and_certificate": key_and_certificate
        }
        body = json.dumps(parms)

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "PUT",
                                             VdcKeystore.URI_VDC_KEYSTORE_BASE, body, None, xml)

        if(self.__format == "json"):
            o = common.json_decode(s)
            return o
        return s


    def get(self, args, stage = None):
        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                                             VdcKeystore.URI_VDC_KEYSTORE_BASE, None, None, xml)

        if(self.__format == "json"):
            o = common.json_decode(s)
            return o
        return s


def create_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'update',
        description='ECS UI/Admin API certificate Create CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='ECS UI/Admin API certificate Create CLI usage.')

    create_parser.add_argument('-privateKey', '-pk',
                                help='private key string',
                                dest='privateKey',
                                required=True)

    create_parser.add_argument('-certificateChain', '-cc',
                                help='certificate chain string',
                                dest='certificateChain',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=vdc_keystore_create)

def vdc_keystore_create(args):

    obj = VdcKeystore(args.ip, args.port, args.format)
    try:
        res = obj.create(args)
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "vdc keystore error" + e.err_text)
        else:
            raise e



def get_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'get',
        description='retrive ECS vdc keystore (UI/Admin cert) CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Get the UI/Admin certificate')

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=vdc_keystore_get)

def vdc_keystore_get(args):
    obj = VdcKeystore(args.ip, args.port, args.format)
    try:
        res = obj.get(args)
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.NOT_FOUND_ERR]):
            raise SOSError(e.err_code, "Vdc keystore error. Certificate not found. " + e.err_text)
        else:
            raise e



# Objectuser Main parser routine
def vdc_keystore_parser(parent_subparser, common_parser):
    # main objectuser parser
    parser = parent_subparser.add_parser(
        'vdc_keystore',
        description='ECS vdc keystore (ie UI/Admin certificate) CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Operations on vdc keystore certificate')
    subcommand_parsers = parser.add_subparsers(help='Use One Of Commands')

    # create command parser
    create_parser(subcommand_parsers, common_parser)
    get_parser(subcommand_parsers, common_parser)




