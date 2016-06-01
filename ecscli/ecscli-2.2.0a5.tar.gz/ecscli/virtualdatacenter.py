'''
Created on Apr 1, 2014

@author: bonduj
'''

import json
import common
import sys

from common import SOSError
from common import TableGenerator


class VirtualDatacenter(object):

    URI_SERVICES_BASE = '/object/vdcs'
    URI_VDC   = URI_SERVICES_BASE + '/vdc'
    URI_VDCID = URI_SERVICES_BASE + '/vdcid'
    URI_VDC_LOCAL = URI_VDC + '/local'
    URI_VDC_LOCAL_SECRETKEY = URI_VDC_LOCAL + '/secretkey'


    ####################################################
    #
    ####################################################
    def __init__(self, ipAddr, port, output_format = None):
        '''
        Constructor: takes IP address and port of the ECS instance.
        These are needed to make http requests for REST API
        '''
        self.__ipAddr = ipAddr
        self.__port = port
        self.__format = 'json'
        if(output_format == 'xml'):
            self.__format = 'xml'


    ####################################################
    #
    ####################################################
    def vdc_insert(self, name, endpoint, key):
        parms = {
            'vdcName': name,
            'interVdcEndPoints': endpoint,
            'secretKeys': key
        }

        uri = VirtualDatacenter.URI_VDC + "/" + name
        body = json.dumps(parms)
        print("JMC body: " + body)
        (s, h) = common.service_json_request(self.__ipAddr,
                                             self.__port,
                                             "PUT",
                                             uri,
                                             body, None, 'json')


    ####################################################
    #
    ####################################################
    def vdc_get_id_from_name(self, name):
        vdc_info = vdc_show(name)
        return vdc_info['vdcId']



    ####################################################
    #
    ####################################################
    def vdc_delete(self, name, vdcid):
        if name:
           vdcid = self.vdc_get_id_from_name(name)

        
        uri = VirtualDatacenter.URI_VDCID + '/' + vdcid + '/deactivate'
        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                    "POST",
                                    uri,
                                    None, None, 'json')
        return common.json_decode(s)


    ####################################################
    #
    ####################################################
    def vdc_show(self, name=None, vdcid=None):
        if name:
            uri = VirtualDatacenter.URI_VDC + '/' + name
        else:
            uri = VirtualDatacenter.URI_VDCID + '/' + vdcid

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr,
                                             self.__port,
                                             "GET",
                                             uri, None, None, xml)
        if(self.__format == "json"):
            o = common.json_decode(s)
            #print(common.format_json_object(o))  #this takes a json object and returns a string
            return o
        return s

    ####################################################
    #
    ####################################################
    def vdc_get_secretkey(self):
        uri = VirtualDatacenter.URI_VDC_LOCAL_SECRETKEY

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr,
                                             self.__port,
                                             "GET",
                                             uri, None, None, xml)
        if(self.__format == "json"):
            o = common.json_decode(s)
            #print(common.format_json_object(o))  #this takes a json object and returns a string
            return o
        return s


    ####################################################
    #
    ####################################################
    def vdc_get_local(self):
        uri = VirtualDatacenter.URI_VDC_LOCAL

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr,
                                             self.__port,
                                             "GET",
                                             uri, None, None, xml)
        if(self.__format == "json"):
            o = common.json_decode(s)
            #print(common.format_json_object(o))  #this takes a json object and returns a string
            return o
        return s

    ####################################################
    #
    ####################################################
    def vdc_list(self):
        uri = VirtualDatacenter.URI_VDC + '/list'

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr,
                                             self.__port,
                                             "GET",
                                             uri, None, None, xml)
        if(self.__format == "json"):
            o = common.json_decode(s)
            #print(common.format_json_object(o))  #this takes a json object and returns a string
            return o
        return s

    ####################################################
    #
    ####################################################
    def vdc_query(self, name):
        vdcId = None
        l = self.vdc_list()
        vdcList = l['vdc']
        for vdc in vdcList:
            if vdc['name'] == name:
                vdcId = vdc['id']
                break
        return vdcId

####################################################
#
####################################################
def vdc_list_parser(subcommand_parsers, common_parser):
    # get vdc's command parser
    vdc_list_parser = subcommand_parsers.add_parser('list',
                description='ECS list VirtualDataCenters CLI usage',
                parents=[common_parser],
                conflict_handler='resolve',
                help='retrieves the secret key of the local VirtualDataCenters')

    vdc_list_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    vdc_list_parser.set_defaults(func=vdc_list)


####################################################
#
####################################################
def vdc_list(args):
    obj = VirtualDatacenter(args.ip, args.port, args.format)
    try:
        result = obj.vdc_list()
        return result
    except SOSError as e:
        common.format_err_msg_and_raise("vdc_get_secretkey", "vdc",
                                        e.err_text, e.err_code)


####################################################
#
####################################################
def vdc_secretKey_parser(subcommand_parsers, common_parser):
    # get vdc's command parser
    vdc_secretkey_parser = subcommand_parsers.add_parser('get_secretkey',
                description='ECS VirtualDataCenter get secret key CLI usage',
                parents=[common_parser],
                conflict_handler='resolve',
                help='retrieves the secret key of the local VirtualDataCenters')

    vdc_secretkey_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    vdc_secretkey_parser.set_defaults(func=vdc_get_secretkey)


