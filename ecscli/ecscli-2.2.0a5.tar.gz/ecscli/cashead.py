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

class CasHEAD(object):
    URI_CAS_BASE     = '/object/user-cas'
    URI_CAS_SECRET   = '/secret'
    URI_CAS_PEA      = '/pea'
    URI_CAS_BUCKET   = '/bucket'
    URI_CAS_APPS     = '/applications'
    URI_CAS_METADATA = '/metadata'



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
    def get_secret(self, uid, namespace=None):
        url = CasHEAD.URI_CAS_BASE
        url += CasHEAD.URI_CAS_SECRET

        if namespace != None:
            url = url + "/" + namespace

        #uid is a required param, but comes after namespace if namespace is included
        url = url + "/" + uid

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "GET",
                                             url,
                                             None, None, xml)
        if(self.__format == "json"):
            o = common.json_decode(s)
            return common.format_json_object(o)
        return s

    ######################################################
    #
    ######################################################
    def create_update_secret(self, uid, namespace=None, secret=None):
        url = CasHEAD.URI_CAS_BASE
        url += CasHEAD.URI_CAS_SECRET

        xml = False
        if self.__format == "xml":
            xml = True

        request = {}
        if namespace != None:
            request['namespace'] = namespace
        if secret != None:
            request['secret'] = secret

        body = json.dumps(request)

        #uid is a required param, but comes after namespace if namespace is included
        url = url + "/" + uid

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "POST",
                                             url,
                                             body, None, xml)
        if(self.__format == "json"):
            o = common.json_decode(s)
            return common.format_json_object(o)
        return s


    ######################################################
    #
    ######################################################
    def get_pea(self, uid, namespace):
        url = CasHEAD.URI_CAS_BASE
        url += CasHEAD.URI_CAS_SECRET
        

        xml = False
        if self.__format == "xml":
            xml = True

        #uid is a required param, but comes after namespace if namespace is included
        url = url + "/" + namespace + "/" + uid + CasHEAD.URI_CAS_PEA 

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "GET",
                                             url,
                                             None, None, xml)
        if(self.__format == "json"):
            o = common.json_decode(s)
            return common.format_json_object(o)
        return s


    ######################################################
    # POST /object/user-cas/secret/{uid}/deactivate
    ######################################################
    def delete_secret(self, uid, namespace=None, secret=None):
        url = CasHEAD.URI_CAS_BASE
        url = url + CasHEAD.URI_CAS_SECRET + "/" + uid + "/deactivate"

        xml = False
        if self.__format == "xml":
            xml = True

        request = {}
        if namespace != None:
            request['namespace'] = namespace
        if secret != None:
            request['secret'] = secret
        body = json.dumps(request)

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "POST",
                                             url,
                                             body, None, xml)
        if(self.__format == "json"):
            o = common.json_decode(s)
            return common.format_json_object(o)
        return s


    ######################################################
    # GET /object/user-cas/bucket/{namespace}/{uid}
    # GET /object/user-cas/bucket/{uid}
    ######################################################
    def get_bucket(self, uid, namespace=None):
        url = CasHEAD.URI_CAS_BASE
        url += CasHEAD.URI_CAS_BUCKET

        xml = False
        if self.__format == "xml":
            xml = True

        if namespace != None:
            url = url + "/" + namespace

        #uid is a required param, but comes after namespace if namespace is included
        url = url + "/" + uid

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "GET",
                                             url,
                                             None, None, xml)
        if(self.__format == "json"):
            o = common.json_decode(s)
            return common.format_json_object(o)
        return s


    ######################################################
    # POST /object/user-cas/bucket/{namespace}/{uid}
    # all args are required
    ######################################################
    def set_bucket(self, bucket, uid, namespace):
        url = CasHEAD.URI_CAS_BASE
        url += CasHEAD.URI_CAS_BUCKET + "/" + namespace + "/" + uid

        xml = False
        if self.__format == "xml":
            xml = True

        request = {"name":bucket}
        body = json.dumps(request)
        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "POST",
                                             url,
                                             body, None, xml)
        if(self.__format == "json"):
            o = common.json_decode(s)
            return common.format_json_object(o)
        return s


    ######################################################
    # GET /object/user-cas/{namespace}
    ######################################################
    def get_registered_apps(self, namespace):
        url = CasHEAD.URI_CAS_BASE
        url += CasHEAD.URI_CAS_APPS + "/" + namespace

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "GET",
                                             url,
                                             None, None, xml)
        if(self.__format == "json"):
            o = common.json_decode(s)
            return common.format_json_object(o)
        return s


    ######################################################
    # POST /object/user-cas/metadata/{namespace}/{uid}
    # all args are required
    # TODO (JMC): the metadata arg needs parsing from string into map
    #       either in this function or in the parser or somewhere
    ######################################################
    def set_metadata(self, metadata, uid, namespace):
        url = CasHEAD.URI_CAS_BASE
        url += CasHEAD.URI_CAS_METADATA + "/" + namespace + "/" + uid

        xml = False
        if self.__format == "xml":
            xml = True

        request = {"metadata": metadata}
        body = json.dumps(request)
        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "POST",
                                             url,
                                             body, None, xml)
        if(self.__format == "json"):
            o = common.json_decode(s)
            return common.format_json_object(o)
        return s

    ######################################################
    # GET /object/user-cas/metadata/{namespace}/{uid}
    ######################################################
    def get_metadata(self, uid, namespace):
        url = CasHEAD.URI_CAS_BASE
        url += CasHEAD.URI_CAS_METADATA + "/" + namespace + "/" + uid

        xml = False
        if self.__format == "xml":
            xml = True

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "GET",
                                             url,
                                             None, None, xml)
        if(self.__format == "json"):
            o = common.json_decode(s)
            return common.format_json_object(o)
        return s


