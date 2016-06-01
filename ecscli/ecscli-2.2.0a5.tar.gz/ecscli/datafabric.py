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
from common import SOSError
from virtualarray import VirtualArray
# from virtualpool import VirtualPool

class DataFabric(object):
    '''
    The class definition for operations on data stoers and data fabric.
    '''

    #Common URIs for datafabric
    URI_SERVICES_BASE = ''

    URI_FABRIC = URI_SERVICES_BASE + '/vdc'
    URI_NODE_LIST = URI_FABRIC + '/nodes'
    URI_SERVICE_LIST = URI_FABRIC + '/services'
    URI_PROVISIONING_PROVISION = URI_FABRIC + '/provisioning/provision'

    URI_DATASTORE = URI_SERVICES_BASE + '/vdc/data-stores'
    URI_TASK_LIST = URI_DATASTORE + '/{0}/tasks/{1}'
    URI_COMMODITY_DATASTORE_LOCAL = URI_DATASTORE + '/commodity'
    # URI_COMMODITY_DATASTORE_FILE = URI_DATASTORE + '/filesystems'
    # URI_COMMODITY_DATASTORE_NFS = URI_DATASTORE + '/nfsexportpoints'
    URI_COMMODITY_DATASTORE_SEARCH = URI_COMMODITY_DATASTORE_LOCAL + '/search/varray/{0}'
    
    URI_DATASTORE_LOCAL_INST = URI_COMMODITY_DATASTORE_LOCAL + '/{0}'
    # URI_DATASTORE_FILE_INST = URI_COMMODITY_DATASTORE_FILE + '/{0}'
    # URI_DATASTORE_NFS_INST = URI_COMMODITY_DATASTORE_NFS + '/{0}'
    
    URI_DATASTORE_DELETE = URI_DATASTORE + '/{0}/deactivate'
    
    def __init__(self, ipAddr, port):

        '''
        Constructor: takes IP address and port of the ECS instance.
        These are needed to make http requests for REST API
        '''
        self.__ipAddr = ipAddr
        self.__port = port


    def list_nodes(self):

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, 'GET',
                                            DataFabric.URI_NODE_LIST, None)
        o = common.json_decode(s)

        if (not o):
            return []
        return o


    def list_services(self):

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, 'GET',
                                            DataFabric.URI_SERVICE_LIST, None)
        o = common.json_decode(s)

        if (not o):
            return []
        return o


    def provision_service(self, serviceType, nodes):

        requestBody = json.dumps({
                   "serviceType": serviceType,
                   "nodes": nodes
                   })

        common.service_json_request(self.__ipAddr, self.__port, 'POST',
                                    DataFabric.URI_PROVISIONING_PROVISION, requestBody)


    def check_for_sync(self, result, sync=None):

        if(sync):
            if(len(result["task"]) > 0):

                resource = result["task"][0]

                return (
                    common.block_until_complete("datastore", resource["resource"]["id"],
                                                resource["op_id"], self.__ipAddr,
                                                self.__port)
                )
            else:
                raise SOSError(SOSError.SOS_FAILURE_ERR,
                    "error: task list is empty, no task response found")
        else:
            return result


    # def create_data_stores(self, ipaddr, name, varray, type,
    #                        desc, size, mountpath, vpool):
    def create_data_stores(self, ipaddr, name, varray, desc):
        '''
        Creates new commodity data stores.

        Note that the data store creation is an asynchronous
        operation - a successful invocation of this request
        does not necessarily mean that creation has completed.
        '''

        varray_uri = VirtualArray(self.__ipAddr,
                                  self.__port).varray_query(varray)
        request = {           
            'name': name,
            'virtual_array': varray_uri
            }
        
        if(desc):
            request["description"] = desc
            
        # if (type == 'commodity'):
        request['nodeId'] = ipaddr

        body = json.dumps({
               "nodes": [ request ]
               })
        uri = DataFabric.URI_COMMODITY_DATASTORE_LOCAL
        # else:
        #     if (size):
        #         request['size'] = size
        #     if (type == 'nfs' and mountpath is not None):
        #         request['mount_point'] = mountpath
        #     if (type == 'file' and vpool is not None):
        #         vpUri = VirtualPool(self.__ipAddr,
        #                             self.__port).vpool_query(vpool, "file")
        #         request['file_data_services_vpool']  = vpUri
        #     body = json.dumps(request)
        #
        #     if (type == 'nfs'):
        #         uri = DataFabric.URI_COMMODITY_DATASTORE_NFS
        #     else:
        #         uri = DataFabric.URI_COMMODITY_DATASTORE_FILE
        
        (s, h) = common.service_json_request(self.__ipAddr, self.__port, 'POST',
                                                uri, body)
        o = common.json_decode(s)

        if (not o):
            return []
        return o


    def list_data_stores(self):
        '''
        Gets list of configured commodity or filesystem data stores.
        '''

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, 'GET',
                                            DataFabric.URI_DATASTORE, None)
        o = common.json_decode(s)

        if (not o):
            return []

        return o["data_store"]


    def show_tasks(self, name, taskid):
        '''
        Get all recent tasks for a data store.
        '''

        dsUri = self.query_data_store(name)
        uri = DataFabric.URI_TASK_LIST.format(dsUri, taskid)

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, 'GET',
                                             uri, None)
        o = common.json_decode(s)

        if (not o):
            return []
        return o


    def query_data_store(self, name):
        '''
        Gets data store ID from name
        '''

        datastores = self.list_data_stores()

        for ds in datastores:
            if ('name' in ds and ds['name'] == name ):
                return ds['id']     
        return name


    def show_data_store(self, name):
        '''
        Gets the details for a commodity data store.
        '''

        uri = DataFabric.URI_DATASTORE_LOCAL_INST.format(name)

        '''
        if (pool is None):
            dsUri = self.query_data_store(name)
            # uri = DataFabric.URI_DATASTORE_NFS_INST.format(dsUri)

            # if (type == 'commodity'):
            uri = DataFabric.URI_DATASTORE_LOCAL_INST.format(dsUri)
            # elif (type == 'file'):
            #     uri = DataFabric.URI_DATASTORE_FILE_INST.format(dsUri)
        else:
            uri = DataFabric.URI_COMMODITY_DATASTORE_SEARCH(pool)
        '''
                
        (s, h) = common.service_json_request(self.__ipAddr, self.__port, 'GET',
                                                uri, None)
        o = common.json_decode(s)

        if (not o):
            return None
        return o


    def get_bulk_resources(self, idlist):
        '''
        Retrieve list of resource representations based on input ids.
        '''

        parms = dict()
        parms['id'] = []
        for id in idlist :
            parms['id'].append(id)

        body = json.dumps(parms)
        uri = self.URI_DATASTORE + '/bulk'
        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "POST", uri, body, None, False)

        o = common.json_decode(s)

        if (not o):
            return []
        return o


    def delete_data_store(self, name):
        '''
        Deactivates the hosting device and data store

        NOTE: Storage will be deleted if it was
        allocated with the data store.

        Data store deletion is an asynchronous operation,
        so a successful invocation of this request does not
        necessarily mean that the deletion has completed.
        '''

        dsUri = self.query_data_store(name)
        uri = DataFabric.URI_DATASTORE_DELETE.format(dsUri)

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, 'POST',
                                                uri, None)
        o = common.json_decode(s)

        if (not o):
            return []
        return o


