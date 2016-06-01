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


class Monitor(object):

    '''
    The class definition for operations on 'Monitoring'.
    '''
    # Commonly used URIs for the 'Monitoring' module
    URI_MONITOR0 = '/vdc/events' #shouldn't be used since start_time is required, but safety
    URI_MONITOR1 = '/vdc/events.{0}/?start_time={1}'
    URI_MONITOR2 = '/vdc/events.{0}/?start_time={1}&end_time{2}'



    def __init__(self, ipAddr, port):
        '''
        Constructor: takes IP address and port of the SOS instance.
        These are needed to make http requests for REST API
        '''
        self.__ipAddr = ipAddr
        self.__port = port

    def get_events(self, output_format, time_frame):
        '''
        Makes REST API call to get the events
        during the given time frame
        Parameters:
            time_frame: string in yyyy-mm-ddThh:mm
        Returns:
            Event details in response payload
        '''
        url = Monitor.URI_MONITOR0
        if(time_frame.end_time):
            print("JMC there is an end_time");
            url = Monitor.URI_MONITOR2.format(output_format,time_frame.start_time, time_frame.end_time)
        else:
            print("JMC there is no end_time")
            url = Monitor.URI_MONITOR1.format(output_format,time_frame.start_time)

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "GET",
                                             url,
                                             None)
        if(output_format == "json"):
            o = common.json_decode(s)
            return common.format_json_object(o)
        return s


def monitor_get_events(args):
    obj = Monitor(args.ip, args.port)
    try:
        '''
        JMC
        if(int(args.year) <= 1900):
            print("error: year=" + args.year +
                  " is before 1900, it require year >= 1900")
            return

        time_frame = common.get_formatted_time_string(args.year,
                                                      args.month, args.day,
                                                      args.hour, args.minute)

        '''

        startTime = time.strptime(args.start_time, "%Y-%m-%dT%H:%M")
        if (args.end_time):
            endTime = time.strptime(args.end_time, "%Y-%m-%dT%H:%M")

        print("JMC startYear: " + str(startTime.tm_year))
        if(startTime.tm_year <=1900):
            print("error: years > 1900 are required")
            return

        if(args.end_time and endTime.tm_year <=1900):
            print("error: years > 1900 are required")
            return

        if(args.end_time and endTime <= startTime):
            print("error: end_time must come after start_time")
            return

        res = obj.get_events(args.format, args)
        return res

    except ValueError as e:
        raise SOSError(SOSError.CMD_LINE_ERR, "error: " + str(e))
    except SOSError as e:
        if (e.err_code == SOSError.SOS_FAILURE_ERR):
            raise SOSError(SOSError.SOS_FAILURE_ERR,
                           "Unable to get requested usage events")
        else:
            raise e


def monitor_parser(parent_subparser, common_parser):
    # main monitoring parser
    parser = parent_subparser.add_parser('monitor',
                                         description='SOS monitoring' +
                                         ' CLI usage',
                                         parents=[common_parser],
                                         conflict_handler='resolve',
                                         help='Get monitoring events for' +
                                         ' the given time bucket')
    mandatory_args = parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-start_time','-st',help='start datetime in format YYYY-mm-DDTHH:MM', required=True)
    mandatory_args.add_argument('-end_time','-et',help='start datetime in format YYYY-mm-DDTHH:MM', required=False)

    parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml or json (default:json)',
                        choices=['xml', 'json'],
                        default="json")

    parser.set_defaults(func=monitor_get_events)
