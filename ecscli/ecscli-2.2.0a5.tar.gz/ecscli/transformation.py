#!/usr/bin/python
# https://asdjenkins.isus.emc.com/jenkins/view/ECS-2.2/job/VS-storage-apidocs-master/lastStableBuild/artifact/VS-storage-apidocs-master/tools/apidocs/build/apidocs/TransformationService_5daafa45d7dcf3402fcfa130b5cafac5_overview.html

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


class Transformation(object):

    '''
    The class definition for operations on 'Transformation'.
    '''

    # Commonly used URIs for the 'objectuser' module

    URI_SERVICES_BASE = ''
    URI_TRANS_BASE = URI_SERVICES_BASE + '/object/transformation'
    URI_TRANS_BASE_ID = URI_SERVICES_BASE + '/object/transformation' + '/{0}'


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
        parms = {
            "type": args.type,
            "admin": args.admin,
            "password": args.password,
            "management_ip": args.mgmtIp,
            "access_ip": args.accessIp,
            "port": args.mgmtPort,
            "datagram_port": args.datagramPort,
            "name": args.name,
            "description": args.description,
            "replication_group": args.repGroup
        }

        body = json.dumps(parms)

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "POST",
                                             Transformation.URI_TRANS_BASE, body, None, xml)

        if(self.__format == "json"):
            o = common.json_decode(s)
            return o
        return s


    def update(self, args):
        uri = Transformation.URI_TRANS_BASE_ID.format(args.transId)
        parms = {
            "type": args.type,
            "admin": args.admin,
            "password": args.password,
            "management_ip": args.mgmtIp,
            "access_ip": args.accessIp,
            "port": args.mgmtPort,
            "datagram_port": args.datagramPort,
            "name": args.name,
            "description": args.description,
            "replication_group": args.repGroup
        }

        body = json.dumps(parms)

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "PUT",
                                             uri, body, None, xml)

        if(self.__format == "json"):
            o = common.json_decode(s)
            return o
        return s


    def get(self, args, stage = None):
        uri = Transformation.URI_TRANS_BASE
        if (hasattr(args, 'transId')):
            if (args.transId is not None):
                uri += '/' + args.transId
                if (stage is not None):
                    uri += '/' + stage

        xml = False
        if self.__format == "xml":
            xml = True

        print("uri: " + uri )
        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                                             uri, None, None, xml)


        if(self.__format == "json"):
            o = common.json_decode(s)
            return o
        return s


    def get_inc_enums(self, args, stage = None):
        uri = Transformation.URI_TRANS_BASE
        if (hasattr(args, 'transId')):
            if (args.transId is not None):
                uri += '/' + args.transId
                if (stage is not None):
                    uri += '/' + stage

        if ((args.sourceId is not None) or (args.token is not None)):
            uri += '?'
            if (args.sourceId is not None):
                uri += 'sourceId=' + args.sourceId
            if ((args.sourceId is not None) and (args.token is not None)):
                uri += '&'
            if (args.token is not None):
                uri += 'token=' + args.token

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                                             uri, None, None, xml)

        if(self.__format == "json"):
            o = common.json_decode(s)
            return o
        return s


    def delete(self, args, stage = None):
        uri = Transformation.URI_TRANS_BASE_ID.format(args.transId)
        if (stage is not None):
            uri += '/' + stage

            if (stage == 'transformationSources'):
                uri += '?'
                if len(args.sourceId) > 1:
                    for sid in args.sourceId[:-1]:
                        uri += 'id=' + sid + '&'
                    uri += 'id=' + args.sourceId[-1]
                else:
                    uri += 'id=' + args.sourceId[0]


        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "DELETE",
                                             uri, None, None, xml)

        if(self.__format == "json"):
            o = common.json_decode(s)
            return o
        return s


    def do(self, args, stage = None):
        uri = Transformation.URI_TRANS_BASE_ID.format(args.transId)
        if (stage is not None):
            uri += '/' + stage

        parms = {}

        body = json.dumps(parms)

        xml = False
        if self.__format == "xml":
            xml = True

        print("uri: " + uri)
        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "POST",
                                             uri, body, None, xml)

        if(self.__format == "json"):
            o = common.json_decode(s)
            return o
        return s

    def doTransSources(self, args, stage = None):
        uri = Transformation.URI_TRANS_BASE_ID.format(args.transId)
        if (stage is not None):
            uri += '/' + stage

        parms = {}
        parms['source_ids'] = args.sourceId

        body = json.dumps(parms)

        xml = False
        if self.__format == "xml":
            xml = True

        print("uri: " + uri)
        print ("body: " + body)
        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "POST",
                                             uri, body, None, xml)

        if(self.__format == "json"):
            o = common.json_decode(s)
            return o
        return s

    def doProfileMapping(self, args, stage = None):
        uri = Transformation.URI_TRANS_BASE_ID.format(args.transId)
        if (stage is not None):
            uri += '/' + stage
    
        parms = {}
        parms['mappings'] = []
        for mapping in args.mappings:
            mapArr = mapping.split('^')
            if (len(mapArr)<4):
                raise SOSError(SOSError.SOS_FAILURE_ERR, "A tagset must be a key value pair string delimited by '^'")
            parms['mappings'].append({"source_id" : mapArr[0], "target_user" : mapArr[1], "target_bucket" : mapArr[2], "target_namespace" : mapArr[3]})


        body = json.dumps(parms)
        
        xml = False
        if self.__format == "xml":
            xml = True

        print("uri: " + uri)
        print("body: " + body)
        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "POST",
                                             uri, body, None, xml)
        if(self.__format == "json"):
            o = common.json_decode(s)
            return o
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

    mandatory_args.add_argument('-type',
                                help='User identifier',
                                metavar='<type>',
                                dest='type',
                                required=True)


    mandatory_args.add_argument('-admin',
                                help='Centera admin name',
                                default=None,
                                dest='admin',
                                required=True)


    mandatory_args.add_argument('-password', '-pw',
                                help='Centera admin user password',
                                default=None,
                                dest='password',
                                required=True)


    mandatory_args.add_argument('-mgmt_ip', 
                                help='Centera management ip address',
                                default=None,
                                dest='mgmtIp',
                                required=True)

    mandatory_args.add_argument('-access_ip',
                                help='Centera data access ip address',
                                default=None,
                                dest='accessIp',
                                required=True)

    mandatory_args.add_argument('-mgmt_port',
                                help='Centera management port',
                                default=None,
                                dest='mgmtPort',
                                required=True)

    mandatory_args.add_argument('-datagram_port',
                                help='Centera data port',
                                default=None,
                                dest='datagramPort',
                                required=True)

    mandatory_args.add_argument('-name',
                                help='Centera user provided name',
                                default=None,
                                dest='name',
                                required=True)

    mandatory_args.add_argument('-description', '-d',
                                help='Centera user provided description',
                                default=None,
                                dest='description',
                                required=True)

    mandatory_args.add_argument('-repGroup', '-rg',
                                help='replicationGroup id',
                                default=None,
                                dest='repGroup',
                                required=False)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_create)

