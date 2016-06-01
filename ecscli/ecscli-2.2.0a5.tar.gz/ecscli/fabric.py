#!/usr/bin/python

#
# Copyright (c) 2013 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.


import common
import json
from argparse import ArgumentParser
from common import SOSError
from virtualarray import VirtualArray

class Fabric(object):
    # List of URIs for Fabric
    URI_FABRIC_STATS = "/vdc/fabric/stats"
    URI_FABRIC_CAPACITY = "/vdc/fabric/capacity"
    URI_FABRIC_AUDIT = "/vdc/fabric/audit"
    URI_FABRIC_EVENTS = "/vdc/fabric/events"
    URI_FABRIC_HEALTH = "/vdc/fabric/health"
    URI_FABRIC_PROVISION = "/vdc/fabric/provision"
    
    URI_FABRIC_OBJECT = '/vdc/fabric/{0}'
    # List of URIs for Fabric service
    URI_FABRIC_SERVICES = '/vdc/fabric/services'
    URI_FABRIC_SERVICE = URI_FABRIC_SERVICES + '/{0}'
    URI_FABRIC_SERVICE_CAPACITY = URI_FABRIC_SERVICE + '/capacity'
    URI_FABRIC_SERVICE_NODES = URI_FABRIC_SERVICE + '/nodes'

    # List of URIs for Fabric Node
    URI_FABRIC_NODES = '/vdc/fabric/nodes'
    URI_FABRIC_NODE = URI_FABRIC_NODES + '/{0}'
    URI_FABRIC_NODE_CAPACITY = URI_FABRIC_NODE + '/capacity'
    URI_FABRIC_NODE_HEALTH = URI_FABRIC_NODE + '/health'
    URI_FABRIC_NODE_DISKS = URI_FABRIC_NODE + '/disks'
    
    # List of URIs for Fabric node
    URI_FABRIC_DISKS = '/vdc/fabric/disks'
    URI_FABRIC_DISK = URI_FABRIC_DISKS + '/{0}'
    URI_FABRIC_DISK_CAPACITY = URI_FABRIC_DISK + '/capacity'
    
    FABRIC_SER_PORT = '4443'
    
    def __init__(self, ipAddr, port):

        '''
        Constructor: takes IP address and port of the ECS instance.
        These are needed to make http requests for REST API
        '''
        self.__ipAddr = ipAddr
        self.__port = port

    def list_by_uri(self, uri):
        '''
        This is a generalized function to list different fabric resources,
        like list Fabric services, fabric nodes and fabric disks.
        '''
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port, 'GET',
            uri, None)
        o = common.json_decode(s)
        if (not o):
            return []
        else:
            return o
        
    def get_by_uri(self, uri):
        '''
        This is a generalized function to detailed the diff fabric resources,
        like details of Fabric service, fabric node and fabric disk.
        '''
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port, 'GET',
            uri, None)
        o = common.json_decode(s)
        if (not o):
            return None
        else:
            return o
    
    def is_uri(self, name):
        '''
        Checks whether the name is a UUID or not
        Returns:
            True if name is UUID, False otherwise
        '''
        try:
            (urn, prod, trailer) = name.split(':', 2)
            return (urn == 'urn' and prod == "fabric")
        except:
            return False    
    def fabric_query(self, name, fabobj):
        '''
        This is a query function to get the URI of given resource name,
        parameters:
             name : Name of the fabric service/node/disk
             fabobj: Parameter to identify the above name.
        return
            Id of the given resource.     
        '''
        if(self.is_uri(name)):
            return name
        uri = Fabric.URI_FABRIC_OBJECT.format(fabobj)
        fabrics = self.list_by_uri(uri)
        if (fabobj == 'services'):
            fabrics = fabrics['service']
        if (fabobj == 'nodes'):
            fabrics = fabrics['node']
        elif (fabobj == 'disks'):
            fabrics = fabrics['disk']    
        for fabric in fabrics:
            if ('name' in fabric and fabric['name'] == name ):
                return fabric['id']  
        
        raise SOSError(SOSError.NOT_FOUND_ERR,
                            fabobj + '  ' + name + ' not found')       
                
    def fabric_service_list(self):
        out = self.list_by_uri(Fabric.URI_FABRIC_SERVICES)
        if (out is not None):
            return out['service']
        else:
            return None
    
    def fabric_node_list(self):
        out = self.list_by_uri(Fabric.URI_FABRIC_NODES)
        if (out is not None):
            return out['node']
        else:
            return None
    
    def fabric_disk_list(self):
        out =  self.list_by_uri(Fabric.URI_FABRIC_DISKS)
        if (out is not None):
            return out['disk']
        else:
            return None
    
    def fabric_service_ops(self, servicename, cmd):
        '''
        This function will perform all different operation on fabric service.
        like fabricservice show/nodes/capacity etc.,
        parameters:
            servicename: Name of fabric service.
            cmd: diff. ops on fabric service like show/nodes/capacity
        return
        return the response of the given object actions.    
        '''
        servUri = self.fabric_query(servicename, "services") 
        uri = Fabric.URI_FABRIC_SERVICE
        if(cmd == 'nodes'):
            uri = Fabric.URI_FABRIC_SERVICE_NODES
        elif(cmd == 'capacity'):
            uri = Fabric.URI_FABRIC_SERVICE_CAPACITY
    
        return self.get_by_uri(uri.format(servUri))
    
    def fabric_node_ops(self, nodename, cmd):
        '''
        This function will perform all different operation on fabric node.
        like fabricnode show/health/disks/capacity etc.,
        parameters:
            nodename: Name of fabric node.
            cmd: diff. ops on fabric node like show/disks/health/capacity
        return
        return the response of the given object actions.    
        '''
        nodeUri = self.fabric_query(nodename, "nodes")
        uri = Fabric.URI_FABRIC_NODE
        if(cmd == 'health'):
            uri = Fabric.URI_FABRIC_NODE_HEALTH
        elif(cmd == 'capacity'):
            uri = Fabric.URI_FABRIC_NODE_CAPACITY
        elif(cmd == 'disks'):
            uri = Fabric.URI_FABRIC_NODE_DISKS    
    
        return self.get_by_uri(uri.format(nodeUri))
    
    def fabric_disk_query(self, diskname, nodename=None):
        for disk in self.fabric_disk_list():
            if ('name' in disk and disk['name'] == diskname ):
                node = self.fabric_node_ops(disk['node_id'], "show")
                if(nodename is not None):
                    if(nodename != node['name']):
                        continue
                return disk['id'] 
        raise SOSError(SOSError.NOT_FOUND_ERR,
                            'disk' +  diskname + ' not found')      
            
    def fabric_disk_ops(self, diskname, cmd, nodename=None):
        '''
        This function will perform all different operation on fabric disk.
        like fabricdisk show/capacity etc.,
        parameters:
            diskname: Name of fabric disk.
            cmd: diff. ops on fabric disk like show/capacity
        return
        return the response of the given object actions.    
        '''
        diskUri = self.fabric_disk_query(diskname, nodename)
        uri = Fabric.URI_FABRIC_DISK
        if(cmd == 'capacity'):
            uri = Fabric.URI_FABRIC_DISK_CAPACITY
            
        return self.get_by_uri(uri.format(diskUri))
        
    def fabric_cmds(self, cmd):
        '''
        This function will perform all different operation on whole fabric.
        like fabric health/capacity etc.,
        parameters:
            cmd: diff. ops on fabric like health/capacity
        return
        return the response of the given object actions.    
        '''
        uri = Fabric.URI_FABRIC_STATS
        if(cmd == 'capacity'):
            uri = Fabric.URI_FABRIC_CAPACITY
        elif(cmd == 'events'):
            uri = Fabric.URI_FABRIC_EVENTS
        elif(cmd == 'stats'):
            uri = Fabric.URI_FABRIC_STATS
        elif(cmd == 'health'):
            uri = Fabric.URI_FABRIC_HEALTH
        elif(cmd == 'audit'):
            uri = Fabric.URI_FABRIC_AUDIT    
        
        return self.get_by_uri(uri)
    
    def fabric_provision(self, service, nodes):
        servUri = self.fabric_query(service, "services")
        nodeUris = []
        for node in nodes:
            nodeUris.append(self.fabric_query(node, "nodes"))
        
        param = { 'name': servUri,
                  'nodes': nodeUris
                }        
        body = json.dumps(param)  
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "POST",
            Fabric.URI_FABRIC_PROVISION,
            body)
        o = common.json_decode(s)
        return o               
    

