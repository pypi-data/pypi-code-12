'''
Created on September 12, 2014

@author: edpugr
'''

import json
import common
import sys

from common import SOSError
from common import TableGenerator


class VirtualDatacenterData(object):

    URI_SERVICES_BASE = ''
    URI_VDC = URI_SERVICES_BASE + '/vdc'

    URI_VDCINFO                 =  '/object/vdcs'
    URI_VDCINFO_GET             = URI_VDCINFO    + '/vdc' + '/{0}'
    URI_VDCINFO_URI_GET             = URI_VDCINFO    + '/vdcid' + '/{0}'

    URI_VDCINFO_INSERT =  URI_VDCINFO_GET
    URI_VDCINFO_LOCAL = URI_VDCINFO + '/vdc/local'
    URI_VDCINFO_LIST = URI_VDCINFO + '/vdc/list'

    VIRTUAL_DATACENTER_ROLES = ['SYSTEM_ADMIN',
                                'PROJECT_ADMIN',
                                'TENANT_ADMIN',
                                'SECURITY_ADMIN']

    def __init__(self, ipAddr, port, output_format=None):
        '''
        Constructor: takes IP address and port of the ECS instance.
        These are needed to make http requests for REST API
        '''
        self.__ipAddr = ipAddr
        self.__port = port
        self.__format = "json"
        if (output_format == 'xml'):
            self.__format = "xml"

    # add a vdc_data to ECS Geo env
    def vdc_data_add(self, name, secretkey, dataEndpoint, cmdEndpoint):
        parms = {
            'vdcName'            : name,
            'dataEndPoints'      : dataEndpoint,
            'cmdEndPoints'       : cmdEndpoint,
            'secretKeys'         : secretkey,
        }

        body = json.dumps(parms)

        (s, h) = common.service_json_request(self.__ipAddr,
                                             self.__port,
                                             "PUT",
                                             VirtualDatacenterData.URI_VDCINFO_INSERT.format(name),
                                             body)

    # vdc data show in a ECS Geo env
    def vdc_data_show(self, args):
        if (args.name is not None):
            uri = VirtualDatacenterData.URI_VDCINFO_GET.format(args.name)
        else:
            uri = VirtualDatacenterData.URI_VDCINFO_URI_GET.format(args.vdcId)

        print("JMC uri: " + uri)
        xml = False
        if self.__format == "xml":
            xml = True
        (s, h) = common.service_json_request(self.__ipAddr,
                            self.__port,
                            "GET",
                            VirtualDatacenterData.URI_VDCINFO_URI_GET.format(uri),
                            None, None, xml)

        if (self.__format == "json"):
            o = common.json_decode(s)
            return o
        return s


    # show vdc_data details
    def vdc_data_get_local(self, xml=False):

        (s, h) = common.service_json_request(self.__ipAddr,
                            self.__port,
                            "GET",
                            VirtualDatacenterData.URI_VDCINFO_LOCAL,
                            None, None)
        o = common.json_decode(s)
        inactive = common.get_node_value(o, 'inactive')

        if(inactive == True):
            return None
        if(xml == True):
            (s, h) = common.service_json_request(self.__ipAddr,
                            self.__port,
                            "GET",
                            VirtualDatacenterData.URI_VDCINFO_LOCAL,
                            None, None, xml)
            return s
        else:
            return o


    def vdc_data_get_list(self):
        xml = False
        if self.__format == "xml":
            xml = True
        (s, h) = common.service_json_request(self.__ipAddr,
                                             self.__port,
                                             "GET",
                                             VirtualDatacenterData.URI_VDCINFO_LIST,
                                             None, None, xml)

        if (self.__format == "json"):
            o = common.json_decode(s)
            return o
        return s

# Start Parser definitions


'''
Preprocessor for the vdc_data add operation
'''

def vdc_data_add_parser(subcommand_parsers, common_parser):
    # add command parser
    add_parser = subcommand_parsers.add_parser('insert',
                 description='ECS Data VirtualDataCenter insert CLI usage',
                 parents=[common_parser],
                 conflict_handler='resolve',
                 help='adding a New VirtualDataCenter \
                            to Existing ECS Geo System')
    mandatory_args = add_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-name', '-n',
                                help='Name of VirtualDataCenter',
                                metavar='<vdc_dataname>',
                                dest='name',
                                required=True)
    mandatory_args.add_argument('-key', '-k',
                                help='the secure key of the VirtualDataCenter',
                                dest='key',
                                metavar='<key>',
                                required=True)
    mandatory_args.add_argument('-dataip', '-dip',
                            help='the IP of the Geo data endpoint to be added',
                            dest='dataip',
                            metavar='<dataip>',
                            required=True)
    mandatory_args.add_argument('-cmdip', '-cip',
                            help='the IP of the Geo Commands endpoint',
                            dest='cmdip',
                            metavar='<cmdip>',
                            required=True)

    add_parser.set_defaults(func=vdc_data_add)



