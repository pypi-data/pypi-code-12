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
import time
import datetime
import collections

class Billing(object):
    URI_BILLING_BASE      = '/object/billing'
    URI_BILLING_BUCKETS   = '/buckets'
    URI_BILLING_NAMESPACE = '/namespace'

    URI_BILLING_INFO      = '/info'
    URI_BILLING_SAMPLE    = '/sample'

    BUCKET_BILLING_INFO = 'name,namespace ,vpool_id,total_size_in_gb,total_objects'

    BUCKET_INFO_COLS          = ['name', 'namespace', 'vpool_id', 'total_size_in_gb', 'total_objects', 'sample_time']
    NAMESPACE_INFO_COLS       = ['name', 'namespace', 'vpool_id', 'total_size_in_gb', 'total_objects', 'sample_time']
    NAMESPACE_INTO_COLS_TOTAL = ['next_marker', 'total_size_in_gb', 'total_objects', 'namespace', 'sample_time']

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
        elif (output_format == "csv"):
           self.__format = "csv"

    ######################################################
    # The cli call for this method only returns 1 row if bucket is specified
    # so it only returns a string at this point in that case
    ######################################################
    def get_billinginfo(self, detail, namespace, bucket=None):
        url = Billing.URI_BILLING_BASE
        marker_qp = '?marker='

        #buckets or namespace billing
        if bucket:
            url += Billing.URI_BILLING_BUCKETS + "/" + namespace + "/" + bucket
        else:
            url += Billing.URI_BILLING_NAMESPACE + "/" + namespace

        url += Billing.URI_BILLING_INFO

        # include_bucket_detail flag
        if (bucket is None and detail is not None):
            url += '?include_bucket_detail=' + detail.lower()
            marker_qp = '&marker='

        xml = False
        if self.__format == "xml":
            xml = True

        #JMC - need time window....+ info or sample and namespace/bucket info
        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "GET",
                                             url,
                                             None, None, xml)

        if (not xml):
            ret = common.json_decode(s)
            if bucket is None:
                while ret['next_marker'] is not '':
                    (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                                         "GET",
                                                         url + marker_qp + ret['next_marker'],
                                                         None, None, xml)
                    o = common.json_decode(s)
                    for item in o['bucket_billing_info']:
                        ret['bucket_billing_info'].append(item)
                    ret['total_objects'] += o['total_objects']
                    ret['total_size_in_gb'] += o['total_size']
                    ret['next_marker'] = o['next_marker']

        else:
            ret = s
            if bucket is None:
                marker = ret[(ret.rfind('<next_marker>') + 13):(ret.rfind('</next_marker>'))]
                while len(marker) >= 1:
                    (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                                         "GET",
                                                         url + marker_qp + marker,
                                                         None, None, xml)
                    ret = ret + s
                    marker = s[(s.rfind('<next_marker>') + 13):(s.rfind('</next_marker>'))]
            return ret


        #GET /object/billing/buckets/{namespace}/{bucketName}/info
        #in this case only 1 row is returned
        if (self.__format == "csv") and (bucket is not None):
            # fnBase = start_time + "_" + end_time + "_b_" + bucket + "_ns_" + namespace + "_info"
            fnBase = "b_" + bucket + "_ns_" + namespace + "_info"
            # print(s) #JMC
            self.csv_writeAll(ret, fnBase, None)
            return

        #GET /object/billing/namespace/{namespace}/info 
        #could have many bucket_billinginfo[] items in it
        if(self.__format == "csv"):
            # fnBase = start_time + "_" + end_time + "_ns_" + namespace  + "_info"
            fnBase = "ns_" + namespace + "_info"
            # print(s) #JMC
            self.csv_writeAll(ret, fnBase, None)
            return

        # print("JMC: " + s)
        return common.format_json_object(ret)


    ######################################################
    # prints the values of a dictionary to csv file
    # cols are keys within the dict and at some point maybe be configurable
    # to be a subset of all keys in the dictionary
    ######################################################
    def printItem(self, fd, item, cols):
        for c in cols[:-1]:
            fd.write( str(item[c]) + "," )
        fd.write( str(item[ cols[-1] ]))
        fd.write('\n')

    ######################################################
    # get an array of keys from the dict
    # however, if one of the values in the dict is itself a dictionary
    # or an array of dictionaries, then recursively handle that
    ######################################################
    def getCols(self, obj, fNameBase):
        cols = []
        for key in obj.keys():
            #if it's a list,array, etc type then it's an a sequence of obj dict instances, so recurse with that array
            if hasattr(obj[key], '__iter__') and (len(obj[key])>0):
                self.csv_writeAll(obj[key], fNameBase, key)
            elif hasattr(obj[key], '__iter__'):
                #this section is here for any debug needs
                pass
            elif (isinstance(obj[key], collections.Mapping)):
                self.csv_writeAll(obj[key], fNameBase, key)
            else:
                cols.append(key)
        return cols

    ######################################################
    #
    ######################################################
    def csv_writeAll(self, obj, fNameBase, addl=None):
        if isinstance(obj, unicode):
            obj = common.json_decode(obj)
        else:
            #this block is here for any debug needs
            pass

        filename = fNameBase
        if addl:
            filename += "_" + addl + "_"
        else:
            #this block is here for any debug needs
            pass

        #create the list of columns
        cols = []
        singleItem = True

        if (isinstance(obj, collections.Mapping)):
            cols = self.getCols(obj, filename)
        elif hasattr(obj[0], '__iter__') and (len(obj)>0) and (isinstance(obj[0], collections.Mapping)):
            cols = self.getCols(obj[0], filename)
            singleItem = False
        else:
            print("JMC it is NOT a collections.Mapping object or the first one is not a list")
            print("JMC it is type: " + str(type(firstObj)))

        filename += ".csv"
        print("JMC outfile: " + filename)
        with open(filename, 'w') as outfile:
            #write the column headers
            for c in cols[:-1]:
                outfile.write( c + "," ) 
            outfile.write(cols[-1] )
            outfile.write('\n')
        
            #obj could be an array of dicts(recurion case) or a single dict instance
            #since we don't know, we are treating the single
            #if necessary I may determine by checking 'addl == None'
            if singleItem:
                self.printItem(outfile, obj, cols)
            else:
                for o in obj:
                    self.printItem(outfile, o, cols)

    ######################################################
    #
    ######################################################
    def csv_writeOld(self, obj, fNameBase, colsArrTotal, colsArr=None):
        filename = fNameBase + '_total.csv'
        with open(filename, 'w') as outfile_total:
            print("JMC outfile_total: " + filename)
            #write the column headers
            for c in Billing.NAMESPACE_INTO_COLS_TOTAL[:-1]:
                outfile_total.write( c + "," ) 
            outfile_total.write(Billing.NAMESPACE_INTO_COLS_TOTAL[-1] )
            outfile_total.write('\n')

            for c in Billing.NAMESPACE_INTO_COLS_TOTAL[:-1]:
                print("JMC" + str(obj[c]))
                outfile_total.write( str(obj[c]) + "," )
            outfile_total.write( str(obj[ Billing.NAMESPACE_INTO_COLS_TOTAL[-1] ]))
            outfile_total.write('\n')



    ######################################################
    #
    ######################################################
    def get_billingsample(self, start_time, end_time, detail, namespace, bucket=None):
        url = Billing.URI_BILLING_BASE
        marker_qp = '&marker='

        #buckets or namespace billing
        if bucket:
            url += Billing.URI_BILLING_BUCKETS + "/" + namespace + "/" + bucket
        else:
            url += Billing.URI_BILLING_NAMESPACE + "/" + namespace

        url += Billing.URI_BILLING_SAMPLE

        #handle the time window
        url += '?'
        url += 'start_time=' + start_time + '&end_time=' + end_time

        # include_bucket_detail flag
        if (bucket is None and detail is not None):
            url += '&include_bucket_detail=' + detail.lower()

        xml = False
        if self.__format == "xml":
            xml = True

        #JMC - need time window....+ info or sample and namespace/bucket info
        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "GET",
                                             url,
                                             None, None, xml)
        if (not xml):
            ret = common.json_decode(s)
            if bucket is None:
                while ret['next_marker'] is not '':
                    (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                                         "GET",
                                                         url + marker_qp + ret['next_marker'],
                                                         None, None, xml)
                    o = common.json_decode(s)
                    for item in o['bucket_billing_sample']:
                        ret['bucket_billing_sample'].append(item)
                    ret['total_objects'] += o['total_objects']
                    ret['total_size_in_gb'] += o['total_size']
                    ret['next_marker'] = o['next_marker']

        else:
            ret = s
            if bucket is None:
                marker = ret[(ret.rfind('<next_marker>') + 13):(ret.rfind('</next_marker>'))]
                while len(marker) >= 1:
                    (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                                         "GET",
                                                         url + marker_qp + marker,
                                                         None, None, xml)
                    ret = ret + s
                    marker = s[(s.rfind('<next_marker>') + 13):(s.rfind('</next_marker>'))]
            return ret

        #GET /object/billing/buckets/{namespace}/{bucketName}/sample
        #in this case only 1 row is returned
        if (self.__format == "csv") and (bucket is not None):
           fnBase = start_time + "_" + end_time + "_b_" + bucket + "_ns_" + namespace + "_sample"
           #print(s) #JMC
           self.csv_writeAll(ret, fnBase, None)
           return

        #GET /object/billing/namespace/{namespace}/sample
        #could have many bucket_billinginfo[] items in it
        if(self.__format == "csv"):
           fnBase = start_time + "_" + end_time + "_ns_" + namespace + "_sample"
           #print(s) #JMC
           self.csv_writeAll(ret, fnBase, None)
           return

        # print("JMC: " + s)
        return common.format_json_object(ret)


