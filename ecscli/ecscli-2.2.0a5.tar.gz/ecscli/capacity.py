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


class Capacity(object):

    '''
    The class definition for operations on 'Monitoring'.
    '''
    # Commonly used URIs for the 'Capacity' module
    URI_CAPACITY = '/object/capacity'


    ######################################################
    #
    ######################################################
    def __init__(self, ipAddr, port, output_format = None):
        '''
        Constructor: takes IP address and port of the SOS instance.
        These are needed to make http requests for REST API
        The output_format can be json or xml and defaults to xml
        '''
        self.__ipAddr = ipAddr
        self.__port = port
        self.__format = "json"
        if (output_format == 'xml'):
           self.__format = "xml"

    ######################################################
    #
    ######################################################
    def get_capacity_info(self, vId = None):
        '''
        Makes REST API call to get the events
        during the given time frame
        Parameters:
            time_frame: string in yyyy-mm-ddThh:mm
        Returns:
            Event details in response payload
        '''
        url = Capacity.URI_CAPACITY
        if(vId):
            print("JMC there is a vId arg")
            url += '/' + vId

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
def get_capacity_info(args):
    obj = Capacity(args.ip, args.port, args.format)
    try:
        res = obj.get_capacity_info(args.vArrayId)
        return res

    except ValueError as e:
        raise SOSError(SOSError.CMD_LINE_ERR, "error: " + str(e))
    except SOSError as e:
        if (e.err_code == SOSError.SOS_FAILURE_ERR):
            raise SOSError(SOSError.SOS_FAILURE_ERR,
                           "Unable to get requested usage events")
        else:
            raise e


######################################################
#this is the main parent parser for capacity
######################################################
def capacity_parser(parent_subparser, common_parser):
    # main monitoring parser
    parser = parent_subparser.add_parser('capacity',
                                         description='get capacity of the cluster or a particular array within the cluster',
                                         parents=[common_parser],
                                         conflict_handler='resolve',
                                         help='Get capacity information')
    parser.add_argument('-vArrayId', '-vId',
                        metavar='<vArrayId>', dest='vArrayId',
                        help='vArrayId within the cluster')

    parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    parser.set_defaults(func=get_capacity_info)