def list_node_parser(subcommand_parsers, common_parser):
    # list node parser
    list_node_parser = subcommand_parsers.add_parser(
        'list',
        description='ECS List data fabric node CLI usage ',
        parents=[common_parser],
        conflict_handler='resolve',
        help='List data fabric nodes')

    list_node_parser.set_defaults(func=list_datafabric_nodes)

def list_datafabric_nodes(args):
    obj = DataFabric(args.ip, args.port)
    try:
        return common.format_json_object(obj.list_nodes())
    except SOSError as e:
        common.format_err_msg_and_raise("list", "data fabric nodes",
                                        e.err_text, e.err_code)


def list_services_parser(subcommand_parsers, common_parser):
    #list services command parser
    list_services_parser = subcommand_parsers.add_parser(
        'list',
        description='ECS List data fabric services CLI usage ',
        parents=[common_parser],
        conflict_handler='resolve',
        help='List data fabric services')

    list_services_parser.set_defaults(func=list_datafabric_services)

def list_datafabric_services(args):

    obj = DataFabric(args.ip, args.port)
    try:
        return common.format_json_object(obj.list_services())
    except SOSError as e:
        common.format_err_msg_and_raise("list", "data services",
                                        e.err_text, e.err_code)


def provision_service_parser(subcommand_parsers, common_parser):
    # provision service command parser
    provision_service_parser = subcommand_parsers.add_parser(
        'provision',
        description='ECS provision data fabric services CLI usage ',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Provision data fabric services')

    mandatory_args = provision_service_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-service', '-s',
                               dest='service',
                               metavar='<service>',
                               help='Type of service (URI)',
                               required=True)
    mandatory_args.add_argument('-nodes', '-n',
                               dest='nodes',
                               nargs='+',
                               metavar='<node>',
                               help='ID of node (URI)',
                               required=True)

    provision_service_parser.set_defaults(func=provision_service)

