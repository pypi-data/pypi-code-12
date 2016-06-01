#!/usr/bin/python

# Copyright (c) 2012-14 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

import common
import tag
import json
import socket
import commands
from common import SOSError
from threading import Timer

class Nfs(object):

    '''
    The class definition for operations on 'Nfs'.
    '''
    # Commonly used URIs for the 'Nfs' module

    URI_SERVICES_BASE = ''
    URI_NFS = URI_SERVICES_BASE + '/object/nfs'

    URI_NFS_EXPORTS = URI_NFS + '/exports'
    URI_NFS_EXPORTS_LIST = URI_NFS_EXPORTS + '?namespace={0}'

    URI_NFS_USERS = URI_NFS + '/users'
    URI_NFS_USERS_DELETE = URI_NFS_USERS + '/remove'
    URI_NFS_USERS_LIST = URI_NFS_USERS + '?namespace={0}'


    def __init__(self, ipAddr, port):
        '''
        Constructor: takes IP address and port of the ViPR instance. These are
        needed to make http requests for REST API
        '''
        self.__ipAddr = ipAddr
        self.__port = port


    def nfs_export_create(self, namespace, export_path, export_options):
        '''
        Makes a REST API call to create a new NFS export
        '''

        uri = self.URI_NFS_EXPORTS
	allExportOptions = []
	tmp = export_options.split(" ")
	for hostexport in tmp:
       		hostExportList=hostexport.split(":")
		exportHostSecurity={'host': hostExportList[0],
				    'security': hostExportList[1]}
		allExportOptions.append(exportHostSecurity)	
        parms = {
            'path': export_path,
            'export-options': allExportOptions,
        }

        body = None
        if (parms):
            body = json.dumps(parms)

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "POST", uri, body)
        o = common.json_decode(s)
        return o

    def nfs_export_delete(self, id):
        '''
        Makes a REST API call to delete an NFS export
        '''

        uri = self.URI_NFS_EXPORTS+"/"+id

        body = None

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "DELETE", uri, body)
        o = common.json_decode(s)
        return o

    def nfs_export_list(self, namespace):
        '''
        Makes a REST API call to list NFS exports
        '''

        uri = self.URI_NFS_EXPORTS_LIST.format(namespace)

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "GET", uri, None)
        o = common.json_decode(s)
        return o['exports']


    def nfs_ug_mapping_create(self, namespace, name, id, type):
        '''
        Makes a REST API call to create a new NFS user group mapping
        '''

        uri = self.URI_NFS_USERS
	print namespace;
	print id;
	print type;
        parms = {
            'id': id,
	    'name': name,	
            'namespace': namespace,
            'type': type
        }
        body = None
        if (parms):
            body = json.dumps(parms)

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "POST", uri, body)
        o = common.json_decode(s)
        return o['id']

    def nfs_ug_mapping_delete(self, namespace, name, id, is_user):
        '''
        Makes a REST API call to delete a NFS user group mapping
        '''

        uri = self.URI_NFS_USERS_DELETE

        parms = {
            'tenant': namespace,
            'mappedId': id,
        }

        if(is_user) :
            parms["user"] = name;
        else :
            parms["group"] = name;

        body = None
        if (parms):
            body = json.dumps(parms)

        (s, h) = common.service_json_request(self.__ipAddr, self.__port, "POST", uri, body)
        if(self.__format == "json"):
            o = common.json_decode(s)
        return s

    def nfs_ug_mapping_list(self, namespace):
        '''
        Makes a REST API call to list NFS user group mappings
        '''

        uri = self.URI_NFS_USERS_LIST.format(namespace)
	print self.__ipAddr;
	print self.__port;
	print uri;
        (s, h) = common.service_json_request(self.__ipAddr, self.__port,  "GET", uri, None)
        o = common.json_decode(s)
        return o['mappings'];

