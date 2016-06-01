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
from virtualdatacenter import VirtualDatacenter


class VirtualArray(object):

    '''
    The class definition for operations on 'VirtualArray'.
    '''

    # Commonly used URIs for the 'varrays' module
    URI_VIRTUALARRAY = '/vdc/data-services/varrays'

    def __init__(self, ipAddr, port, output_format=None):
        '''
        Constructor: takes IP address and port of the ECS instance.
        These are needed to make http requests for REST API
        '''
        self.__ipAddr = ipAddr
        self.__port = port
        self.__format = "json"
        if (output_format == "xml"):
            self.__format = "xml"

    ####################################################
    # gets the varray uri from name
    # raises an SOSError.NOT_FOUND_ERR if name is not found
    ####################################################
    def varray_query(self, name):
        '''
        Returns the UID of the varray specified by the name
        '''
        if (common.is_uri(name)):
            return name

        res = self.varray_list()
        vlist = res['varray']
        print("JMC: " + str(vlist))

        #array of dictionary items
        for v in vlist:
            if(v['name'] == name):
                return v['id']

        raise SOSError(SOSError.NOT_FOUND_ERR,
                       "varray " + name + ": not found")

    ####################################################
    # vdcname is the varray uri. It is not the common name
    ####################################################
    def varray_list(self, vdcname=None):
        xml = False
        if self.__format == "xml":
            xml = True

        uri = ""
        if(vdcname != None):
            uri = VirtualArray.URI_VIRTUALARRAY + "/" + vdcname
        else:
            uri = VirtualArray.URI_VIRTUALARRAY

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "GET", uri, None, None, xml)

        if(self.__format == "json"):
            o = common.json_decode(s)
            return o
        return s
     
    ####################################################
    # label - common user name
    ####################################################
    def varray_create(self, label, isProtected, description):
        #first check to see if the varray already exists. It will throw and exception
        #if it does NOT. So the varray can then be created with that name/label
        try:
            check = self.varray_query(label)

        # normal/good processing would go into this exception handling.
        # if the error is NOT_FOUND_ERR. That is good.
        # other exceptions...bad
        except SOSError as e:
            if(e.err_code == SOSError.NOT_FOUND_ERR):
                parms = {
                    'name':label,
                    'isProtected': isProtected,
                    'description': description
                }

                body = None
                if (parms):
                    body = json.dumps(parms)

                xml = False
                if self.__format == "xml":
                    xml = True

                (s, h) = common.service_json_request(
                    self.__ipAddr, self.__port, "POST",
                    VirtualArray.URI_VIRTUALARRAY, body, None, xml)

                if(self.__format == "json"):
                    o = common.json_decode(s)
                    return o
                return s

            else:
                raise e

        if(check):
            raise SOSError(SOSError.ENTRY_ALREADY_EXISTS_ERR,
                           "varray with name " + label + " already exists")


    ####################################################
    # (args.currentname, args.uri, args.newname, args.isProtected, args.description)
    # cname and uri are mutually exclusive args
    # protect - currently required. In ECS 1.3 if None is passed in, then the original value will be retrieved and used
    # description - currently required. In ECS 1.3 if None is passed in, then the original value will be retrieved and used
    ####################################################
    def varray_update(self, cname, arrayuri, newname, protect, desc):
        #if cname is None, then you have the arrayuri, but you might need the original varray name
        #if it's not changing
        if cname is None:
            varray_info = self.varray_list(arrayuri)
            cname = varray_info['name']
        else:
            arrayuri = self.varray_query(cname)

        #the name is NOT changing so use the original name
        if newname is None:
            newname = cname

        parms = {
            'name': newname,
            'isProtected': protect,
            'description': desc
        }

        body = json.dumps(parms)

        xml = False
        if self.__format == "xml":
            xml = True

        uri = VirtualArray.URI_VIRTUALARRAY+ "/" + arrayuri
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port, "PUT",
            uri, body, None, xml)

        if(self.__format == "json"):
            o = common.json_decode(s)
            return common.format_json_object(o)
        return s


    ####################################################
    #
    ####################################################
    def varray_delete(self, label):
        '''
        Makes a REST API call to delete a varray by its UUID
        '''
        uri = self.varray_query(label)
        body = None
     
        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port, "DELETE",
            VirtualArray.URI_VIRTUALARRAY + "/" + uri,
            body, None, xml)


        if(self.__format == "json"):
            o = common.json_decode(s)
            return common.format_json_object(o)
        return s


####################################################
#
####################################################
def create_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'create',
        description='ECS varray Create CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Create a varray')

    mandatory_args = create_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-name',
                                help='Name of varray',
                                metavar='<varrayname>',
                                dest='name',
                                required=True)


    create_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    create_parser.add_argument('-isProtected', '-protect',
                        metavar='<isProtected>', dest='isProtected',
                        help='true or false whether the varray has native protection',
                        choices=['true', 'false'],
                        default="false")

    create_parser.add_argument('-description', '-d',
                        metavar='<description>', dest='description',
                        help='user help description',
                        default="")

    create_parser.set_defaults(func=varray_create)