def transformation_create(args):

    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.create(args)
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": Add user failed\n" + e.err_text)
        else:
            raise e


def update_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'update',
        description='ECS Objectuser Create CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Create an objectuser')

    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation Id of transformation to update',
                                dest='transId',
                                required=True)

    mandatory_args.add_argument('-type',
                                help='User identifier',
                                dest='type',
                                required=True)


    mandatory_args.add_argument('-admin',
                                help='Centera admin name',
                                default=None,
                                dest='admin',
                                required=True)


    mandatory_args.add_argument('-password', '-pw',
                                help='Centera admin user password',
                                default=None,
                                dest='password',
                                required=True)


    mandatory_args.add_argument('-mgmt_ip', 
                                help='Centera management ip address',
                                default=None,
                                dest='mgmtIp',
                                required=True)

    mandatory_args.add_argument('-access_ip',
                                help='Centera data access ip address',
                                default=None,
                                dest='accessIp',
                                required=True)

    mandatory_args.add_argument('-mgmt_port',
                                help='Centera management port',
                                default=None,
                                dest='mgmtPort',
                                required=True)

    mandatory_args.add_argument('-datagram_port',
                                help='Centera data port',
                                default=None,
                                dest='datagramPort',
                                required=True)

    mandatory_args.add_argument('-name',
                                help='Centera user provided name',
                                default=None,
                                dest='name',
                                required=True)

    mandatory_args.add_argument('-description', '-d',
                                help='Centera user provided description',
                                default=None,
                                dest='description',
                                required=True)

    mandatory_args.add_argument('-repGroup', '-rg',
                                help='replicationGroup id',
                                default=None,
                                dest='repGroup',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_update)

