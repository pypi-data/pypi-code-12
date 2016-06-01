#!/usr/bin/python

# Copyright (c) 2014 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

import codecs
import common
import datetime
import metering
import os
import StringIO
import xml.etree.ElementTree as et
from common import SOSError
from datetime import timedelta
from _elementtree import fromstring
from matplotlib.pyparsing import empty

class Report(object):
    
    '''
    Class definition for usage reporting operations.
    '''
    def __init__(self, ipAddr, port, out_name):
        '''
        Constructor: Takes IP address and port of instance for
        REST API requests; defines destination directory for
        generated reports, forms metering object to produce statistics.
        '''
        self.__meter = metering.Meter(ipAddr, port)

        if out_name is not None :
            self.__out_name = out_name
            if os.path.isfile(out_name) :
                os.remove(out_name)

        self.__tagged = False
                
    def format_stats(self, time_slice, output_format):
        
        '''
        Gets statistics regarding resource usage for the specified time
        frame and formats a report in the specified way. User may
        specify namespace and bucket to include in report, or specify
        to include all buckets or all namespaces.
        Parameters:
            time_slice: string in yyyy-mm-ddThh:mm format
        Return:
            Report of usage statistics.
        '''
        
        #Containers for output information
        output_buffer = []
        output = None

        # open the xml file for iteration
        xml_in = StringIO.StringIO(self.__meter.get_stats('xml', time_slice))
        context = et.iterparse(xml_in, events=("start", "end"))
        
        # output file definition
        if output_format == 'csv' :
            try:
                output = codecs.open(self.__out_name, "a", encoding='utf-8')
            except:
                print("Failed to open the output file")
                raise
        
        # get to the root
        event, root = context.next()

        #Variables for output buffers
        items = []
        header_line = []
        field_name = ''
        delim = ','
        colWidth = 15       #Recommend console width to be multiple of (colWidth+3) for readability
        time_header = 'time_measured'
        if output_format == 'ascii' : delim = '|'
        started = False
        
        if self.__tagged and output_format == 'csv': output.write('\n')

        # iterate through the xml
        for event, elem in context:
            # if elem is an unignored child node of the record tag, it should be written to buffer
            should_write = elem.tag != 'stats' and started
            should_tag = should_write and not self.__tagged
            
            # set
            if event == 'start':
                if not started:
                    started = True
                elif should_tag:
                    # if elem is nested inside a "parent", field name becomes parent_elem
                    field_name = elem.tag
                    if output_format == 'ascii' :
                        field_name = (field_name[:colWidth]).ljust(colWidth, ' ')
                    
            else:
                if should_write and elem.tag != 'element':
                    if should_tag:
                        #Force timestamp to leftmost in layout
                        if elem.tag == time_header:
                            header_line = [field_name] + header_line
                        else:
                            header_line.append(field_name)  # add field name to csv header
                    # remove current tag from the tag name chain
                    field_name = field_name.rpartition('_' + elem.tag)[0]
                        
                    newItem = ' '*colWidth
                    if not (elem.text is None) :
                        newItem = (elem.text.strip().replace('"', r'""')[:colWidth]).ljust(colWidth, ' ')
                    
                    if elem.tag == time_header:
                        items = [newItem] + items
                    else:
                        items.append(newItem)
                    
                # end of traversing the record tag
                elif len(items) > 0:
                    # csv header (element tag names)
                    if header_line and not self.__tagged:
                        if output_format == 'ascii' :
                            print(((r' ' + delim + r' ').join(header_line))[:-2])
                            print ''
                        else:
                            output.write(delim.join(header_line) + '\n')
                    self.__tagged = True

                    # send the csv to buffer
                    if output_format == 'csv':
                        output_buffer.append(r'"' + (r'"' + delim + r'"').join(items) + r'"')
                    else:
                        output_buffer.append(r' ' + (r' ' + delim + r' ').join(items) + r' ')
                    items = []

                    # flush buffer
                    if len(output_buffer) > 1000:
                        if output_format == 'ascii' :
                            print ((' '.join(output_buffer))[1:-3])
                        else:
                            output.write('\n'.join(output_buffer))
                        output_buffer = []

                elem.clear()  # discard element; recover memory

                # write remaining buffer to file
                if output_format == 'ascii' :
                    if output_buffer != [] : print ((' '.join(output_buffer))[1:-3])
                else:
                    output.write('\n'.join(output_buffer))
                output_buffer = []
            
        return output
            
        
def get_report(args):
    
    st = datetime.datetime(int(args.year), int(args.month), int(args.day), 
                           int(args.hour), int(args.minute), 0)
    
    try:
        os.mkdir(out_path)
    except Exception:
        pass
    
    if args.format == 'csv' :
        out_path = os.path.expanduser(args.destdir)
        out_name = out_path + '/' + 'report' + '_' + st.strftime("%Y%m%d_%H%M") + '.csv'
    else:
        out_name = ' '

    obj = Report(args.ip, args.port, out_name)
    
    #Confirm/define sample size.
    if not int(args.sampletime) % 5 == 0 :
        exit(2)
    numsamples = int(args.sampletime) // 5
    
    if (args.format == 'ascii') : print ''
    
    try:
        #Iterate through timeslice in 5-minute chunks
        for i in range(numsamples) :
            time_slice = common.get_formatted_time_string(st.year, st.month, st.day,
                                                           st.hour, st.minute)
        
            obj.format_stats(time_slice, args.format)
            #update time slice
            st = st + datetime.timedelta(minutes=5)
    
    except ValueError as e:
        raise SOSError(SOSError.CMD_LINE_ERR, "arg parsing error: " + str(e))
        exit(1)
    except SOSError as e:
        if (e.err_code == SOSError.SOS_FAILURE_ERR):
            raise SOSError(SOSError.SOS_FAILURE_ERR,
                           "Unable to generate report")
        exit(1)
    if (args.format == 'ascii') : print ''
        

def report_parser(parent_subparser, common_parser):
    #main reporting parser

    parser = parent_subparser.add_parser('report',
                                         description='ViPR storage reporting CLI usage',
                                         parents=[common_parser],
                                         conflict_handler='resolve',
                                         help='Get usage report for' +
                                         ' the given storage area and time')
    
    mandatory_args = parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-year', '-y',
                                help='Year', dest='year',
                                metavar='<year>')
    mandatory_args.add_argument('-month', '-mon',
                                metavar='<month>', dest='month',
                                help='month of the year {1 - 12}')
    mandatory_args.add_argument('-day', '-d',
                                metavar='<day>', dest='day',
                                help='day of the month {01 - 31}')
    mandatory_args.add_argument('-hour', '-hr',
                                metavar='<hour>', dest='hour',
                                help='hour of the day {00 - 23}')
    parser.add_argument('-minute', '-min',
                        metavar='<minute>', dest='minute',
                        help='minute of the hour {00 - 59}')
    parser.add_argument('-sampletime', '-st',
                        metavar='<sampletime>', dest='sampletime',
                        help='length of time to sample bucket in minutes;' +
                        ' must be multiple of 5 (default: 5)',
                        default=5)
    parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: csv or ascii (default:ascii)',
                        choices=['csv', 'ascii'],
                        default="csv")
    parser.add_argument('-destdir', '-dd',
                        metavar='<destdir>', dest='destdir',
                        help='destination directory for report files' + 
                        ' (default: ~/Documents/vipr)',
                        default='~/Documents/vipr')
    parser.set_defaults(func=get_report)