######################## END CLASS ##############################

######################################################
#
######################################################
def get_secret(args):
    try:
        obj = CasHEAD(args.ip, args.port, args.format)

        #args.namespace might be none. It's not required
        res = obj.get_secret(args.uid, args.namespace)
        return res

    except SOSError as e:
        common.format_err_msg_and_raise(
            "get_secret",
            "cas",
            e.err_text,
            e.err_code)


######################################################
#
######################################################
def create_update_secret(args):
    try:
        obj = CasHEAD(args.ip, args.port, args.format)

        res = obj.create_update_secret(args.uid, args.namespace, args.secret)
        return res

    except SOSError as e:
        common.format_err_msg_and_raise(
            "create_update_secret",
            "cas",
            e.err_text,
            e.err_code)

######################################################
#
######################################################
def get_pea(args):
    try:
        obj = CasHEAD(args.ip, args.port, args.format)

        res = obj.get_pea(args.uid, args.namespace)
        return res

    except SOSError as e:
        common.format_err_msg_and_raise(
            "get_pea",
            "cas",
            e.err_text,
            e.err_code)


######################################################
#
######################################################
def delete_secret(args):
    try:
        obj = CasHEAD(args.ip, args.port, args.format)

        res = obj.delete_secret(args.uid, args.namespace, args.secret)
        return res

    except SOSError as e:
        common.format_err_msg_and_raise(
            "delete_secret",
            "cas",
            e.err_text,
            e.err_code)

######################################################
#                                            
######################################################
def get_bucket(args):                        
    try:
        obj = CasHEAD(args.ip, args.port, args.format)

        #args.namespace might be none. It's not required
        res = obj.get_bucket(args.uid, args.namespace)
        return res

    except SOSError as e:
        common.format_err_msg_and_raise(
            "get_bucket",
            "cas",
            e.err_text,
            e.err_code)


######################################################
#
######################################################
def set_bucket(args):
    try:
        obj = CasHEAD(args.ip, args.port, args.format)

        #args.namespace might be none. It's not required
        res = obj.set_bucket(args.bucket, args.uid, args.namespace)
        return res

    except SOSError as e:
        common.format_err_msg_and_raise(
            "set_bucket",
            "cas",
            e.err_text,
            e.err_code)


######################################################
#
######################################################
def get_registered_apps(args):
    try:
        obj = CasHEAD(args.ip, args.port, args.format)

        #args.namespace might be none. It's not required
        res = obj.get_registered_apps(args.namespace)
        return res

    except SOSError as e:
        common.format_err_msg_and_raise(
            "get_registered_apps",
            "cas",
            e.err_text,
            e.err_code)