def transformation_update(args):

    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.update(args)
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": Add user failed\n" + e.err_text)
        else:
            raise e


def get_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'get',
        description='ECS Objectuser Create CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Create an objectuser')


    create_parser.add_argument('-transId', 
                                dest='transId',
                                help='transformation Id, if empty then all will be retrieved')

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_get)

def transformation_get(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.get(args)
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": Add user failed\n" + e.err_text)
        else:
            raise e


def do_precheck_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'do-precheck',
        description='ECS Objectuser Create CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Create an objectuser')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_do_precheck)

def transformation_do_precheck(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.do(args, 'precheck')
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": Add user failed\n" + e.err_text)
        else:
            raise e


def do_enum_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'do-enum',
        description='ECS transformation CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='do transformation enumeration')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_do_enum)

def transformation_do_enum(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.do(args, 'enumeration')
        return res
    except SOSError as e:
        raise e


def do_indexing_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'do-index',
        description='ECS Objectuser Create CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Create an objectuser')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_do_indexing)

def transformation_do_indexing(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.do(args, 'indexing')
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": Add user failed\n" + e.err_text)
        else:
            raise e


def do_migration_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'do-migration',
        description='ECS Objectuser Create CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Create an objectuser')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_do_migration)

def transformation_do_migration(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.do(args, 'migration')
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": Add user failed\n" + e.err_text)
        else:
            raise e


def do_reconciliation_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'do-reconcile',
        description='ECS Objectuser Create CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Create an objectuser')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_do_reconciliation)

def transformation_do_reconciliation(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.do(args, 'reconciliation')
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": Add user failed\n" + e.err_text)
        else:
            raise e


def do_transSources_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'do-trans-sources',
        description='ECS Objectuser Create CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Create an objectuser')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    mandatory_args.add_argument('-sourceId', '-si',
                                help='transformation sourceId returned from get-profile-mapping',
                                dest='sourceId',
                                nargs='+',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_do_trans_sources)

def transformation_do_trans_sources(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.doTransSources(args, 'transformationSources')
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": Add user failed\n" + e.err_text)
        else:
            raise e


def delete_sources_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'delete-sources',
        description='delete the transformation sources',
        parents=[common_parser],
        conflict_handler='resolve',
        help='delete transformation sources')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    mandatory_args.add_argument('-sourceId', '-si',
                                help='transformation sourceId returned from get-profile-mapping',
                                dest='sourceId',
                                nargs='+',
                                required=True)


    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_delete_sources)

def transformation_delete_sources(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.delete(args, 'transformationSources')
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": Add user failed\n" + e.err_text)
        else:
            raise e



def get_profile_mapping_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'get-profile-mapping',
        description='ECS Objectuser Create CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Create an objectuser')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_get_profile_mapping)

def transformation_get_profile_mapping(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.get(args, 'profile/mapping')
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": Add user failed\n" + e.err_text)
        else:
            raise e



def do_profile_mapping_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'do-profile-mapping',
        description='ECS Objectuser Create CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Create an objectuser')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.add_argument('-mapping','-mp',
                                help='List of one or more mappings source_id^target_user^target_bucket^target_namespace tuples ' +
                                     'each tuple specified in that order',
                                metavar='<mappings>',
                                dest='mappings',
                                nargs='+')

    create_parser.set_defaults(func=transformation_do_profile_mapping)

def transformation_do_profile_mapping(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.doProfileMapping(args, 'profile/mapping')
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": Add user failed\n" + e.err_text)
        else:
            raise e