def create_nfs_export_command_parser(subcommand_parsers, common_parser):

    # create export command parser
    create_nfs_export_command_parser = subcommand_parsers.add_parser(
        'create-export',
        description='ViPR NFS CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Create an NFS file export')

    mandatory_args = create_nfs_export_command_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-namespace', '-ns',
                                help='Namespace',
                                metavar='<namespace>',
                                dest='namespace',
                                required=True)
    mandatory_args.add_argument('-path',
                                help='Export path',
                                metavar='<path>',
                                dest='path',
                                required=True)

    mandatory_args.add_argument('-exportoptions', '-opts',
                                help='Export options',
                                metavar='<export options>',
                                dest='export_options',
                                required=True)

    create_nfs_export_command_parser.set_defaults(func=nfs_export_create)

def nfs_export_create(args):
    nfs = Nfs(args.ip, args.port)
    try:
        res = nfs.nfs_export_create(
                args.namespace,
                args.path,
                args.export_options)
    except SOSError as e:
        raise e

def delete_nfs_export_command_parser(subcommand_parsers, common_parser):

    # delete export command parser
    delete_nfs_export_command_parser = subcommand_parsers.add_parser(
        'delete-export',
        description='ViPR NFS CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Delete an NFS file export')

    mandatory_args = delete_nfs_export_command_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-id', 
                                help='Pick the id from the list-export.',
                                metavar='id',
                                dest='id',
                                required=True)

    delete_nfs_export_command_parser.set_defaults(func=nfs_export_delete)

def nfs_export_delete(args):
    nfs = Nfs(args.ip, args.port)
    try:
        res = nfs.nfs_export_delete(
            args.id)
    except SOSError as e:
        raise e

def list_nfs_exports_command_parser(subcommand_parsers, common_parser):

    # list exports command parser
    list_nfs_export_command_parser = subcommand_parsers.add_parser(
        'list-export',
        description='ViPR NFS CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='List NFS file exports')

    mandatory_args = list_nfs_export_command_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-namespace', '-ns',
                                help='Namespace',
                                metavar='<namespace>',
                                dest='namespace',
                                required=True)

    list_nfs_export_command_parser.set_defaults(func=nfs_export_list)

def nfs_export_list(args):
    nfs = Nfs(args.ip, args.port)
    try:
        res = nfs.nfs_export_list(args.namespace)
	output = [];

	for iter in res:
		tmp=dict()
		tmp['path']=iter['path'];
		tmp['id']=iter['id'];
		'''
		str1 = "";
		for item in iter['export-options']:
			str1 += str(item)
		tmp['export-opts'] = str1
		'''
		tmp['export-opts'] = str(iter['export-options'])
		output.append(tmp);
        if(res):
            from common import TableGenerator
            TableGenerator(output, ['path', 'id', 'export-opts']).printTable()

    except SOSError as e:
        raise e

def create_nfs_ug_mapping_command_parser(subcommand_parsers, common_parser):

    # create export command parser
    create_nfs_ug_mapping_command_parser = subcommand_parsers.add_parser(
        'create-ug-mapping',
        description='ViPR NFS CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Create a user/group mapping for NFS file export')

    mandatory_args = create_nfs_ug_mapping_command_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-namespace', '-ns',
                                help='Namespace',
                                metavar='<namespace>',
                                dest='namespace',
                                required=True)

    mandatory_args.add_argument('-name',
                                help='name',
                                metavar='<name>',
                                dest='name',
                                required=True)

    mandatory_args.add_argument('-id',
                                help='Id',
                                metavar='<id>',
                                dest='id',
                                required=True)

    mandatory_args.add_argument('-ug',
                                help='Is user or a group. Pass "user" for a user and "group" for a group',
                                metavar='<ug>',
                                dest='ug',
                                required=True)

    create_nfs_ug_mapping_command_parser.set_defaults(func=nfs_ug_mapping_create)


