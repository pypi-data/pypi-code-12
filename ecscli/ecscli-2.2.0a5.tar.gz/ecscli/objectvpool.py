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
from virtualarray import VirtualArray
from virtualdatacenter import VirtualDatacenter

class ObjectVpool(object):
    '''
    The class definition for operations on ObjectVPool
    '''

    #Common URIs for objectvpool
    URI_SERVICES_BASE      = '' 
    URI_OBJ_VPOOL          = URI_SERVICES_BASE + '/vdc/data-service/vpools'
    URI_OBJ_VPOOL_INSTANCE = URI_OBJ_VPOOL + '/{0}'


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


    def objectvpool_list(self):
        '''
        Gets the identifiers for all configured replication groups.
        '''

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "GET", ObjectVpool.URI_OBJ_VPOOL,
                                             None, None, xml)

        if (self.__format == "json"):
            o = common.json_decode(s)
            return o
        return s


    def objectvpool_query(self, name):
        '''
        Gets the uri for the specified object name.
        '''

        if (common.is_uri(name)):
            return name

        try:
            objcos = self.objectvpool_show(name)
        except SOSError as e:
            raise e

        if ( objcos['name'] == name and objcos['inactive'] == False ):
            return objcos['id']

        raise SOSError(SOSError.NOT_FOUND_ERR,
                       "Object Vpool query failed: active object vpool" +
                       "with name " + name + " not found")


    def objectvpool_show(self, id):
        '''
        Gets the details for the specified replication group.
        '''

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request( self.__ipAddr, self.__port,
                                              "GET", self.URI_OBJ_VPOOL_INSTANCE.format(id),
                                              None, None, xml)

        if (self.__format == "json"):
            o = common.json_decode(s)
            return o
        return s


    def objectvpool_create(self, name, description, zonemaps, allow):
        '''
        Creates a replication group that includes the
        specified storage pools (VDC:storage pool tuple).
        '''

        parms = {
            'name': name,
            'description': description
        }
        if (name):
            parms['name'] = name
        if (description):
            parms['description'] = description
        parms['zone_mappings'] = []

        for zonemap in zonemaps:
            pair = zonemap.split('^')
            varray = VirtualArray(self.__ipAddr,
                                  self.__port).varray_query(pair[0])
            vdc = None
            if(len(pair) > 1 and len(pair[1]) > 0):
                vdc = VirtualDatacenter(self.__ipAddr,
                                            self.__port).vdc_query(pair[1])
            else:
                raise SOSError(SOSError.SOS_FAILURE_ERR,
                               "Please provide vdc in -zonemapping parameter ")
            parms['zone_mappings'].append({"name" : vdc, "value" : varray})

        parms['isAllowAllNamespaces'] = allow

        body = json.dumps(parms)

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "POST", self.URI_OBJ_VPOOL,
                                             body, None, xml)

        if (self.__format == "json"):
            o = common.json_decode(s)
            return o
        return s


    def objectvpool_add(self, id, maps):
        '''
        Adds one or more storage pools (as VDC:storage pool tuples)
        to the specified replication group.
        '''

        parms = dict()
        parms['mappings'] = []

        for map in maps:
            pair = map.split('^')
            varray = VirtualArray(self.__ipAddr,
                                  self.__port).varray_query(pair[1])
            vdc = None
            if(len(pair) > 1 and len(pair[0]) > 0):
                vdc = VirtualDatacenter(self.__ipAddr,
                                            self.__port).vdc_query(pair[0])
            else:
                raise SOSError(SOSError.SOS_FAILURE_ERR,
                               "Please provide vdc in -mapping parameter ")
            parms['mappings'].append({"name" : vdc, "value" : varray})


        body = json.dumps(parms)

        uri = self.URI_OBJ_VPOOL_INSTANCE + '/addvarrays'

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "PUT", uri.format(id), body)


    def objectvpool_remove(self, id, maps):
        '''
        Removes one or more storage pools (as VDC:storage pool tuples)
        from the specified replication group.
        '''

        parms = dict()
        parms['mappings'] = []

        for map in maps:
            pair = map.split('^')
            varray = VirtualArray(self.__ipAddr,
                                  self.__port).varray_query(pair[1])
            vdc = None
            if(len(pair) > 1 and len(pair[0]) > 0):
                vdc = VirtualDatacenter(self.__ipAddr,
                                            self.__port).vdc_query(pair[0])
            else:
                raise SOSError(SOSError.SOS_FAILURE_ERR,
                               "Please provide vdc in -mapping parameter ")
            parms['mappings'].append({"name" : vdc, "value" : varray})


        body = json.dumps(parms)
        uri = self.URI_OBJ_VPOOL_INSTANCE.format(id) + '/removevarrays'

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "PUT", uri.format(id), body)

            
    def objectvpool_delete(self, id):
        '''
        Makes a REST API call to delete a objectvpool by its UUID
        '''

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "POST",
                    self.URI_OBJ_VPOOL_INSTANCE.format(id) + "/deactivate", None)


    def objectvpool_update(self, id, name, description, allow):
        '''
        Updates the name and description for a replication group.
        '''

        parms = {
            'name': name,
            'description': description,
            'allowAllNamespaces': allow
        }

        body = json.dumps(parms)

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                            "PUT", self.URI_OBJ_VPOOL_INSTANCE.format(id), body)


