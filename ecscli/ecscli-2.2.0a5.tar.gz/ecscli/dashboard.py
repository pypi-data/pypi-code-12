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


class Dashboard(object):

    '''
    The class definition for operations on 'Dashboard'.
    '''

    # Commonly used URIs
    URI_SERVICES_BASE = ''
    URI_DASHBOARD = URI_SERVICES_BASE + '/dashboard'

    URI_DASHBOARD_LOCAL_ZONE = URI_DASHBOARD + '/zones/localzone'
    URI_DASHBOARD_LOCAL_REPGROUPS = URI_DASHBOARD_LOCAL_ZONE + '/replicationgroups'
    URI_DASHBOARD_LOCAL_RGLINKSFAILED = URI_DASHBOARD_LOCAL_ZONE + '/rglinksFailed'
    URI_DASHBOARD_LOCAL_STORAGEPOOLS = URI_DASHBOARD_LOCAL_ZONE + '/storagepools'
    URI_DASHBOARD_LOCAL_NODES = URI_DASHBOARD_LOCAL_ZONE + '/nodes'

    URI_DASHBOARD_STORAGEPOOLS = URI_DASHBOARD + '/storagepools/{0}'
    URI_DASHBOARD_NODES = URI_DASHBOARD + '/nodes/{0}'
    URI_DASHBOARD_DISKS = URI_DASHBOARD + '/disks/{0}'
    URI_DASHBOARD_PROCESSES = URI_DASHBOARD + '/processes/{0}'
    URI_DASHBOARD_NODEPROCESSES = URI_DASHBOARD + '/nodes/{0}/processes'
    URI_DASHBOARD_NODEDISKS = URI_DASHBOARD + '/nodes/{0}/disks'
    URI_DASHBOARD_STORAGEPOOL_NODES = URI_DASHBOARD + '/storagepools/{0}/nodes'
    URI_DASHBOARD_LOCAL_RGLINKSBOOT = URI_DASHBOARD_LOCAL_ZONE + '/rglinksBootstrap'
    URI_DASHBOARD_REPGROUP = URI_DASHBOARD + '/replicationgroups/{0}'
    URI_DASHBOARD_RGLINKS = URI_DASHBOARD + '/rglinks/{0}'
    URI_DASHBOARD_REPGROUP_LINKS = URI_DASHBOARD + '/replicationgroups/{0}/rglinks'


    ###################################################
    #
    ###################################################
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


    ###################################################
    #
    ###################################################
    def list(self, uri, id = None):

        xml = False
        if self.__format == "xml":
            xml = True

        #uri = Dashboard.URI_DASHBOARD_ZONES
        if (id is not None):
            uri.format(id)

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "GET",
                                             uri, None, None, xml)
        if(self.__format == "json"):
            o = common.json_decode(s)
            return o
        return s


