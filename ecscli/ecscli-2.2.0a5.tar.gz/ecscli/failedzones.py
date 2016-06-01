#!/usr/bin/python

# Copyright (c) 2012 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

import time
import common
from common import SOSError


class Zones(object):

    '''
    The class definition for operations on 'Monitoring'.
    '''
    # Commonly used URIs for the 'Monitoring' module
    URI_TEMPFAILEDZONES_ALL = '/tempfailedzone/allfailedzones'
    URI_TEMPFAILEDZONES_RGID = '/tempfailedzone/rgid'




    def __init__(self, ipAddr, port, output_format=None):
        '''
        Constructor: takes IP address and port of the SOS instance.
        These are needed to make http requests for REST API
        '''
        self.__ipAddr = ipAddr
        self.__port = port
        self.__format = "json"
        if (output_format == 'xml'):
           self.__format = "xml"

    def get_info_all(self):
        url = Zones.URI_TEMPFAILEDZONES_ALL

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

    def get_info_rgid(self, rgid):
        url = Zones.URI_TEMPFAILEDZONES_RGID
        url += "/" + rgid

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



def failedzones_get_info(args):
    obj = Zones(args.ip, args.port, args.format)
    try:
        res = None
        if args.repGrpId != None:
            res = obj.get_info_rgid(args.repGrpId)
        else:
            res = obj.get_info_all()
        
        return res

    except ValueError as e:
        raise SOSError(SOSError.CMD_LINE_ERR, "error: " + str(e))
    except SOSError as e:
        if (e.err_code == SOSError.SOS_FAILURE_ERR):
            raise SOSError(SOSError.SOS_FAILURE_ERR,
                           "Unable to get requested usage events")
        else:
            raise e


def failedzone_parser(parent_subparser, common_parser):
    # main monitoring parser
    parser = parent_subparser.add_parser('failedzones',
                                         description='get configured temp failed zone info' +
                                         ' CLI usage',
                                         parents=[common_parser],
                                         conflict_handler='resolve',
                                         help='Get failed zone information')

    parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")


    parser.add_argument('-repGrpId', '-rgid',
                        help='allows retrieval of failed zone info for particular replication group id')

    parser.set_defaults(func=failedzones_get_info)