####################################################
#
####################################################
def vdc_get_secretkey(args):
    obj = VirtualDatacenter(args.ip, args.port, args.format)
    try:
        result = obj.vdc_get_secretkey()
        return result 
    except SOSError as e:
        common.format_err_msg_and_raise("vdc_get_secretkey", "vdc",
                                        e.err_text, e.err_code)


####################################################
#
####################################################
def vdc_local_parser(subcommand_parsers, common_parser):
    # get vdc's command parser
    vdc_local_parser = subcommand_parsers.add_parser('get_local',
                description='ECS get local VirtualDataCenter CLI usage',
                parents=[common_parser],
                conflict_handler='resolve',
                help='retrieves the local VirtualDataCenter info')

    vdc_local_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")
    
    vdc_local_parser.set_defaults(func=vdc_get_local)
                 
                 
####################################################
#                           
####################################################
def vdc_get_local(args):
    obj = VirtualDatacenter(args.ip, args.port, args.format)
    try:                        
        result = obj.vdc_get_local()
        return result
    except SOSError as e:
        common.format_err_msg_and_raise("vdc_get_local", "vdc",
                                        e.err_text, e.err_code)

####################################################
#
####################################################
def vdc_insert_parser(subcommand_parsers, common_parser):
    # add command parser
    vdc_insert_parser = subcommand_parsers.add_parser('insert',
                 description='ECS VirtualDataCenter insert CLI usage',
                 parents=[common_parser],
                 conflict_handler='resolve',
                 help='adding a New VirtualDataCenter \
                            to Existing ECS Geo System')
    mandatory_args = vdc_insert_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-name', '-n',
                                help='Name of VirtualDataCenter',
                                dest='name',
                                required=True)
    mandatory_args.add_argument('-key', '-k',
                                help='the secure key of the VirtualDataCenter',
                                dest='key',
                                required=True)
    mandatory_args.add_argument('-endpoint', '-ep',
                            help='the VIP of VirtualDataCenter to be added',
                            dest='endpoint',
                            required=True)
    vdc_insert_parser.set_defaults(func=vdc_insert)

####################################################
#
####################################################
def vdc_insert(args):
    try:
        obj = VirtualDatacenter(args.ip, args.port)
        obj.vdc_insert(args.name, args.endpoint, args.key)
    except SOSError as e:
        common.format_err_msg_and_raise("insert", "vdc",
                                        e.err_text, e.err_code)


####################################################
#
####################################################
def vdc_show_parser(subcommand_parsers, common_parser):
    # get vdc's command parser
    vdc_show_parser = subcommand_parsers.add_parser('show',
                description='ECS VirtualDataCenter list CLI usage',
                parents=[common_parser],
                conflict_handler='resolve',
                help='retrieves the list of VirtualDataCenters')

    mandatory_args = vdc_show_parser.add_mutually_exclusive_group(required=True)

    #should be able to input the uri or the old name which will be converted to the uri
    mandatory_args.add_argument('-name', '-name',
                                help='name of vdc. Either this or vdc id is required',
                                dest='name')
    mandatory_args.add_argument('-vdcid', '-vdcid',
                                help='current id of vdc. Either this or current name is required',
                                dest='vdcid')

    vdc_show_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    vdc_show_parser.set_defaults(func=vdc_show)


####################################################
#
####################################################
def vdc_show(args):
    obj = VirtualDatacenter(args.ip, args.port, args.format)
    try:
        result = obj.vdc_show(args.name, args.vdcid)
        return result 
    except SOSError as e:
        common.format_err_msg_and_raise("show", "vdc",
                                        e.err_text, e.err_code)

####################################################
#
####################################################
def vdc_delete_parser(subcommand_parsers, common_parser):
    # add command parser
    vdc_delete_parser = subcommand_parsers.add_parser('delete',
                    description='ECS VirtualDataCenter delete CLI usage',
                    parents=[common_parser],
                    conflict_handler='resolve',
                    help='delete to VirtualDataCenter from ECS Geo System')

    mandatory_args = vdc_delete_parser.add_mutually_exclusive_group(required=True)
    mandatory_args.add_argument('-vdcid', '-vdcid',
                                help='uri id of VirtualDataCenter',
                                dest='vdcid')
    mandatory_args.add_argument('-name', '-name',
                                help='common name of VirtualDataCenter',
                                dest='name')
    vdc_delete_parser.set_defaults(func=vdc_delete)


####################################################
#
####################################################
def vdc_delete(args):
    try:
        return VirtualDatacenter(args.ip, args.port).vdc_delete(args.name, args.vdcid)
    except SOSError as e:
        common.format_err_msg_and_raise("delete", "vdc",
                                        e.err_text, e.err_code)
#
# Host Main parser routine
#
####################################################
#
####################################################
def vdc_parser(parent_subparser, common_parser):

    parser = parent_subparser.add_parser('vdc',
                    description='ECS virtualdatacenter CLI usage',
                    parents=[common_parser],
                    conflict_handler='resolve',
                    help='Operations on VirtualDataCenter')
    subcommand_parsers = parser.add_subparsers(
        help='use one of sub-commands')

    # add command parser
    vdc_insert_parser(subcommand_parsers, common_parser)
    # show command parser
    vdc_show_parser(subcommand_parsers, common_parser)
    # delete command parser
    vdc_delete_parser(subcommand_parsers, common_parser)

    vdc_secretKey_parser(subcommand_parsers, common_parser)
    vdc_local_parser(subcommand_parsers, common_parser)
    vdc_list_parser(subcommand_parsers, common_parser)