######################################################
#
######################################################
def set_metadata(args):
    try:
        obj = CasHEAD(args.ip, args.port, args.format)

        #args.namespace might be none. It's not required
        res = obj.set_metadata(args.metadata, args.uid, args.namespace)
        return res

    except SOSError as e:
        common.format_err_msg_and_raise(
            "set_metadata",
            "cas",
            e.err_text,
            e.err_code)



######################################################
#
######################################################
def get_metadata(args):
    try:
        obj = CasHEAD(args.ip, args.port, args.format)

        res = obj.get_metadata(args.uid, args.namespace)
        return res

    except SOSError as e:
        common.format_err_msg_and_raise(
            "get_metadata",
            "cas",
            e.err_text,
            e.err_code)



######################################################
#
######################################################
def get_secret_parser(subcommand_parsers, common_parser):
    get_secret_parser = subcommand_parsers.add_parser(
        'get_secret', description='ECS get cas secret for user',
        parents=[common_parser],
        conflict_handler='resolve',
        help='get CAS secret')

    mandatory_args = get_secret_parser.add_argument_group(
        'mandatory arguments')

    mandatory_args.add_argument('-uid', '-uid',
                               dest='uid',
                               metavar='<uid>',
                               help='CAS uid',
                               required=True)

    get_secret_parser.add_argument('-namespace', '-ns',
                        help='CAS namespace')

    get_secret_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    get_secret_parser.set_defaults(func=get_secret)


######################################################
#
######################################################
def create_update_secret_parser(subcommand_parsers, common_parser):
    create_update_secret_parser = subcommand_parsers.add_parser(
        'create_update_secret', description='ECS create or update cas secret for user',
        parents=[common_parser],
        conflict_handler='resolve',
        help='create/update CAS secret')

    mandatory_args = create_update_secret_parser.add_argument_group(
        'mandatory arguments')

    mandatory_args.add_argument('-uid', '-uid',
                               dest='uid',
                               metavar='<uid>',
                               help='CAS uid',
                               required=True)

    create_update_secret_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")


    create_update_secret_parser.add_argument('-namespace', '-ns',
                        help='CAS namespace')

    create_update_secret_parser.add_argument('-secret', '-secret',
                        help='CAS namespace')


    create_update_secret_parser.set_defaults(func=create_update_secret)

######################################################
#
######################################################
def get_pea_parser(subcommand_parsers, common_parser):
    get_pea_parser = subcommand_parsers.add_parser(
        'get_pea', description='ECS get cas pea for user with namespace',
        parents=[common_parser],
        conflict_handler='resolve',
        help='get CAS pea')

    mandatory_args = get_pea_parser.add_argument_group(
        'mandatory arguments')

    mandatory_args.add_argument('-uid', '-uid',
                               dest='uid',
                               metavar='<uid>',
                               help='CAS uid',
                               required=True)

    get_pea_parser.add_argument('-namespace', '-ns',
                        help='CAS namespace')

    get_pea_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    get_pea_parser.set_defaults(func=get_pea)



######################################################
#
######################################################
def delete_secret_parser(subcommand_parsers, common_parser):
    delete_secret_parser = subcommand_parsers.add_parser(
        'delete_secret', description='ECS delete cas secret for user',
        parents=[common_parser],
        conflict_handler='resolve',
        help='delete CAS secret')

    mandatory_args = delete_secret_parser.add_argument_group(
        'mandatory arguments')

    mandatory_args.add_argument('-uid', '-uid',
                               dest='uid',
                               metavar='<uid>',
                               help='CAS uid',
                               required=True)

    delete_secret_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")


    delete_secret_parser.add_argument('-namespace', '-ns',
                        help='CAS namespace')

    delete_secret_parser.add_argument('-secret', '-secret',
                        help='CAS namespace')

    delete_secret_parser.set_defaults(func=delete_secret)


######################################################
#
######################################################
def get_bucket_parser(subcommand_parsers, common_parser):
    get_bucket_parser = subcommand_parsers.add_parser(
        'get_bucket', description='ECS get cas bucket for user',
        parents=[common_parser],
        conflict_handler='resolve',
        help='get CAS bucket for uid/namespace')

    mandatory_args = get_bucket_parser.add_argument_group(
        'mandatory arguments')

    mandatory_args.add_argument('-uid', '-uid',
                               dest='uid',
                               metavar='<uid>',
                               help='CAS uid',
                               required=True)

    get_bucket_parser.add_argument('-namespace', '-ns',
                        help='CAS namespace')

    get_bucket_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    get_bucket_parser.set_defaults(func=get_bucket)

