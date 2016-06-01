# copyright (c) 2013 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.


from argparse import ArgumentParser
from common import SOSError
import common
import json
import os

class Nodes(object):
    URI_NODES_BASE     = '/vdc/nodes'

    ######################################################
    #
    ######################################################
    def __init__(self, ipAddr, port, output_format):

        '''
        Constructor: takes IP address and port of the ECS instance.
        These are needed to make http requests for REST API
        '''
        self.__ipAddr = ipAddr
        self.__port = port
        self.__format = "json"
        if (output_format == 'xml'):
           self.__format = "xml"

    ######################################################
    #
    ######################################################
    def get_nodes(self):
        url = ''
        if(self.__format == "json"):
            url = Nodes.URI_NODES_BASE + ".json"
        else:
            url = Nodes.URI_NODES_BASE

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "GET",
                                             url,
                                             None)
        if(self.__format == "json"):
            o = common.json_decode(s)
            return common.format_json_object(o)
        return s

######################## END CLASS ##############################

######################################################
#
######################################################
def get_nodes(args):
    try:
        obj = Nodes(args.ip, args.port, args.format)

        res = obj.get_nodes()
        return res

    except SOSError as e:
        common.format_err_msg_and_raise(
            "list",
            "nodes",
            e.err_text,
            e.err_code)

######################################################
#
######################################################
def get_nodes_parser(subcommand_parsers, common_parser):
    get_nodes_parser = subcommand_parsers.add_parser(
        'list', description='get list of ECS datanodes information',
        parents=[common_parser],
        conflict_handler='resolve',
        help='get ECS nodes')

    get_nodes_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    get_nodes_parser.set_defaults(func=get_nodes)



######################################################
#this is the main parent parser for cas
######################################################
def nodes_parser(parent_subparser, common_parser):
    parser = parent_subparser.add_parser(
        'nodes',
        description='get ECS nodes info ',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Operations to retrieve ECS datanodes information')
    subcommand_parsers = parser.add_subparsers(help='use one of sub-commands')

    get_nodes_parser(subcommand_parsers, common_parser)