def create_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'create',
        description='ECS ObjectVPool Create CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Create an objectvpool')

    mandatory_args = create_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-name',
                                help='name identifying this classification ' +
                                    'of replication group',
                                metavar='<name>',
                                dest='name',
                                required=True)

    mandatory_args.add_argument('-description','-desc',
                                help='description of object vpool',
                                metavar='<description>',
                                dest='description')

    mandatory_args.add_argument('-zonemapping','-zp',
                                help='List of varrayId-zoneId tuples ' +
                                     'eg list of storagepool^VDC, storagepool^VDC',
                                metavar='<zonemapping>',
                                dest='zonemapping',
                                nargs='+',
                                required=True)

    mandatory_args.add_argument('-allowallnamespaces','-aan',
                                help='indicates if vpool allows access to ' +
                                    'all Namespaces for dataservices',
                                metavar='<allowAllNamespaces>',
                                dest='allowAllNamespaces',
                                required=True)

    create_parser.add_argument('-format', '-f',
                               metavar='<format>', dest='format',
                               help='response format: xml or json (default:json)',
                               choices=['xml', 'json'],
                               default="json")


    create_parser.set_defaults(func=objectvpool_create)

def objectvpool_create(args):
    obj = ObjectVpool(args.ip, args.port, args.format)

    try:
        return obj.objectvpool_create(args.name, args.description,
                                  args.zonemapping, args.allowAllNamespaces)
    except SOSError as e:
        common.format_err_msg_and_raise("create", "object vpool",
                                        e.err_text, e.err_code)


def add_parser(subcommand_parsers, common_parser):
    # add command parser
    add_parser = subcommand_parsers.add_parser(
        'add',
        description='ECS ObjectVPool Add CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Add storage pool(s) to an objectvpool')

    mandatory_args = add_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-id',
                                help='id of object vpool',
                                metavar='<id>',
                                dest='id',
                                required=True)

    mandatory_args.add_argument('-mapping','-m',
                                help='List of varrayId-zoneId tuples ' +
                                     'eg list of VDC^Virtualarray',
                                metavar='<mapping>',
                                dest='mapping',
                                nargs='+',
                                required=True)

    add_parser.set_defaults(func=objectvpool_add)

def objectvpool_add(args):
    obj = ObjectVpool(args.ip, args.port)

    try:
        obj.objectvpool_add(args.id, args.mapping)
    except SOSError as e:
        common.format_err_msg_and_raise("add", "object vpool",
                                        e.err_text, e.err_code)


def remove_parser(subcommand_parsers, common_parser):
    # remove command parser
    remove_parser = subcommand_parsers.add_parser(
        'remove',
        description='ECS ObjectVPool Remove CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Remove storage pool(s) from an objectvpool')

    mandatory_args = remove_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-id',
                                help='id of object vpool',
                                metavar='<id>',
                                dest='id',
                                required=True)

    mandatory_args.add_argument('-mapping','-m',
                                help='List of varrayId-zoneId tuples ' +
                                     'eg list of VDC^Virtualarray',
                                metavar='<mapping>',
                                dest='mapping',
                                nargs='+',
                                required=True)

    remove_parser.set_defaults(func=objectvpool_remove)

def objectvpool_remove(args):
    obj = ObjectVpool(args.ip, args.port)

    try:
        obj.objectvpool_remove(args.id, args.mapping)
    except SOSError as e:
        common.format_err_msg_and_raise("remove", "object vpool",
                                        e.err_text, e.err_code)


def delete_parser(subcommand_parsers, common_parser):
    # delete command parser
    delete_parser = subcommand_parsers.add_parser(
        'delete',
        description='ECS ObjectVPool delete CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Delete an ObjectVPool')

    mandatory_args = delete_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-id',
                                help='id of object vpool',
                                metavar='<id>',
                                dest='id',
                                required=True)

    delete_parser.set_defaults(func=objectvpool_delete)

def objectvpool_delete(args):
    obj = ObjectVpool(args.ip, args.port)

    try:
        obj.objectvpool_delete(args.id)
    except SOSError as e:
	    common.format_err_msg_and_raise("delete", "object vpool", e.err_text, e.err_code)