######################## END CLASS ##############################

######################################################
# for either namespace or bucket
# from here, the time window can be broken into chunks which
# calls the class instance methods iteratively
# each time chunk will be separate file so the instance methods don't
# need to know anything about it
######################################################
def get_billinginfo(args):
    try:
        obj = Billing(args.ip, args.port, args.format)

        result = obj.get_billinginfo(args.bucket_detail, args.namespace, args.bucket)
        return result

    except SOSError as e:
        common.format_err_msg_and_raise(
            "info",
            "billing",
            e.err_text,
            e.err_code)


######################################################
# for either namespace or bucket
######################################################
def get_billingsample(args):
    try:
        obj = Billing(args.ip, args.port, args.format)

        startTime = time.strptime(args.start_time, "%Y-%m-%dT%H:%MZ")
        endTime = time.strptime(args.end_time, "%Y-%m-%dT%H:%MZ")

        if (endTime <= startTime):
            print("error: end_time must be greater than start_time")
            return

        res = obj.get_billingsample(args.start_time, args.end_time, args.bucket_detail,
                                    args.namespace, args.bucket)
        return res

    except SOSError as e:
        common.format_err_msg_and_raise(
            "sample",
            "billing",
            e.err_text,
            e.err_code)


######################################################
# namespace is required for all URIs
# bucket is optional and effects the URI
# start_time and end_time are required and will return error otherwise
######################################################
def get_billinginfo_parser(subcommand_parsers, common_parser):
    get_billinginfo_parser = subcommand_parsers.add_parser(
        'info', description='retrieves ECS billing total information',
        parents=[common_parser],
        conflict_handler='resolve',
        help='get ECS billing info')

    mandatory_args = get_billinginfo_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-namespace','-ns',help='user namespace', required=True)

    get_billinginfo_parser.add_argument('-start_time', '-st',
                                        help='start datetime in format YYYY-MM-DDThh:mmZ must be at a 5min interval')
    get_billinginfo_parser.add_argument('-end_time', '-et',
                                        help='end datetime in format YYYY-MM-DDThh:mmZ must be at 5min interval')

    get_billinginfo_parser.add_argument('-bucket', '-b',
                                        help='specific bucket to sample')

    get_billinginfo_parser.add_argument('-bucket_detail', '-bd',
                                        help='boolean flag to include info on all buckets')

    get_billinginfo_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml, json or csv (default:json)',
                        choices=['xml', 'json', 'csv'],
                        default="json")

    get_billinginfo_parser.set_defaults(func=get_billinginfo)