####################################################
#
####################################################
def varray_create(args):
    obj = VirtualArray(args.ip, args.port, args.format)
    try:
        return obj.varray_create(args.name, args.isProtected, args.description)
    except SOSError as e:
        common.format_err_msg_and_raise("create", "varray",
                                        e.err_text, e.err_code)


####################################################
#
####################################################
def delete_parser(subcommand_parsers, common_parser):
    # delete command parser
    delete_parser = subcommand_parsers.add_parser(
        'delete',
        description='ECS varray Delete CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Delete a varray')

    mandatory_args = delete_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-name',
                                help='name (or uri) of varray. uri will be used directly. name will be used to retrieve uri',
                                dest='name',
                                required=True)

    delete_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    delete_parser.set_defaults(func=varray_delete)

####################################################
#
####################################################
def varray_delete(args):
    obj = VirtualArray(args.ip, args.port, args.format)
    try:
        res = obj.varray_delete(args.name)
        return res
    except SOSError as e:
        common.format_err_msg_and_raise("delete", "varray",
                                        e.err_text, e.err_code)


####################################################
#
####################################################
def query_parser(subcommand_parsers, common_parser):
    # query command parser
    query_parser = subcommand_parsers.add_parser(
        'query',
        description='ECS varray Query CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Query a varray')

    mandatory_args = query_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                help='name of varray',
                                dest='name',
                                metavar='<varrayname>',
                                required=True)

    query_parser.set_defaults(func=varray_query)

####################################################
#
####################################################
def varray_query(args):
    obj = VirtualArray(args.ip, args.port)
    try:
        res = obj.varray_query(args.name)
        return res
    except SOSError as e:
        common.format_err_msg_and_raise("query", "varray",
                                        e.err_text, e.err_code)

####################################################
#
####################################################
def list_parser(subcommand_parsers, common_parser):
    # list command parser
    list_parser = subcommand_parsers.add_parser(
        'list',
        description='ECS varray List CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='List of varrays')

    list_parser.add_argument('-uri', '-uri',
        help='varray uri',
        dest='uri')

    list_parser.add_argument('-format', '-fm',
                        dest='format',
                        help='Response: xml, json, text/plain',
                        choices=['xml', 'json', 'text/plain'],
                        default='json')

    list_parser.set_defaults(func=varray_list)


####################################################
#
####################################################
def varray_list(args):
    obj = VirtualArray(args.ip, args.port, args.format)

    try:
        return obj.varray_list(args.uri)

    except SOSError as e:
        common.format_err_msg_and_raise("list", "varray",
                                        e.err_text, e.err_code)


####################################################
#
####################################################
def update_parser(subcommand_parsers, common_parser):
    # update command parser
    update_parser = subcommand_parsers.add_parser(
        'update',
        description='ECS update varray CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='update a varray')

    mandatory_args = update_parser.add_mutually_exclusive_group(required=True)

    #should be able to input the uri or the old name which will be converted to the uri
    mandatory_args.add_argument('-currentname', '-cn',
                                help='current name of varray. Either this or uri is required',
                                dest='currentname')

    mandatory_args.add_argument('-uri', '-uri',
                                help='current uri of varray. Either this or current name is required',
                                dest='uri') 



    update_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    update_parser.add_argument('-newname', '-nn',
                        dest='newname',
                        help='new name if the varray is being renamed',
                        default=None)

    update_parser.add_argument('-isProtected', '-protect',
                        metavar='<isProtected>', dest='isProtected',
                        help='true or false whether the varray has native protection. Will default to current value',
                        choices=['true', 'false'], required=True,
                        default=None)

    update_parser.add_argument('-description', '-d',
                        metavar='<description>', dest='description',
                        help='general description of varray usage', required=True,
                        default=None)

    update_parser.set_defaults(func=varray_update)

####################################################
#
####################################################
def varray_update(args):
    obj = VirtualArray(args.ip, args.port, args.format)
    try:
        return obj.varray_update(args.currentname, args.uri, args.newname, args.isProtected, args.description)
    except SOSError as e:
        common.format_err_msg_and_raise("update", "varray",
                                        e.err_text, e.err_code)


#
# varray Main parser routine
#
####################################################
#
####################################################
def varray_parser(parent_subparser, common_parser):
    # main varray parser
    parser = parent_subparser.add_parser('varray',
                                         description='ECS varray CLI usage',
                                         parents=[common_parser],
                                         conflict_handler='resolve',
                                         help='Operations on varray')
    subcommand_parsers = parser.add_subparsers(help='Use One Of Commands')

    # create command parser
    create_parser(subcommand_parsers, common_parser)

    # update command parser
    update_parser(subcommand_parsers, common_parser)

    # delete command parser
    delete_parser(subcommand_parsers, common_parser)

    # list command parser
    list_parser(subcommand_parsers, common_parser)