def nfs_ug_mapping_create(args):
    nfs = Nfs(args.ip, args.port)
    try:

        res = nfs.nfs_ug_mapping_create(
            args.namespace,
            args.name,
            args.id,
            args.ug)
    except SOSError as e:
        raise e

def delete_nfs_ug_mapping_command_parser(subcommand_parsers, common_parser):

    # create export command parser
    delete_nfs_ug_mapping_command_parser = subcommand_parsers.add_parser(
        'delete-ug-mapping',
        description='ViPR NFS CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Delete a user/group mapping for NFS file export')

    mandatory_args = delete_nfs_ug_mapping_command_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-namespace', '-ns',
                                help='Namespace',
                                metavar='<namespace>',
                                dest='namespace',
                                required=True)

    mandatory_args.add_argument('-name',
                                help='name',
                                metavar='<name>',
                                dest='name',
                                required=True)

    mandatory_args.add_argument('-id',
                                help='Id',
                                metavar='<id>',
                                dest='id',
                                required=True)

    mandatory_args.add_argument('-ug',
                                help='Is user or a group. Pass "user" for a user and "group" for a group',
                                metavar='<ug>',
                                dest='ug',
                                required=True)

    delete_nfs_ug_mapping_command_parser.set_defaults(func=nfs_ug_mapping_delete)


def nfs_ug_mapping_delete(args):
    nfs = Nfs(args.ip, args.port)
    try:
        if(args.ug == "user" ) :
            is_user = True
        else :
            is_user = False

        res = nfs.nfs_ug_mapping_delete(
            args.namespace,
            args.name,
            args.id,
            is_user)
    except SOSError as e:
        raise e

def list_nfs_ug_mapping_command_parser(subcommand_parsers, common_parser):

    # list exports command parser
    list_nfs_ug_mapping_command_parser = subcommand_parsers.add_parser(
        'list-ug-mapping',
        description='ViPR NFS CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='List NFS user group mappings')

    mandatory_args = list_nfs_ug_mapping_command_parser.add_argument_group('mandatory arguments')

    mandatory_args.add_argument('-namespace', '-ns',
                                help='Namespace',
                                metavar='<namespace>',
                                dest='namespace',
                                required=True)
    list_nfs_ug_mapping_command_parser.set_defaults(func=nfs_ug_mapping_list)

def nfs_ug_mapping_list(args):
    nfs = Nfs(args.ip, args.port)
    try:
        res = nfs.nfs_ug_mapping_list(args.namespace)

        output = []
	'''
        for iter in res:
            tmp = dict()
            tmp['mappingId'] = iter['mappingId']

            name = None
            if ('user' in iter):
                name = iter['user']
            elif ('group' in iter):
                name = iter['group']

            tmp['name'] = iter['name']
            tmp['namespace'] = iter['tenant']

            tmp['User-Group'] = iter['']
            output.append(tmp)
	'''
	for iter in res:
		output.append(iter)
		
        if(res):
            from common import TableGenerator
            TableGenerator(res, ['namespace', 'id', 'name', 'type']).printTable()

    except SOSError as e:
        raise e

#
# Nfs Main parser routine
#
def nfs_parser(parent_subparser, common_parser):
    parser = parent_subparser.add_parser(
        'nfs',
        description='ViPR NFS CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Operations on NFS')
    subcommand_parsers = parser.add_subparsers(help='Use One Of Commands')

    # add nfs export command parsers
    create_nfs_export_command_parser(subcommand_parsers, common_parser)
    delete_nfs_export_command_parser(subcommand_parsers, common_parser)
    list_nfs_exports_command_parser(subcommand_parsers, common_parser)

    # add nfs user group mapping command parsers
    create_nfs_ug_mapping_command_parser(subcommand_parsers, common_parser)
    delete_nfs_ug_mapping_command_parser(subcommand_parsers, common_parser)
    list_nfs_ug_mapping_command_parser(subcommand_parsers, common_parser)