######################################################
# namespace is required for all URIs
# bucket is optional and effects the URI
# start_time and end_time are required and will return error otherwise
######################################################
def get_billingsample_parser(subcommand_parsers, common_parser):
    get_billingsample_parser = subcommand_parsers.add_parser(
        'sample', description='retrieves ECS billing total information',
        parents=[common_parser],
        conflict_handler='resolve',
        help='get ECS billing sample information which are details specific to objects')

    mandatory_args = get_billingsample_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-namespace','-ns',help='user namespace', required=True)
    mandatory_args.add_argument('-start_time','-st',help='start datetime in format YYYY-MM-DDThh:mmZ must be at a 5min interval', required=True)
    mandatory_args.add_argument('-end_time', '-et',
                                help='end datetime in format YYYY-MM-DDThh:mmZ must be at 5min interval', required=True)

    get_billingsample_parser.add_argument('-bucket', '-b',
                                          help='specific bucket to sample')

    get_billingsample_parser.add_argument('-bucket_detail', '-bd',
                                          help='boolean flag to include info on all buckets')

    get_billingsample_parser.add_argument('-format', '-f',
                        metavar='<format>', dest='format',
                        help='response format: xml, json or csv (default:json)',
                        choices=['xml', 'json', 'csv'],
                        default="json")

    get_billingsample_parser.set_defaults(func=get_billingsample)


######################################################
#this is the main parent parser for cas
######################################################
def billing_parser(parent_subparser, common_parser):
    parser = parent_subparser.add_parser(
        'billing',
        description='get ECS billing info ',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Operations to retrieve ECS billing information')
    subcommand_parsers = parser.add_subparsers(help='use one of sub-commands')

    get_billinginfo_parser(subcommand_parsers, common_parser)
    get_billingsample_parser(subcommand_parsers, common_parser)