def provision_service(args):
    obj = DataFabric(args.ip, args.port)
    try:
        obj.provision_service(args.service,
                              args.nodes)
    except SOSError as e:
        common.format_err_msg_and_raise("provision", "data services",
                                        e.err_text, e.err_code)


def create_datastore_parser(subcommand_parsers, common_parser):
    # create datastore command parser
    create_datastore_parser = subcommand_parsers.add_parser(
        'create',
        description='ECS create data store CLI usage ',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Create data store')

    mandatory_args = create_datastore_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-name', '-n',
                               dest='name',
                               metavar='<name>',
                               help='Name of data store',
                               required=True)

    mandatory_args.add_argument('-varray', '-va',
                               dest='varray',
                               metavar='<varray>',
                               help='Virtual Array of data store',
                               required=True)

    create_datastore_parser.add_argument('-dsid', '-datastoreid',
                               dest='dsid',
                               metavar='<datastoreid>',
                               help='IP address of data store')

    create_datastore_parser.add_argument('-desc', '-description',
                               dest='description',
                               metavar='<description>',
                               help='Description for data store')

    # create_datastore_parser.add_argument('-size', '-s',
    #                            dest='size',
    #                            metavar='<size>',
    #                            help='Size of data store')
    #
    # create_datastore_parser.add_argument('-mountpath', '-mtp',
    #                            dest='mountpath',
    #                            metavar='<mountpath>',
    #                            help='Mount path of NFS data store')
    #
    # create_datastore_parser.add_argument('-vpool', '-vp',
    #                            dest='vpool',
    #                            metavar='<vpool>',
    #                            help='Name of File Virtual pool')
    #
    # mandatory_args.add_argument('-type', '-t',
    #                            dest='type',
    #                            metavar='<type>',
    #                            choices=['commodity', 'file', 'nfs'],
    #                            required=True,
    #                            help='Type of data store')
    
    create_datastore_parser.set_defaults(func=create_datasore)

def create_datasore(args):

    obj = DataFabric(args.ip, args.port)

    # if (args.type == 'commodity' and args.dsid is None):
    if (args.dsid is None):
        raise SOSError(SOSError.SOS_FAILURE_ERR,
              "Please define -datastoreid for commodity data store")
    # elif (args.type == 'file' and (args.size is None or args.vpool is None) ):
    #     raise SOSError(SOSError.SOS_FAILURE_ERR,
    #           "Please define -size and -vpool for file data store")
    # elif (args.type == 'nfs' and (args.size is None or args.mountpath is None) ):
    #     raise SOSError(SOSError.SOS_FAILURE_ERR,
    #           "Please define -size and -mountpath for NFS data store")

    try:
        res = obj.create_data_stores(args.dsid,
                                     args.name,
                                     args.varray,
                                     # args.type,
                                     args.description)
                                     # args.size,
                                     # args.mountpath,
                                     # args.vpool)
        return common.format_json_object(res)
    except SOSError as e:
        common.format_err_msg_and_raise("create", "datastore",
                                        e.err_text, e.err_code)