def fabric_common_parser(subcommand_parsers, common_parser, command):
    fabric_common_parser = subcommand_parsers.add_parser(
        command, description='ECS fabric ' + command + ' CLI usage ',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Fabric ' + command)
    
    fabric_common_parser.set_defaults(func=fabric_common_ops)
    fabric_common_parser.set_defaults(op=command)
    


def fabric_common_ops(args):

    obj = Fabric(args.ip, args.port)
    try:
        res = obj.fabric_cmds(args.op)
        return common.format_json_object(res)
    except SOSError as e:
        common.format_err_msg_and_raise(
            args.op,
            "fabric",
            e.err_text,
            e.err_code)
        
def fabric_provision_parser(subcommand_parsers, common_parser):
    fabric_provision_parser = subcommand_parsers.add_parser(
        'provision', description='ECS Fabric provision CLI usage ',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Set Fabric Provision')
    mandatory_args = fabric_provision_parser.add_argument_group(
        'mandatory arguments')
    mandatory_args.add_argument('-service', '-se',
                               dest='service',
                               help='Name of the service',
                               required=True)
    fabric_provision_parser.add_argument('-nodes',
                               dest='nodes',
                               metavar='<nodes>',
                               nargs='+',
                               help='Set of nodes in a service')
    fabric_provision_parser.set_defaults(func=fabric_provision)


def fabric_provision(args):

    obj = Fabric(args.ip, args.port)

    try:
        res = obj.fabric_provision(args.service, args.nodes)
        return common.format_json_object(res)
    except SOSError as e:
        common.format_err_msg_and_raise(
            "provision",
            "fabric",
            e.err_text,
            e.err_code)       
                 

def fabric_service_sub_parser(subcommand_parsers, common_parser, command):
    fabric_service_sub_parser = subcommand_parsers.add_parser(
        command, description='ECS fabric service' + command + ' CLI usage ',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Fabric service ' + command)
    mandatory_args = fabric_service_sub_parser.add_argument_group(
        'mandatory arguments')
    mandatory_args.add_argument('-service', '-se',
                               dest='service',
                               help='Name of the service',
                               required=True)
    fabric_service_sub_parser.set_defaults(func=fabric_service_ops)
    fabric_service_sub_parser.set_defaults(op=command)


def fabric_service_ops(args):
    obj = Fabric(args.ip, args.port)
    try:
        res = obj.fabric_service_ops(args.service, args.op)
        return common.format_json_object(res)
    except SOSError as e:
        common.format_err_msg_and_raise(
            args.op,
            "fabricservice",
            e.err_text,
            e.err_code)
        
def fabric_service_list_parser(subcommand_parsers, common_parser):
    fabric_service_list_parser = subcommand_parsers.add_parser(
        'list', description='ECS fabric service list CLI usage ',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Fabric service list')
    fabric_service_list_parser.set_defaults(func=fabric_service_list)

def fabric_service_list(args):
    obj = Fabric(args.ip, args.port)
    try:
        res = obj.fabric_service_list()
        if(res is not None):
            from common import TableGenerator
            TableGenerator(res, ['name']).printTable()
    except SOSError as e:
        common.format_err_msg_and_raise(
            'list',
            "fabricservice",
            e.err_text,
            e.err_code)
        
def fabric_node_sub_parser(subcommand_parsers, common_parser, command):
    fabric_node_sub_parser = subcommand_parsers.add_parser(
        command, description='ECS fabric node' + command + ' CLI usage ',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Fabric node ' + command)
    mandatory_args = fabric_node_sub_parser.add_argument_group(
        'mandatory arguments')
    mandatory_args.add_argument('-node', '-n',
                               dest='node',
                               help='Name of the node',
                               required=True)
    fabric_node_sub_parser.set_defaults(func=fabric_node_ops)
    fabric_node_sub_parser.set_defaults(op=command)


def fabric_node_ops(args):
    obj = Fabric(args.ip, args.port)
    try:
        res = obj.fabric_node_ops(args.node, args.op)
        return common.format_json_object(res)
    except SOSError as e:
        common.format_err_msg_and_raise(
            args.op,
            "fabricnode",
            e.err_text,
            e.err_code)
        
def fabric_node_list_parser(subcommand_parsers, common_parser):
    fabric_node_list_parser = subcommand_parsers.add_parser(
        'list', description='ECS fabric node list CLI usage ',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Fabric node list')
    fabric_node_list_parser.set_defaults(func=fabric_node_list)

def fabric_node_list(args):
    obj = Fabric(args.ip, args.port)
    try:
        res = obj.fabric_node_list()
        if(res is not None):
            from common import TableGenerator
            TableGenerator(res, ['name']).printTable()
    except SOSError as e:
        common.format_err_msg_and_raise(
            'list',
            "fabricnode",
            e.err_text,
            e.err_code)
        
        
def fabric_disk_sub_parser(subcommand_parsers, common_parser, command):
    fabric_disk_sub_parser = subcommand_parsers.add_parser(
        command, description='ECS fabric disk' + command + ' CLI usage ',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Fabric disk ' + command)
    mandatory_args = fabric_disk_sub_parser.add_argument_group(
        'mandatory arguments')
    mandatory_args.add_argument('-disk', 
                               dest='disk',
                               help='Name of the disk',
                               required=True)
    fabric_disk_sub_parser.add_argument('-node', 
                               dest='node',
                               help='Name of the node')
    fabric_disk_sub_parser.set_defaults(func=fabric_disk_ops)
    fabric_disk_sub_parser.set_defaults(op=command)


def fabric_disk_ops(args):
    obj = Fabric(args.ip, args.port)
    try:
        res = obj.fabric_disk_ops(args.disk, args.op, args.node)
        return common.format_json_object(res)
    except SOSError as e:
        common.format_err_msg_and_raise(
            args.op,
            "fabricdisk",
            e.err_text,
            e.err_code)
        
def fabric_disk_list_parser(subcommand_parsers, common_parser):
    fabric_disk_list_parser = subcommand_parsers.add_parser(
        'list', description='ECS fabric disk list CLI usage ',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Fabric disk list')
    fabric_disk_list_parser.add_argument('-node', 
                               dest='node',
                               help='Name of the node')
    fabric_disk_list_parser.set_defaults(func=fabric_disk_list)

def fabric_disk_list(args):
    obj = Fabric(args.ip, args.port)
    try:
        res = obj.fabric_disk_list()
        output = []
        if(res is not None):
            for disk in res:
                node = obj.fabric_node_ops(disk['node_id'], "show")
                if(args.node is not None):
                    if(args.node != node['name']):
                        continue
                    
                disk['node_name'] = node['name']
                output.append(disk)    
            from common import TableGenerator
            TableGenerator(output, ['name', 'node_name']).printTable()
    except SOSError as e:
        common.format_err_msg_and_raise(
            'list',
            "fabricdisk",
            e.err_text,
            e.err_code)                    


def fabric_parser(parent_subparser, common_parser):

    parser = parent_subparser.add_parser(
        'fabric',
        description='ECS fabric CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Operations on fabric')
    subcommand_parsers = parser.add_subparsers(help='use one of sub-commands')

    fabric_common_parser(subcommand_parsers, common_parser, "health")
    
    #fabric_common_parser(subcommand_parsers, common_parser, "audit")
    
    fabric_common_parser(subcommand_parsers, common_parser, "capacity")
    
    #fabric_common_parser(subcommand_parsers, common_parser, "events")
    
    #fabric_common_parser(subcommand_parsers, common_parser, "stats")
    
    #fabric_provision_parser(subcommand_parsers, common_parser)
    

def fabric_service_parser(parent_subparser, common_parser):

    parser = parent_subparser.add_parser(
        'fabricservice',
        description='ECS fabric service CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Operations on fabric service')
    subcommand_parsers = parser.add_subparsers(help='use one of sub-commands')
    
    fabric_service_sub_parser(subcommand_parsers, common_parser, "show")
    
    fabric_service_sub_parser(subcommand_parsers, common_parser, "nodes")
    
    fabric_service_sub_parser(subcommand_parsers, common_parser, "capacity")
    
    fabric_service_list_parser(subcommand_parsers, common_parser)
    
    
def fabric_node_parser(parent_subparser, common_parser):

    parser = parent_subparser.add_parser(
        'fabricnode',
        description='ECS fabric node CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Operations on fabric node')
    subcommand_parsers = parser.add_subparsers(help='use one of sub-commands')
    
    fabric_node_sub_parser(subcommand_parsers, common_parser, "show")
    
    fabric_node_sub_parser(subcommand_parsers, common_parser, "health")
    
    fabric_node_sub_parser(subcommand_parsers, common_parser, "disks")
    
    fabric_node_sub_parser(subcommand_parsers, common_parser, "capacity")
    
    fabric_node_list_parser(subcommand_parsers, common_parser)
    
def fabric_disk_parser(parent_subparser, common_parser):

    parser = parent_subparser.add_parser(
        'fabricdisk',
        description='ECS fabric disk CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Operations on fabric disk')
    subcommand_parsers = parser.add_subparsers(help='use one of sub-commands')
    
    fabric_disk_sub_parser(subcommand_parsers, common_parser, "show")
    
    fabric_disk_sub_parser(subcommand_parsers, common_parser, "capacity")
    
    fabric_disk_list_parser(subcommand_parsers, common_parser)        
    
    
    