def vdc_data_add(args):
    try:
        VirtualDatacenterData(args.ip, args.port).vdc_data_add(
            args.name, args.key, args.dataip, args.cmdip)
    except SOSError as e:
        common.format_err_msg_and_raise("add", "vdc_data",
                                        e.err_text, e.err_code)


'''
Preprocessor for the vdc_data list operation
'''


def vdc_data_list_parser(subcommand_parsers, common_parser):
    # list vdc_data's command parser
    list_parser = subcommand_parsers.add_parser('list',
                description='ECS Data VirtualDataCenter list CLI usage',
                parents=[common_parser],
                conflict_handler='resolve',
                help='retrieves the list of VirtualDataCenters')

    list_parser.add_argument('-format', '-f',
                             metavar='<format>', dest='format',
                             help='response format: xml or json (default:json)',
                             choices=['xml', 'json'],
                             default="json")

    list_parser.set_defaults(func=vdc_data_list)


def vdc_data_list(args):
    vdc_dataob = VirtualDatacenterData(args.ip, args.port)
    try:
        vdc_datalist = vdc_dataob.vdc_data_get_list()
        return vdc_datalist

    except SOSError as e:
        common.format_err_msg_and_raise("list", "vdc_data",
                                        e.err_text, e.err_code)
'''
Preprocessor for the vdc_data show operation
'''

def vdc_data_show_parser(subcommand_parsers, common_parser):
    # show command parser
    show_parser = subcommand_parsers.add_parser('show',
                    description='ECS Data VirtualDataCenter show CLI usage',
                    parents=[common_parser],
                    conflict_handler='resolve',
                    help='show VirtualDataCenter details')

    show_parser.add_argument('-format', '-f',
                             metavar='<format>', dest='format',
                             help='response format: xml or json (default:json)',
                             choices=['xml', 'json'],
                             default="json")

    arggroup = show_parser.add_mutually_exclusive_group(required=True)
    arggroup.add_argument('-name', '-n',
                          help='Name of virtual datacenter',
                          dest='name')
    arggroup.add_argument('-vdcId', '-id',
                          help='id of the virtual datacenter',
                          dest='vdcId')

    show_parser.set_defaults(func=vdc_data_show)


def vdc_data_show(args):
    try:
        res = VirtualDatacenterData(args.ip, args.port).vdc_data_show(args)
        return res

    except SOSError as e:
        common.format_err_msg_and_raise("show", "vdc_data", e.err_text,
                                        e.err_code)


'''
Preprocessor for the vdc_data local operation
'''

def vdc_data_local_parser(subcommand_parsers, common_parser):
    # local command parser
    show_parser = subcommand_parsers.add_parser('local',
                    description='ECS Data VirtualDataCenter local CLI usage',
                    parents=[common_parser],
                    conflict_handler='resolve',
                    help='local VirtualDataCenter details')
    show_parser.add_argument('-xml',
                             dest='xml',
                             action='store_true',
                             help='XML response')

    show_parser.set_defaults(func=vdc_data_get_local)


def vdc_data_get_local(args):
    try:
        res = VirtualDatacenterData(args.ip, args.port).vdc_data_get_local(args.xml)
        if(res):
            if(args.xml == True):
                return common.format_xml(res)
            else:
                return common.format_json_object(res)
    except SOSError as e:
        common.format_err_msg_and_raise("local", "vdc_data", e.err_text,
                                        e.err_code)


#
# Data Vdc Main parser routine
#


def vdc_data_parser(parent_subparser, common_parser):

    parser = parent_subparser.add_parser('vdc_data',
                    description='ECS Data Virtualdatacenter CLI usage',
                    parents=[common_parser],
                    conflict_handler='resolve',
                    help='Operations on VirtualDataCenter')
    subcommand_parsers = parser.add_subparsers(
        help='use one of sub-commands')

    # add command parser
    vdc_data_add_parser(subcommand_parsers, common_parser)
    # list command parser
    vdc_data_list_parser(subcommand_parsers, common_parser)
    # show command parser
    vdc_data_show_parser(subcommand_parsers, common_parser)
    # local command parser
    vdc_data_local_parser(subcommand_parsers, common_parser)