def update_parser(subcommand_parsers, common_parser):
    # update command parser
    update_parser = subcommand_parsers.add_parser(
        'update',
       description='ECS ObjectVPool Update CLI usage.',
       parents=[common_parser],
       conflict_handler='resolve',
       help='Create an ObjectVPool')

    mandatory_args = update_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-id',
                                help='id of object vpool',
                                metavar='<id>',
                                dest='id',
                                required=True)

    mandatory_args.add_argument('-name','-n',
                                help='name to update',
                                metavar='<name>',
                                dest='name',
                                required=True)

    mandatory_args.add_argument('-description','-d',
                                help='Description to update',
                                metavar='<description>',
                                dest='description',
                                required=True)

    mandatory_args.add_argument('-allowallnamespaces','-aan',
                                help='AllowAllNamespaces boolean to update',
                                metavar='<allowAllNamespaces>',
                                dest='allowAllNamespaces',
                                required=True)


    update_parser.set_defaults(func=objectvpool_update)

def objectvpool_update(args):
    obj = ObjectVpool(args.ip, args.port)
    try:
        obj.objectvpool_update(args.id, args.name, args.description,
                                  args.allowAllNamespaces)
    except SOSError as e:
        common.format_err_msg_and_raise("update", "object vpool",
                                        e.err_text, e.err_code)


def show_parser(subcommand_parsers, common_parser):
    # show command parser
    show_parser = subcommand_parsers.add_parser(
        'show',
        description='ECS ObjectVPool show CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Show an ObjectVPool')

    mandatory_args = show_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-id',
                                help='id of object vpool',
                                metavar='<id>',
                                dest='id',
                                required=True)

    show_parser.add_argument('-format', '-f',
                             metavar='<format>', dest='format',
                             help='response format: xml or json (default:json)',
                             choices=['xml', 'json'],
                             default="json")

    show_parser.set_defaults(func=objectvpool_show)

def objectvpool_show(args):
    obj = ObjectVpool(args.ip, args.port, args.format)

    try:
        return obj.objectvpool_show(args.id)
    except SOSError as e:
	    common.format_err_msg_and_raise("show", "object vpool", e.err_text, e.err_code)


def list_parser(subcommand_parsers, common_parser):
    # list command parser
    list_parser = subcommand_parsers.add_parser(
        'list',
        description='ECS ObjectVPool List CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='List ObjectVPools')

    #list_parser.add_argument('-verbose', '-v',
    #                         action='store_true',
    #                         help='List objectvpools with details',
    #                         dest='verbose')

    #list_parser.add_argument('-long', '-l',
    #                         action='store_true',
    #                         help='List objectvpools with more details in tabular format',
    #                         dest='long')

    list_parser.add_argument('-format', '-f',
                             metavar='<format>', dest='format',
                             help='response format: xml or json (default:json)',
                             choices=['xml', 'json'],
                             default="json")

    list_parser.set_defaults(func=objectvpool_list)

def objectvpool_list(args):
    obj = ObjectVpool(args.ip, args.port, args.format)

    try:
        res = obj.objectvpool_list()
        return res

            # output = []
            #
            # for iter in res:
            # if(iter['inactive']==False):
            #         output.append(iter)
            #
            # if(len(output) > 0):
            #     if(args.verbose):
            #         return common.format_json_object(output)
            #     fmtoutput = []
            #     for dsvp in output:
            #         if ('varrayMappings' in dsvp):
            #             for map in dsvp['varrayMappings']:
            #                 if('value' in map):
            #                     nhName = VirtualArray(
            #                         args.ip, args.port).varray_show(
            #                                             map['value'])['name']
            #
            #                 if('name' in map):
            #                     vdcName = VirtualDatacenterData(
            #                         args.ip, args.port).vdc_data_show(
            #                                             map['name'])['name']
            #                 map['vdc_varray'] = vdcName + ':' + nhName
            #
            #         fmtoutput.append(dsvp)
            #     if(args.long):
            #         from common import TableGenerator
            #         TableGenerator(
            #             fmtoutput,
            #             ['module/name', 'vdc_varray',
            #              'description']).printTable()
            #     else:
            #         from common import TableGenerator
            #         TableGenerator(fmtoutput, ['module/name','vdc_varray',
            #                                 'description']).printTable()


    except SOSError as e:
        common.format_err_msg_and_raise("list", "object vpool", e.err_text, e.err_code)



def objectvpool_parser(parent_subparser, common_parser):
    # main objectvpool parser
    parser = parent_subparser.add_parser('objectvpool',
                                        description='ECS ObjectVPool CLI usage',
                                        parents=[common_parser],
                                        conflict_handler='resolve',
                                        help='Operations on ObjectVPool')
    subcommand_parsers = parser.add_subparsers(help='Use One Of Commands')

    # create command parser
    create_parser(subcommand_parsers, common_parser)

    # add command parser
    add_parser(subcommand_parsers, common_parser)

    # remove command parser
    remove_parser(subcommand_parsers, common_parser)

    # delete command parser
    delete_parser(subcommand_parsers, common_parser)

    # update command parser
    update_parser(subcommand_parsers, common_parser)

    # list command parser
    list_parser(subcommand_parsers, common_parser)

    # show command parser
    show_parser(subcommand_parsers, common_parser)