##########################################################
#
##########################################################
def list_dash_localzone_parser(subcommand_parsers, common_parser):
    # list localzone command parser
    list_dash_localzone_parser = subcommand_parsers.add_parser(
        'list-localzone',
        description='ECS List localzone CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='list namespace')

    list_dash_localzone_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    list_dash_localzone_parser.set_defaults(func=list_dash_localzone)

##########################################################
#
##########################################################
def list_dash_localzone(args):

    obj = Dashboard(args.ip, args.port, args.format)
    try:
        return obj.list(Dashboard.URI_DASHBOARD_LOCAL_ZONE)
    except SOSError as e:
        raise e

##########################################################
#
##########################################################
def list_dash_lzrepgroup_parser(subcommand_parsers, common_parser):
    # list localzone command parser
    list_dash_lzrepgroup_parser = subcommand_parsers.add_parser(
        'list-lzrepgroup',
        description='ECS List localzone CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='list localzone replication groups')

    list_dash_lzrepgroup_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    list_dash_lzrepgroup_parser.set_defaults(func=list_dash_lzrepgroups)
##########################################################
#
##########################################################
def list_dash_lzrepgroups(args):

    obj = Dashboard(args.ip, args.port, args.format)
    try:
        return obj.list(Dashboard.URI_DASHBOARD_LOCAL_REPGROUPS)
    except SOSError as e:
        raise e

##########################################################
#
##########################################################
def list_dash_lzrglinksfailed_parser(subcommand_parsers, common_parser):
    # list localzone command parser
    list_dash_lzrglinksfailed_parser = subcommand_parsers.add_parser(
        'list-lzrglinksfailed',
        description='ECS List localzone CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='list localzone failed rglinks')

    list_dash_lzrglinksfailed_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    list_dash_lzrglinksfailed_parser.set_defaults(func=list_dash_lzrglinksfailed)
##########################################################
#
##########################################################
def list_dash_lzrglinksfailed(args):

    obj = Dashboard(args.ip, args.port, args.format)
    try:
        return obj.list(Dashboard.URI_DASHBOARD_LOCAL_RGLINKSFAILED)
    except SOSError as e:
        raise e

##########################################################
#
##########################################################
def list_dash_lzstoragepools_parser(subcommand_parsers, common_parser):
    # list localzone command parser
    list_dash_lzstoragepools_parser = subcommand_parsers.add_parser(
        'list-lzstoragepools',
        description='ECS List localzone storage pools CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='list namespace')

    list_dash_lzstoragepools_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    list_dash_lzstoragepools_parser.set_defaults(func=list_dash_lzstoragepools)
##########################################################
#
##########################################################
def list_dash_lzstoragepools(args):

    obj = Dashboard(args.ip, args.port, args.format)
    try:
        return obj.list(Dashboard.URI_DASHBOARD_LOCAL_STORAGEPOOLS)
    except SOSError as e:
        raise e

##########################################################
#
##########################################################
def list_dash_lznodes_parser(subcommand_parsers, common_parser):
    # list localzone command parser
    list_dash_lznodes_parser = subcommand_parsers.add_parser(
        'list-lznodes',
        description='ECS List localzone nodes CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='list local zone nodes')

    list_dash_lznodes_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    list_dash_lznodes_parser.set_defaults(func=list_dash_lznodes)

##########################################################
#
##########################################################
def list_dash_lznodes(args):

    obj = Dashboard(args.ip, args.port, args.format)
    try:
        return obj.list(Dashboard.URI_DASHBOARD_LOCAL_NODES)
    except SOSError as e:
        raise e

##########################################################
#
##########################################################
def list_dash_storagepools_parser(subcommand_parsers, common_parser):
    # list localzone command parser
    list_dash_storagepools_parser= subcommand_parsers.add_parser(
        'list-storagepools',
        description='ECS List localzone CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='list namespace')

    mandatory_args = list_dash_storagepools_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-id', '-id',
                             help='Storage pools id',
                             default=None,
                             metavar='<id>',
                             dest='id',
                             required=True)

    list_dash_storagepools_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    list_dash_storagepools_parser.set_defaults(func=list_dash_storagepools)

##########################################################
#
##########################################################
def list_dash_storagepools(args):

    obj = Dashboard(args.ip, args.port, args.format)
    try:
        return obj.list(Dashboard.URI_DASHBOARD_STORAGEPOOLS.format(args.id))
    except SOSError as e:
        raise e

##########################################################
#
##########################################################
def list_dash_nodes_parser(subcommand_parsers, common_parser):
    # list localzone command parser
    list_dash_nodes_parser= subcommand_parsers.add_parser(
        'list-nodes',
        description='ECS List node details CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='list node details')

    mandatory_args = list_dash_nodes_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-id', '-id',
                             help='node id',
                             default=None,
                             metavar='<id>',
                             dest='id',
                             required=True)

    list_dash_nodes_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    list_dash_nodes_parser.set_defaults(func=list_dash_nodes)

##########################################################
#
##########################################################
def list_dash_nodes(args):

    obj = Dashboard(args.ip, args.port, args.format)
    try:
        return obj.list(Dashboard.URI_DASHBOARD_NODES.format(args.id))
    except SOSError as e:
        raise e

##########################################################
#
##########################################################
def list_dash_disk_parser(subcommand_parsers, common_parser):
    # list localzone command parser
    list_dash_disk_parser= subcommand_parsers.add_parser(
        'list-disk',
        description='ECS List disk details CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='list disk info')

    mandatory_args = list_dash_disk_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-id', '-id',
                             help='disk id',
                             default=None,
                             metavar='<id>',
                             dest='id',
                             required=True)

    list_dash_disk_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    list_dash_disk_parser.set_defaults(func=list_dash_disk)

##########################################################
#
##########################################################
def list_dash_disk(args):

    obj = Dashboard(args.ip, args.port, args.format)
    try:
        return obj.list(Dashboard.URI_DASHBOARD_DISKS.format(args.id))
    except SOSError as e:
        raise e

##########################################################
#
##########################################################
def list_dash_process_parser(subcommand_parsers, common_parser):
    # list localzone command parser
    list_dash_process_parser= subcommand_parsers.add_parser(
        'list-process',
        description='ECS List process info CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='list process info')

    mandatory_args = list_dash_process_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-id', '-id',
                             help='process id',
                             default=None,
                             metavar='<id>',
                             dest='id',
                             required=True)

    list_dash_process_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    list_dash_process_parser.set_defaults(func=list_dash_process)

##########################################################
#
##########################################################
def list_dash_process(args):

    obj = Dashboard(args.ip, args.port, args.format)
    try:
        return obj.list(Dashboard.URI_DASHBOARD_PROCESSES.format(args.id))
    except SOSError as e:
        raise e

##########################################################
#
##########################################################
def list_dash_nodeprocesses_parser(subcommand_parsers, common_parser):
    # list localzone command parser
    list_dash_nodeprocesses_parser= subcommand_parsers.add_parser(
        'list-nodeprocesses',
        description='ECS List node processes CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='list node processes')

    mandatory_args = list_dash_nodeprocesses_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-id', '-id',
                             help='node id',
                             default=None,
                             metavar='<id>',
                             dest='id',
                             required=True)

    list_dash_nodeprocesses_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    list_dash_nodeprocesses_parser.set_defaults(func=list_dash_nodeprocesses)

##########################################################
#
##########################################################
def list_dash_nodeprocesses(args):

    obj = Dashboard(args.ip, args.port, args.format)
    try:
        return obj.list(Dashboard.URI_DASHBOARD_NODEPROCESSES.format(args.id))
    except SOSError as e:
        raise e

##########################################################
#
##########################################################
def list_dash_nodedisks_parser(subcommand_parsers, common_parser):
    # list localzone command parser
    list_dash_nodedisks_parser= subcommand_parsers.add_parser(
        'list-nodedisks',
        description="ECS List a node's disks CLI usage.",
        parents=[common_parser],
        conflict_handler='resolve',
        help='list node disks')

    mandatory_args = list_dash_nodedisks_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-id', '-id',
                             help='node id',
                             default=None,
                             metavar='<id>',
                             dest='id',
                             required=True)

    list_dash_nodedisks_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    list_dash_nodedisks_parser.set_defaults(func=list_dash_nodedisks)

##########################################################
#
##########################################################
def list_dash_nodedisks(args):

    obj = Dashboard(args.ip, args.port, args.format)
    try:
        return obj.list(Dashboard.URI_DASHBOARD_NODEDISKS.format(args.id))
    except SOSError as e:
        raise e

##########################################################
#
##########################################################
def list_dash_storagepoolnodes_parser(subcommand_parsers, common_parser):
    # list localzone command parser
    list_dash_storagepoolnodes_parser= subcommand_parsers.add_parser(
        'list-storagepoolnodes',
        description='ECS List storage pool nodes CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='list storage pool nodes')

    mandatory_args = list_dash_storagepoolnodes_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-id', '-id',
                             help='Storage pool id',
                             default=None,
                             metavar='<id>',
                             dest='id',
                             required=True)

    list_dash_storagepoolnodes_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    list_dash_storagepoolnodes_parser.set_defaults(func=list_dash_storagepoolnodes)

##########################################################
#
##########################################################
def list_dash_storagepoolnodes(args):

    obj = Dashboard(args.ip, args.port, args.format)
    try:
        return obj.list(Dashboard.URI_DASHBOARD_STORAGEPOOL_NODES.format(args.id))
    except SOSError as e:
        raise e

##########################################################
#
##########################################################
def list_dash_rglinksbootstrap_parser(subcommand_parsers, common_parser):
    # list localzone command parser
    list_dash_rglinksbootstrap_parser = subcommand_parsers.add_parser(
        'list-lzrglinkbootstrap',
        description='ECS List rglinks bootstrap link details CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='list rg links bootstrap details')

    list_dash_rglinksbootstrap_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    list_dash_rglinksbootstrap_parser.set_defaults(func=list_dash_rglinksbootstrap)

##########################################################
#
##########################################################
def list_dash_rglinksbootstrap(args):

    obj = Dashboard(args.ip, args.port, args.format)
    try:
        return obj.list(Dashboard.URI_DASHBOARD_LOCAL_RGLINKSBOOT)
    except SOSError as e:
        raise e

##########################################################
#
##########################################################
def list_dash_repgroup_parser(subcommand_parsers, common_parser):
    # list localzone command parser
    list_dash_repgroup_parser= subcommand_parsers.add_parser(
        'list-repgroup',
        description='ECS List replication group details CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='list replication group info')

    mandatory_args = list_dash_repgroup_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-id', '-id',
                             help='replication group id',
                             default=None,
                             metavar='<id>',
                             dest='id',
                             required=True)

    list_dash_repgroup_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    list_dash_repgroup_parser.set_defaults(func=list_dash_repgroup)

##########################################################
#
##########################################################
def list_dash_repgroup(args):

    obj = Dashboard(args.ip, args.port, args.format)
    try:
        return obj.list(Dashboard.URI_DASHBOARD_REPGROUP.format(args.id))
    except SOSError as e:
        raise e

##########################################################
#
##########################################################
def list_dash_rglinks_parser(subcommand_parsers, common_parser):
    # list localzone command parser
    list_dash_rglinks_parser= subcommand_parsers.add_parser(
        'list-rglinks',
        description='ECS List replication group links CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='list replication group links')

    mandatory_args = list_dash_rglinks_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-id', '-id',
                             help='replication group id',
                             default=None,
                             metavar='<id>',
                             dest='id',
                             required=True)

    list_dash_rglinks_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    list_dash_rglinks_parser.set_defaults(func=list_dash_rglinks)

##########################################################
#
##########################################################
def list_dash_rglinks(args):

    obj = Dashboard(args.ip, args.port, args.format)
    try:
        return obj.list(Dashboard.URI_DASHBOARD_RGLINKS.format(args.id))
    except SOSError as e:
        raise e

##########################################################
#
##########################################################
def list_dash_repgrouplinks_parser(subcommand_parsers, common_parser):
    # list localzone command parser
    list_dash_repgrouplinks_parser= subcommand_parsers.add_parser(
        'list-repgrouprglinks',
        description='ECS List replication group links CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='list replication group links')

    mandatory_args = list_dash_repgrouplinks_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-id', '-id',
                             help='replication group id',
                             default=None,
                             metavar='<id>',
                             dest='id')

    list_dash_repgrouplinks_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    list_dash_repgrouplinks_parser.set_defaults(func=list_dash_repgrouplinks)

##########################################################
#
##########################################################
def list_dash_repgrouplinks(args):

    obj = Dashboard(args.ip, args.port, args.format)
    try:
        return obj.list(Dashboard.URI_DASHBOARD_REPGROUP_LINKS.format(args.id))
    except SOSError as e:
        raise e


##########################################################
#
##########################################################
def dashboard_parser(parent_subparser, common_parser):
    # main tenant parser
    parser = parent_subparser.add_parser(
        'dashboard',
        description='ECS replication group links CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Operations on replication group links')
    subcommand_parsers = parser.add_subparsers(help='Use One Of Commands')

    # list namespace parser
    list_dash_repgrouplinks_parser(subcommand_parsers, common_parser)
    list_dash_rglinks_parser(subcommand_parsers, common_parser)
    list_dash_repgroup_parser(subcommand_parsers, common_parser)
    list_dash_rglinksbootstrap_parser(subcommand_parsers, common_parser)
    list_dash_storagepoolnodes_parser(subcommand_parsers, common_parser)
    list_dash_nodedisks_parser(subcommand_parsers, common_parser)
    list_dash_nodeprocesses_parser(subcommand_parsers, common_parser)
    list_dash_process_parser(subcommand_parsers, common_parser)
    list_dash_disk_parser(subcommand_parsers, common_parser)
    list_dash_nodes_parser(subcommand_parsers, common_parser)
    list_dash_storagepools_parser(subcommand_parsers, common_parser)
    list_dash_lznodes_parser(subcommand_parsers, common_parser)
    list_dash_lzstoragepools_parser(subcommand_parsers, common_parser)
    list_dash_lzrglinksfailed_parser(subcommand_parsers, common_parser)
    list_dash_lzrepgroup_parser(subcommand_parsers, common_parser)
    list_dash_localzone_parser(subcommand_parsers, common_parser)