def show_datastore_parser(subcommand_parsers, common_parser):
    # show datastore command parser
    show_datastore_parser = subcommand_parsers.add_parser(
        'show',
        description='ECS show data store node CLI usage ',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Show data store')

    show_datastore_parser.add_argument('-name', '-n',
                               dest='name',
                               help='Name of data store',
                               required=True)

    show_datastore_parser.set_defaults(func=show_datastore)

def show_datastore(args):

    obj = DataFabric(args.ip, args.port)

    try:
        if (args.name is None and args.pool is None) :
            raise SOSError(SOSError.SOS_FAILURE_ERR,
                           "Please define either data store name or storage pool id")
        res = obj.show_data_store(args.name)
        return common.format_json_object(res)
    except SOSError as e:
        common.format_err_msg_and_raise("show", "datastore",
                                        e.err_text, e.err_code)


def bulk_get_parser(subcommand_parsers, common_parser):
    # get-bulk command parser
    bulk_get_parser = subcommand_parsers.add_parser(
        'bulk-get',
        description='ECS Datastore Get Bulk Resources CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='List all resource representations')

    mandatory_args = bulk_get_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-ids',
                                help='comma-delimited list of resource ids',
                                metavar='<ids>',
                                dest='ids',
                                required=True)

    bulk_get_parser.set_defaults(func=datastores_get_bulk)

def datastores_get_bulk(args):

    obj = DataFabric(args.ip, args.port)

    try:
        output = obj.get_bulk_resources(args.ids.split())
        return common.format_json_object(output)

    except SOSError as e:
        raise common.format_err_msg_and_raise("bulk-get", "datastore",
                                              e.err_text, e.err_code)


def delete_datastore_parser(subcommand_parsers, common_parser):
    # delete datastore command parser
    delete_datastore_parser = subcommand_parsers.add_parser(
        'delete',
        description='ECS delete data store node CLI usage ',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Delete data store')

    mandatory_args = delete_datastore_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-name', '-n',
                               dest='name',
                               help='Name of data store',
                               required=True)

    # mandatory_args.add_argument('-type', '-t',
    #                            dest='type',
    #                            metavar='<type>',
    #                            required=True,
    #                            choices=['commodity', 'file', 'nfs'],
    #                            help='Type of data store')

    delete_datastore_parser.set_defaults(func=delete_datastore)

def delete_datastore(args):

    obj = DataFabric(args.ip, args.port)

    try:
        res = obj.delete_data_store(args.name)
        return common.format_json_object(res)
    except SOSError as e:
        common.format_err_msg_and_raise("delete", "datastore",
                                        e.err_text, e.err_code)


def task_parser(subcommand_parsers, common_parser):
    # tasks command parser
    task_parser = subcommand_parsers.add_parser(
        'tasks',
        description='ECS datastore List tasks CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Show details of datastore tasks')

    mandatory_args = task_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-name', '-n',
                                metavar='<name>',
                                dest='name',
                                help='Name of data store',
                                required=True)

    mandatory_args.add_argument('-id',
                             dest='id',
                             metavar='<opid>',
                             help='Operation ID',
                             required=True)

    task_parser.set_defaults(func=datastore_tasks_list)

def datastore_tasks_list(args):

    obj = DataFabric(args.ip, args.port)

    try:
        res = obj.show_tasks(args.name, args.id)
        return common.format_json_object(res)

    except SOSError as e:
        common.format_err_msg_and_raise("get tasks list", "datastore",
                                        e.err_text, e.err_code)


def list_parser(subcommand_parsers, common_parser):
    # list command parser
    list_parser = subcommand_parsers.add_parser(
        'list',
        description='ECS Datastore List CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='List all data stores')

    list_parser.add_argument('-verbose', '-v',
                             dest='verbose',
                             help='data stores list with details',
                             action='store_true')

    list_parser.add_argument('-long', '-l',
                             action='store_true',
                             help='List Data stores with details in table format',
                             dest='long')

    list_parser.set_defaults(func=datastores_list)

def datastores_list(args):

    obj = DataFabric(args.ip, args.port)

    try:
        output = obj.list_data_stores()
        if(len(output) > 0):
            if(args.verbose):
                return common.format_json_object(output)
            if(args.long):
                from common import TableGenerator
                TableGenerator(output, ['name', 'id',
                                        'resource_type']).printTable()
            else:
                from common import TableGenerator
                TableGenerator(output, ['name']).printTable()

        return output
    except SOSError as e:
        raise common.format_err_msg_and_raise("list", "datastore",
                                              e.err_text, e.err_code)


def datafabric_node_parser(parent_subparser, common_parser):
    # main datafabric node parser
    parser = parent_subparser.add_parser(
        'node',
        description='ECS node CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Operations on data fabric nodes')
    subcommand_parsers = parser.add_subparsers(help='Use One Of Commands')

    #list nodes command parser
    list_node_parser(subcommand_parsers, common_parser)


def datafabric_service_parser(parent_subparser, common_parser):
    # main data fabric services parser
    parser = parent_subparser.add_parser(
        'dataservice',
        description='ECS dataservice CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Operations on data fabric services')
    subcommand_parsers = parser.add_subparsers(help='use one of sub-commands')

    # list services command parser
    list_services_parser(subcommand_parsers, common_parser)

    # provision service command parser
    provision_service_parser(subcommand_parsers, common_parser)


def datafabric_commodity_datastore_parser(parent_subparser, common_parser):
    # main data fabric parser
    parser = parent_subparser.add_parser(
        'datastore',
        description='ECS datastore CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Operations on datastore')
    subcommand_parsers = parser.add_subparsers(help='use one of sub-commands')

    create_datastore_parser(subcommand_parsers, common_parser)

    show_datastore_parser(subcommand_parsers, common_parser)

    bulk_get_parser(subcommand_parsers, common_parser)

    delete_datastore_parser(subcommand_parsers, common_parser)

    task_parser(subcommand_parsers, common_parser)

    list_parser(subcommand_parsers, common_parser)