######################################################
#
######################################################
def set_bucket_parser(subcommand_parsers, common_parser):
    set_bucket_parser = subcommand_parsers.add_parser(
        'set_bucket', description='ECS set cas bucket for user',
        parents=[common_parser],
        conflict_handler='resolve',
        help='set CAS bucket for uid/namespace')

    mandatory_args = set_bucket_parser.add_argument_group(
        'mandatory arguments')

    mandatory_args.add_argument('-uid', '-uid',
                               dest='uid',
                               metavar='<uid>',
                               help='CAS uid',
                               required=True)

    mandatory_args.add_argument('-namespace', '-ns',
                        help='CAS namespace')

    mandatory_args.add_argument('-bucket', '-b',
                        help='CAS bucket name')

    set_bucket_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    set_bucket_parser.set_defaults(func=set_bucket)

######################################################
#
######################################################
def get_registered_apps_parser(subcommand_parsers, common_parser):
    get_registered_apps_parser = subcommand_parsers.add_parser(
        'get_registered_apps', description='ECS get cas registered applications for user',
        parents=[common_parser],
        conflict_handler='resolve',
        help='get CAS registered applications for namespace')

    mandatory_args = get_registered_apps_parser.add_argument_group(
        'mandatory arguments')

    mandatory_args.add_argument('-namespace', '-ns',
                        help='CAS namespace')

    get_registered_apps_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    get_registered_apps_parser.set_defaults(func=get_registered_apps)


######################################################
#
######################################################
def set_metadata_parser(subcommand_parsers, common_parser):
    set_metadata_parser = subcommand_parsers.add_parser(
        'set_metadata', description='ECS set cas metadata for user',
        parents=[common_parser],
        conflict_handler='resolve',
        help='set CAS metadata for uid/namespace')

    mandatory_args = set_metadata_parser.add_argument_group(
        'mandatory arguments')

    mandatory_args.add_argument('-uid', '-uid',
                               dest='uid',
                               metavar='<uid>',
                               help='CAS uid',
                               required=True)

    mandatory_args.add_argument('-namespace', '-ns',
                        help='CAS namespace')

    mandatory_args.add_argument('-metadata', '-md', dest='metadata',
                        help="CAS metadata value should be entered in format 'key':'value','key':'value'...")

    set_metadata_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    set_metadata_parser.set_defaults(func=set_metadata)

######################################################
#
######################################################
def get_metadata_parser(subcommand_parsers, common_parser):
    get_metadata_parser = subcommand_parsers.add_parser(
        'get_metadata', description='ECS get cas metadata for user with namespace',
        parents=[common_parser],
        conflict_handler='resolve',
        help='get CAS user metadata')

    mandatory_args = get_metadata_parser.add_argument_group(
        'mandatory arguments')

    mandatory_args.add_argument('-uid', '-uid',
                               dest='uid',
                               metavar='<uid>',
                               help='CAS uid',
                               required=True)

    get_metadata_parser.add_argument('-namespace', '-ns',
                        help='CAS namespace')

    get_metadata_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    get_metadata_parser.set_defaults(func=get_metadata)


######################################################
#this is the main parent parser for cas
######################################################
def cashead_parser(parent_subparser, common_parser):
    parser = parent_subparser.add_parser(
        'cas',
        description='ECS CAS profile CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Operations on CAS profile')
    subcommand_parsers = parser.add_subparsers(help='use one of sub-commands')

    get_secret_parser(subcommand_parsers, common_parser) 
    create_update_secret_parser(subcommand_parsers, common_parser)
    get_pea_parser(subcommand_parsers, common_parser)
    delete_secret_parser(subcommand_parsers, common_parser)
    get_bucket_parser(subcommand_parsers, common_parser)
    set_bucket_parser(subcommand_parsers, common_parser)
    get_registered_apps_parser(subcommand_parsers, common_parser)
    set_metadata_parser(subcommand_parsers, common_parser)
    get_metadata_parser(subcommand_parsers, common_parser)