def get_precheck_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'get-precheck',
        description='ECS gets a precheck report for a transformation',
        parents=[common_parser],
        conflict_handler='resolve',
        help='gets a precheck report for a transformation id')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_get_precheck)

def transformation_get_precheck(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.get(args, 'precheck')
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": Add user failed\n" + e.err_text)
        else:
            raise e




def get_enum_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'get-enum',
        description='ECS transformation CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='get transformation enumeration')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_get_enum)

def transformation_get_enum(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.get(args, 'enumeration')
        return res
    except SOSError as e:
        raise e


def get_indexing_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'get-indexing',
        description='ECS get transformation indexing report CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='gets a transformation indexing report')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_get_indexing)

def transformation_get_indexing(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.get(args, 'indexing')
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": Add user failed\n" + e.err_text)
        else:
            raise e




def get_reconciliation_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'get-recon',
        description='ECS transformation CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='get the transformation reconconciliation report')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_get_recon)

def transformation_get_recon(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.get(args, 'reconciliation')
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": Add user failed\n" + e.err_text)
        else:
            raise e




def get_recon_mismatches_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'get-recon-mismatches',
        description='ECS transformation CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='get a report on centera transformation reconciliation mistmatches')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_get_recon_mismatches)

def transformation_get_recon_mismatches(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.get(args, 'reconciliation/mismatches')
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": Add user failed\n" + e.err_text)
        else:
            raise e



def get_migration_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'get-migration',
        description='ECS transformation CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='get ECS transformation migration report')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_get_migration)

def transformation_get_migration(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.get(args, 'migration')
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": Add user failed\n" + e.err_text)
        else:
            raise e




def do_precheck_retry_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'do-precheck-retry',
        description='ECS transformation CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='does a precheck retry for the transformation')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_do_precheck_retry)

def transformation_do_precheck_retry(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.do(args, 'precheck/retry')
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": Add user failed\n" + e.err_text)
        else:
            raise e



def do_enum_parser_retry(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'do-enum-retry',
        description='ECS transformation CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='do transformation enumeration retry')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_do_enum_retry)

def transformation_do_enum_retry(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.do(args, 'enumeration/retry')
        return res
    except SOSError as e:
        raise e


def do_index_retry_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'do-index-retry',
        description='ECS transformation CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='do a transformation index retry')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_do_index_retry)

def transformation_do_index_retry(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.do(args, 'indexing/retry')
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": Add user failed\n" + e.err_text)
        else:
            raise e




def do_recon_retry_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'do-recon-retry',
        description='ECS transformation CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='do a transformation reconciliation retry')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_do_recon_retry)

def transformation_do_recon_retry(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.do(args, 'reconciliation/retry')
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": Add user failed\n" + e.err_text)
        else:
            raise e



def do_migration_retry_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'do-migration-retry',
        description='ECS transformation CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Create an objectuser')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_do_migration_retry)

def transformation_do_migration_retry(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.do(args, 'migration/retry')
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": Add user failed\n" + e.err_text)
        else:
            raise e

def get_inc_enums_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'get_inc_enums',
        description='ECS transformation CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='get a list of incomplete enumerations')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    create_parser.add_argument('-sourceId',
                                help='source id result returned from GET failed sources',
                                dest='sourceId',
                                required=True)
    create_parser.add_argument('-token',
                                help='a token returned by previous call to GET Centera Incomplete Enumeration Results, or null for first call',
                                dest='token',
                                required=True)


    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_get_inc_enums)

def transformation_get_inc_enums(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.get_inc_enums(args, 'centera/incompleteEnumerationResults')
        return res
    except SOSError as e:
        if (e.err_code in [SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Objectuser " +
                           args.uid + ": Add user failed\n" + e.err_text)
        else:
            raise e


def get_failed_sources_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'get-failed-sources',
        description='ECS transformation CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='get transformation failed sources')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_get_failed_sources)

def transformation_get_failed_sources(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.get(args, 'enumeration/failedSources')
        return res
    except SOSError as e:
        raise e


def do_cancel_precheck_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'cancel-precheck',
        description='ECS transformation CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='cancel the transformation precheck')

    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_do_cancel_precheck)

def transformation_do_cancel_precheck(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.do(args, 'precheck/cancel')
        return res
    except SOSError as e:
        raise e



def do_enum_cancel_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'cancel-enum',
        description='ECS transformation CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='cancel transformation enumeration')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_do_enum_cancel)

def transformation_do_enum_cancel(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.do(args, 'enumeration/cancel')
        return res
    except SOSError as e:
        raise e



def do_index_cancel_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'cancel-indexing',
        description='ECS transformation CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='do transformation enumeration')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_do_cancel_index)

def transformation_do_cancel_index(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.do(args, 'indexing/cancel')
        return res
    except SOSError as e:
        raise e



def do_cancel_recon_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'cancel-recon',
        description='ECS transformation CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='cancel transformation reconciliation')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_do_cancel_recon)

def transformation_do_cancel_recon(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.do(args, 'reconciliation/cancel')
        return res
    except SOSError as e:
        raise e




def do_cancel_migration_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'cancel-migration',
        description='ECS transformation CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='cancel transformation migration')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_do_cancel_migration)

def transformation_do_cancel_migration(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.do(args, 'migration/cancel')
        return res
    except SOSError as e:
        raise e


def delete_tranformation_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'delete-transformation',
        description='delete the transformation',
        parents=[common_parser],
        conflict_handler='resolve',
        help='delete transformation')


    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-transId',
                                help='transformation id',
                                dest='transId',
                                required=True)

    create_parser.add_argument('-format', '-f',
                                metavar='<format>', dest='format',
                                help='response format: xml or json (default:json)',
                                choices=['xml', 'json'],
                                default="json")

    create_parser.set_defaults(func=transformation_delete)

def transformation_delete(args):
    obj = Transformation(args.ip, args.port, args.format)
    try:
        res = obj.delete(args)
        return res
    except SOSError as e:
        raise e


# Objectuser Main parser routine
def transformation_parser(parent_subparser, common_parser):
    # main objectuser parser
    parser = parent_subparser.add_parser(
        'transformation',
        description='ECS Centera transformation CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Operations on Centera transformation')
    subcommand_parsers = parser.add_subparsers(help='Use One Of Commands')

    # create command parser
    create_parser(subcommand_parsers, common_parser)
    update_parser(subcommand_parsers, common_parser)
    get_parser(subcommand_parsers, common_parser)
    do_precheck_parser(subcommand_parsers, common_parser)
    do_indexing_parser(subcommand_parsers, common_parser)
    do_migration_parser(subcommand_parsers, common_parser)
    do_reconciliation_parser(subcommand_parsers, common_parser)
    do_transSources_parser(subcommand_parsers, common_parser)
    delete_sources_parser(subcommand_parsers, common_parser)
    get_profile_mapping_parser(subcommand_parsers, common_parser)
    do_profile_mapping_parser(subcommand_parsers, common_parser)
    get_precheck_parser(subcommand_parsers, common_parser)
    get_enum_parser(subcommand_parsers, common_parser)
    get_indexing_parser(subcommand_parsers, common_parser)
    get_reconciliation_parser(subcommand_parsers, common_parser)
    get_recon_mismatches_parser(subcommand_parsers, common_parser)
    get_migration_parser(subcommand_parsers, common_parser)
    do_precheck_retry_parser(subcommand_parsers, common_parser)
    do_enum_parser(subcommand_parsers, common_parser)
    do_enum_parser_retry(subcommand_parsers, common_parser)
    do_index_retry_parser(subcommand_parsers, common_parser)
    do_recon_retry_parser(subcommand_parsers, common_parser)
    do_migration_retry_parser(subcommand_parsers, common_parser)
    get_inc_enums_parser(subcommand_parsers, common_parser)
    get_failed_sources_parser(subcommand_parsers, common_parser)
    do_cancel_precheck_parser(subcommand_parsers, common_parser)
    do_enum_cancel_parser(subcommand_parsers, common_parser)
    do_index_cancel_parser(subcommand_parsers, common_parser)
    do_cancel_recon_parser(subcommand_parsers, common_parser)
    do_cancel_migration_parser(subcommand_parsers, common_parser)
    delete_tranformation_parser(subcommand_parsers, common_parser)
