#!/usr/bin/python

# Copyright (c) 2012 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

import common
import urllib
import datetime
import json
import os
import re
from common import SOSError


class Logging(object):

    '''
    The class definition for Logging
    '''

    # Commonly used URIs for Logging service
    URI_LOGS = "/logs"
    URI_LOG_LEVELS = URI_LOGS + "/log-levels"

    URI_SEND_ALERT = "/vdc/callhome/alert/"
    URI_GET_ESRSCONFIG = "/vdc/callhome/connectemc/config"
    URI_GET_ESRSCONFIG_DEACTIVATE = "/vdc/callhome/connectemc/config/deactivate"
    URI_LICENSE = "/license"

    ####################################################
    #
    ####################################################
    def __init__(self, ipAddr, port, output_format):
        '''
        Constructor: takes IP address and port of the SOS instance.
        These are needed to make http requests for REST API
        '''
        self.__ipAddr = ipAddr
        self.__port = port
        self.__format = "json"
        if (output_format == "xml"):
            self.__format = "xml"

    ####################################################
    #
    ####################################################
    def direct_print_log_unit(self, unit, accept='json', filehandle=None):

        if unit is None:
            print_str = ''
            if(filehandle):
                try:
                    filehandle.write(print_str)
                except IOError:
                    pass
            else:
                print print_str

            return

        if accept == 'json':
            print_str = "{\n" + "\tnode:\t\t" + (
                            unit.get('node')
                            if unit.get('node') is not None else "") + "\n" \
                        + "\tseverity:\t" + (
                            unit.get('severity')
                            if unit.get('severity') is not None else "") + "\n" \
                        + "\tthread:\t\t" + (
                            unit.get('thread')
                            if unit.get('thread') is not None else "") + "\n" \
                        + "\tmessage:\t" + (
                            unit.get('message').replace('\n', '\n\t\t\t')
                            if unit.get('message') is not None else "") + "\n" \
                        + "\tservice:\t" + (
                            unit.get('service')
                            if unit.get('service') is not None else "") + "\n" \
                        + "\ttime:\t\t" + (
                            unit.get('time')
                            if unit.get('time') is not None else "") + "\n" \
                        + "\tline:\t\t" + (
                            str(unit.get('line'))
                            if unit.get('line') is not None else "") + "\n" \
                        + "\tclass:\t\t" + (
                            unit.get('class')
                            if unit.get('class') is not None else "") + "\n" \
                        + "}" + "\n"

            if(filehandle):
                try:
                    filehandle.write(print_str)
                except IOError:
                    pass

        elif accept == 'xml':
            print_str = "<log>" + "\n" \
                + "\t<node>\t\t" + (
                    unit.get('node')
                    if unit.get('node') is not None else "") + \
                "</node>" + "\n" \
                + "\t<severity>\t" + (
                    unit.get('severity')
                    if unit.get('severity') is not None else "") + \
                "</severity>" + "\n" \
                + "\t<thread>\t" + (
                    unit.get('thread')
                    if unit.get('thread') is not None else "") + \
                "</thread>" + "\n" \
                + "\t<message>\t" + (
                    unit.get('message').replace('\n', '\n\t\t\t')
                    if unit.get('message') is not None else "") + \
                "</message>" + "\n" \
                + "\t<service>\t" + (
                    unit.get('service')
                    if unit.get('service') is not None else "") + \
                "</service>" + "\n" \
                + "\t<time>\t\t" + (
                    unit.get('time')
                    if unit.get('time') is not None else "") + \
                "</time>" + "\n" \
                + "\t<line>\t\t" + (
                    str(unit.get('line'))
                    if unit.get('line') is not None else "") + \
                "</line>" + "\n" \
                + "\t<class>\t\t" + (
                    unit.get('class')
                    if unit.get('class') is not None else "") + \
                "</class>" + "\n" \
                + "</log>" + "\n"

            if(filehandle):
                try:
                    filehandle.write(print_str)
                except IOError:
                    pass

        # textplain with fillers
        elif accept == 'text/plain':
            # general logs
            if unit.get('class'):
                utcTime = datetime.datetime.utcfromtimestamp(
                    unit.get('time_ms') / 1000.0).strftime(
                    '%Y-%m-%d %H:%M:%S,%f')[:-3]
                print_str = utcTime + ' ' + unit.get('node') + ' ' + \
                    unit.get('service') + ' [' + unit.get('thread') + '] ' + \
                    unit.get('severity') + ' ' + unit.get('class') + \
                    ' (line ' + (str)(unit.get('line')) + ') ' + \
                    unit.get('message') + '\n'
            # system logs
            else:
                print_str = unit.get('time') + ',000 ' + unit.get('node') + \
                    ' ' + unit.get('service') + ' [-] ' + \
                    unit.get('severity') + \
                    ' - ' + '(line -) ' + unit.get('message') + '\n'

            if(filehandle):
                try:
                    filehandle.write(print_str)
                except IOError:
                    pass
        # native text
        else:
            # general logs
            if unit.get('class'):
                utcTime = datetime.datetime.utcfromtimestamp(
                    unit.get('time_ms') / 1000.0).strftime(
                    '%Y-%m-%d %H:%M:%S,%f')[:-3]
                print_str = utcTime + ' ' + unit.get('node') + ' ' + \
                    unit.get('service') + ' [' + unit.get('thread') + '] ' + \
                    unit.get('severity') + ' ' + unit.get('class') + \
                    ' (line ' + str(unit.get('line')) + ') ' + \
                    unit.get('message') + '\n'
            # system logs
            else:
                print_str = unit.get('time') + ',000 ' + unit.get('node') + \
                    ' ' + unit.get('service') + ' ' + unit.get('severity') + \
                    ' ' + unit.get('message') + '\n'

            if(filehandle):
                try:
                    filehandle.write(print_str)
                except IOError:
                    pass

    ####################################################
    #
    ####################################################
    def get_logs(self, log, severity, start, end, node,
                 regex, format, maxcount, filepath):

        params = ''
        if (log != ''):
            params += '&' if ('?' in params) else '?'
            params += "log_name=" + log
        if (severity != ''):
            params += '&' if ('?' in params) else '?'
            params += "severity=" + severity
        if (start != ''):
            params += '&' if ('?' in params) else '?'
            params += "start=" + start
        if (end != ''):
            params += '&' if ('?' in params) else '?'
            params += "end=" + end
        if (node != ''):
            params += '&' if ('?' in params) else '?'
            params += "node_id=" + node
        if (regex != ''):
            params += '&' if ('?' in params) else '?'
            params += "msg_regex=" + urllib.quote_plus(regex.encode("utf8"))
        if (maxcount != ''):
            params += '&' if ('?' in params) else '?'
            params += "maxcount=" + maxcount

        tmppath = filepath + ".tmp"

        (res, h) = common.service_json_request(self.__ipAddr,
                                               self.__port,
                                               "GET",
                                               self.URI_LOGS + params,
                                               None,
                                               None,
                                               False,
                                               None,
                                               tmppath)

        resp = None
        try:
            if(os.path.getsize(tmppath) > 0):
                with open(tmppath) as infile:
                    resp = json.load(infile)
        except ValueError:
            raise SOSError(SOSError.VALUE_ERR,
                           "Failed to recognize JSON payload")
        except Exception as e:
            raise SOSError(e.errno, e.strerror)

        fp = None
        if(filepath):
            try:
                fp = open(filepath, 'w')
            except IOError as e:
                raise SOSError(e.errno, e.strerror)

        if resp:
            if 'error' in resp:
                print resp.get('error')
            elif isinstance(resp, list):
                layer1_size = len(resp)
                i = 0
                while i < layer1_size:
                    if(resp[i]):   
                        self.direct_print_log_unit(resp[i], format, fp)
                    i += 1

            try:
                os.remove(tmppath)
            except IOError:
                pass

        else:
            print "No log available."

        if(fp):
            fp.close()

        if(not resp):
            return None

    ####################################################
    #
    ####################################################
    def get_log_level(self, loglst, nodelst):
        request = ""

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "GET", Logging.URI_LOG_LEVELS +
                                             self.prepare_get_log_lvl_params(
                                                 loglst,
                                                 nodelst),
                                             None)
        if(not s):
            return None
        o = common.json_decode(s)
        return o

    ####################################################
    #
    ####################################################
    def set_log_level(self, severity, logs, nodes, expiretime):
        request = ""

        params = self.prepare_set_log_level_body(severity, logs, nodes,
                                                  expiretime)

        if (params):
            body = json.dumps(params)

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "POST", Logging.URI_LOG_LEVELS,
                                             body)
        if(not s):
            return None
        o = common.json_decode(s)
        return o

    ####################################################
    # 'Callhome' 'Send Alert"
    ####################################################
    def send_alert(self, args):

        logparams = self.prepare_params(args)

        uriparams = self.prepare_alert_params(logparams, args)

        params = self.prepare_body(args)

        if (params):
            body = json.dumps(params)

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "POST", Logging.URI_SEND_ALERT +
                                             uriparams,
                                             body)

        if(not s):
            return None

        o = common.json_decode(s)
        return o

    ####################################################
    #
    ####################################################
    def get_esrsconfig(self):
        url = Logging.URI_GET_ESRSCONFIG
        if (self.__format == "json"):
           url = Logging.URI_GET_ESRSCONFIG + ".json"

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "GET", url,
                                             None)
        if(not s):
            return None

        if (self.__format == "json"):
            s = common.format_json_object(common.json_decode(s))
        return s

    ####################################################
    #
    ####################################################
    def esrsconfig_deactivate(self):
        url = Logging.URI_GET_ESRSCONFIG_DEACTIVATE
        if (self.__format == "json"):
           url = Logging.URI_GET_ESRSCONFIG

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "GET", url,
                                             None)
        if(not s):
            return None

        if (self.__format == "json"):
            s = common.format_json_object(common.json_decode(s))
        return s

    ####################################################
    # used by send alert to format user input into a msg
    ####################################################
    def prepare_params(self, args):

        params = self.prepare_get_log_lvl_params(args.log, args.node)

        if (args.severity != ''):
            params += '&' if ('?' in params) else '?'
            params += "severity=" + args.severity
        if (args.start != ''):
            params += '&' if ('?' in params) else '?'
            params += "start=" + args.start
        if (args.end != ''):
            params += '&' if ('?' in params) else '?'
            params += "end=" + args.end
        if (args.regular != ''):
            params += '&' if ('?' in params) else '?'
            params += "msg_regex=" + \
                urllib.quote_plus(args.regular.encode("utf8"))
        if (args.maxcount != ''):
            params += '&' if ('?' in params) else '?'
            params += "maxcount=" + args.maxcount
        return params

    ####################################################
    # used by send alert to format user input into a msg
    ####################################################
    def prepare_get_log_lvl_params(self, loglst, nodelst):
        params = ''
        if(loglst):
            for log in loglst:
                params += '&' if ('?' in params) else '?'
                params += "log_name=" + log
        if(nodelst):
            for node in nodelst:
                params += '&' if ('?' in params) else '?'
                params += "node_id=" + node
        return params

    ####################################################
    # used by send alert to format user input into a msg
    ####################################################
    def prepare_alert_params(self, params, args):
        if (args.source != ''):
            params += '&' if ('?' in params) else '?'
            params += "source=" + args.source
        if (args.eventid != ''):
            params += '&' if ('?' in params) else '?'
            params += "event_id=" + args.eventid
        return params

    ####################################################
    # send alert - formats info into post body
    ####################################################
    def prepare_body(self, args):
        params = {'user_str': args.message,
                  'contact': args.contact
                  }
        return params

    ####################################################
    # send alert msg help
    ####################################################
    def prepare_set_log_level_body(self, severity, logs, nodes, expiretime):
        params = {'severity': int(severity)}
        if (logs):
            params['log_name'] = logs
        if (nodes):
            params['node_id'] = nodes
        if (expiretime):
            params['expir_in_min'] = expiretime

        return params

    ####################################################
    #
    ####################################################
    def prepare_license_body(self, args):
        text = ''
        features = ''
        feature_obj = {}
        if args.licensetextfile:
            try:
                with open(args.licensetextfile, 'r') as content_file:
                    text = content_file.read()
                text = text.rstrip('\n')
            except Exception as e:
                #raise SOSError(e.errno, e.strerror)
                raise Exception("Exception: error getting license text file")


        params = {}
        params["license_feature"] = []
        if args.licensefeaturefiles == '':
            ffs = args.licensefeaturefiles.split(',')
            for aff in ffs: 
                features = ''
                try:
                    with open(aff, 'r') as content_file:
                        features = content_file.read()
                    features = features.rstrip('\n')

                    feature_obj, status, err_txt = self.validate_license_features(features)
                    if (status == False):
                        print("Warning: missing features in " + aff + " - " + err_txt)
                        #raise Exception("Exception: " + err_txt)
                    params["license_feature"].append(feature_obj)

                except Exception as e:
                    print("Warning: Error retrieving feature file: " + aff)
                    #raise SOSError(e.errno, e.strerror)
                    #raise Exception("Exception: error getting license feature file")


        params = {"license_text": text}

        return params

    ####################################################
    #
    ####################################################
    def validate_license_features(self, features):
        o = common.json_decode("{" + features + "}")
        status = True
        missing_features = []
        err_txt = ""

        try:
            for theAttr in ["serial", "version", "issued_date", "expiration_date", "model", "product", "site_id", "issuer", "notice", "licensed_ind",\
                "expired_ind", "license_id_indicator", "error_message", "storage_capacity_unit", "storage_capacity", "trial_license_ind"]:
                if o.get(theAttr) is None:
                    status = False
                    missing_features.append(theAttr)

                else:
                    val = o.get(theAttr)
                    if val == "False":
                        o[theAttr] = "false"
                    if val == "True":
                        o[theAttr] = true

            if status == False:
                err_txt = "missing license features: " + str(missing_features)
        except Exception as e:
            raise SOSError(e.errno, e.strerror)

        return (o, status, err_txt)
            

    ####################################################
    #
    ####################################################
    def get_license(self):

        if (self.__format == "xml"):
            Logging.URI_LICENSE += ".xml"
        else:
            Logging.URI_LICENSE += ".json"

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "GET", Logging.URI_LICENSE,
                                             None)
        if(not s):
            return None
        o = common.json_decode(s)
        return o

    ####################################################
    #
    ####################################################
    def add_license(self, args):
        if(args.licensetextfile is ""):
            raise SOSError(SOSError.CMD_LINE_ERR,
                           "License file path can not be empty string")

        params = self.prepare_license_body(args)

        if (params):
            body = json.dumps(params)

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "POST", Logging.URI_LICENSE,
                                             body)
        if(not s):
            return None

        o = common.json_decode(s)
        return o

class Configuration(object):

    '''
    The class definition for Configuration
    '''

    URI_CONFIGURE_CONNECTEMC_SMTP = "/vdc/callhome/connectemc/config/email"
    URI_CONFIGURE_CONNECTEMC_FTPS = "/vdc/callhome/connectemc/config/ftps"

    URI_PROPS = "/config/object/properties/"
    URI_PROPS_CATEGORY = "/config/object/properties?category={0}"
    URI_PROPS_METADATA = "/config/object/properties/metadata"
    URI_RESET_PROPS = "/config/object/properties/reset/"
    
    URI_CONFIG_PROPERTY_TYPE = ['ovf', 'config', 'mutated', 'obsolete', 'all']
    UPDATE_PROPERTY_IGNORE_LIST = [
        'system_svcuser_encpassword',
        'system_sysmonitor_encpassword',
        'system_root_encpassword',
        'system_proxyuser_encpassword']

    ####################################################
    #
    ####################################################
    def __init__(self, ipAddr, port, output_format):
        '''
        Constructor: takes IP address and port of the SOS instance.
        These are needed to make http requests for REST API
        '''
        self.__ipAddr = ipAddr
        self.__port = port
        self.__format = "json"
        if (output_format == "xml"):
            self.__format = "xml"

    ####################################################
    # 'Callhome' 'connectemc-ftps'
    ####################################################
    def configure_connectemc_ftps(self, args):
        params = self.prepare_connectemc_ftps_body(args)

        if (params):
            body = json.dumps(params)

        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "POST", Configuration.URI_CONFIGURE_CONNECTEMC_FTPS,
            body)
        if(not s):
            return None

        o = common.json_decode(s)
        return o

    ####################################################
    #
    ####################################################
    def configure_connectemc_smtp(self, args):
        params = self.prepare_connectemc_smtp_body(args)

        if (params):
            body = json.dumps(params)

        url = Configuration.URI_CONFIGURE_CONNECTEMC_SMTP
        if (self.__format == "json"):
            url += ".json"

        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "POST", url,
            body)
        if(not s):
            return None

        if (self.__format == "json"):
            s = common.json_decode(s)
        return s

    ####################################################
    # 
    ####################################################
    def prepare_connectemc_ftps_body(self, args):
        params = {'bsafe_encryption_ind': 'no',
                  'host_name': args.ftpserver
                  }
        return params

    ####################################################
    #
    ####################################################
    def prepare_connectemc_smtp_body(self, args):
        params = {'bsafe_encryption_ind': 'no',
                  'email_server': args.smtpserver,
                  'primary_email_address': args.primaryemail,
                  'email_sender': args.senderemail
                  }
        return params

    ####################################################
    #
    ####################################################
    def get_properties(self, type=None):
        uri_conf = None
        if(type == None):
            uri_conf = Configuration.URI_PROPS
        else:
            uri_conf = Configuration.URI_PROPS_CATEGORY.format(type)
        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "GET", uri_conf,
                                             None)
        if(not s):
            return None

        o = common.json_decode(s)

        return o


    ####################################################
    #
    ####################################################
    def get_properties_metadata(self):
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "GET", Configuration.URI_PROPS_METADATA,
            None)
        if(not s):
            return None

        o = common.json_decode(s)

        return o

    ####################################################
    #
    ####################################################
    def set_properties(self, propertiesfile, propertyname, propertyvaluefile):

        try:
            if(propertiesfile):
                f = open(propertiesfile, 'r')
                props = []
                for line in f:
                    props.append(line)

            elif(propertyname):
                f = open(propertyvaluefile, 'r')
                content = f.read()

        except Exception as e:
            raise SOSError(e.errno, e.strerror)

        if(propertiesfile):
            params = self.prepare_properties_body(props)
        elif(propertyname):
            params = self.prepare_custom_properties_body(propertyname, content)

        if (params):
            body = json.dumps(params)

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "PUT", Configuration.URI_PROPS,
                                             body)
        if(not s):
            return None

        o = common.json_decode(s)
        return o

    ####################################################
    #
    ####################################################
    def prepare_properties_body(self, props):
        params = dict()
        properties = dict()
        params['properties'] = properties
        properties['entry'] = []
        for prop in props:
            matching = re.match("(.+?)=(.*)\n?", prop)
            if matching:
                key, value = matching.groups()

                if(key in Configuration.UPDATE_PROPERTY_IGNORE_LIST):
                    print "Skipping the update for the property "+key
                    continue

                entry = dict()
                entry['key'] = key
                entry['value'] = value
                properties['entry'].append(entry)
        return params

    ####################################################
    #
    ####################################################
    def prepare_custom_properties_body(self, propertyname, propertyvalue):
        params = dict()
        properties = dict()
        params['properties'] = properties
        properties['entry'] = []
        entry = dict()
        entry['key'] = propertyname
        entry['value'] = propertyvalue
        properties['entry'].append(entry)

        return params


    ####################################################
    #
    ####################################################
    def get_download_filename(self, content_disposition):
        content_disposition = content_disposition.replace(" ", "")
        matching = re.match("(.*)filename=(.+)", content_disposition)
        if matching:
            filename = matching.group(2)
            return filename
        else:
            return ""

    ####################################################
    #
    ####################################################
    def write_to_file(self, filename, mode, content):
        try:
            with open(filename, mode) as f:
                f.write(content.encode('utf-8'))
        except IOError as e:
            raise SOSError(e.errno, e.strerror)

####################################################
#
####################################################        
def get_logs_parser(subcommand_parsers, common_parser):
    get_logs_parser = subcommand_parsers.add_parser('get-logs',
                                                    description='ECS: CLI' +
                                                    ' usage to get the logs',
                                                    parents=[common_parser],
                                                    conflict_handler='resolve',
                                                    help='Get logs')

    get_logs_parser.add_argument('-log', '-lg',
                                 metavar='<logname>',
                                 dest='log',
                                 help='Log Name',
                                 default='')

    add_log_args(get_logs_parser)

    get_logs_parser.set_defaults(func=get_logs)


####################################################
#
####################################################
def get_alerts_parser(subcommand_parsers, common_parser):
    get_alerts_parser = subcommand_parsers.add_parser(
        'get-alerts',
        description='ECS: CLI' +
        ' usage to get' +
        ' the alerts',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Get alerts')

    add_log_args(get_alerts_parser)

    get_alerts_parser.set_defaults(func=get_alerts)

####################################################
#
####################################################
def get_alerts(args):
    obj = Logging(args.ip, args.port)
    log = "systemevents"
    from common import TableGenerator
    try:
        res = obj.get_logs(
            log,
            args.severity,
            args.start,
            args.end,
            args.node,
            args.regular,
            args.format,
            args.maxcount,
            args.filepath)
    except SOSError as e:
        common.format_err_msg_and_raise("get", log, e.err_text, e.err_code)

####################################################
#
####################################################
def get_logs(args):
    obj = Logging(args.ip, args.port)
    from common import TableGenerator
    try:
        res = obj.get_logs(
            args.log,
            args.severity,
            args.start,
            args.end,
            args.node,
            args.regular,
            args.format,
            args.maxcount,
            args.filepath)
    except SOSError as e:
        common.format_err_msg_and_raise("get", "logs", e.err_text, e.err_code)

####################################################
#
####################################################
def get_log_level_parser(subcommand_parsers, common_parser):
    get_log_level_parser = subcommand_parsers.add_parser(
        'get-log-level',
        description='ECS:' +
        ' CLI usage to get' +
        ' the logging level',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Get log level')

    get_log_level_parser.add_argument('-logs', '-lg',
                                      metavar='<logs>',
                                      dest='logs',
                                      help='Logs Name',
                                      nargs="+")

    get_log_level_parser.add_argument('-nodes', '-nds',
                                      metavar='<nodes>',
                                      dest='nodes',
                                      help='Nodes',
                                      nargs="+")

    get_log_level_parser.set_defaults(func=get_log_level)

####################################################
#
####################################################
def get_log_level(args):
    obj = Logging(args.ip, args.port)
    from common import TableGenerator
    try:
        res = obj.get_log_level(args.logs, args.nodes)
        return common.format_json_object(res)
    except SOSError as e:
        common.format_err_msg_and_raise(
            "get",
            "log level",
            e.err_text,
            e.err_code)

####################################################
#
####################################################
def set_log_level_parser(subcommand_parsers, common_parser):
    set_log_level_parser = subcommand_parsers.add_parser(
        'set-log-level',
        description='ECS:' +
        ' CLI usage to set' +
        ' the logging level',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Set logging' +
        ' level')

    set_log_level_parser.add_argument('-severity', '-sv',
                                      metavar='<severity>',
                                      dest='severity',
                                      help='Any value from 0,4,5,7,8,9' +
                                      '(FATAL, ERROR, WARN, INFO, DEBUG,' +
                                      ' TRACE).',
                                      choices=['0', '4', '5', '7', '8', '9'],
                                      default='7')

    set_log_level_parser.add_argument('-logs', '-lg',
                                      metavar='<logs>',
                                      dest='logs',
                                      help='Logs Name',
                                      nargs="+")

    set_log_level_parser.add_argument('-nodes', '-nds',
                                      metavar='<nodes>',
                                      dest='nodes',
                                      help='Nodes',
                                      nargs="+")
    set_log_level_parser.add_argument('-expiretime', '-ext',
                                  metavar='<expiretime>',
                                  dest='expiretime',
                                  type=int,
                                  help='log level expiration time in minutes')

    '''set_log_level_parser.add_argument('-type',
                                metavar='<type>',
                                dest='type',
                                help='type')'''

    set_log_level_parser.set_defaults(func=set_log_level)

####################################################
#
####################################################
def set_log_level(args):
    obj = Logging(args.ip, args.port)
    from common import TableGenerator
    try:
        res = obj.set_log_level(args.severity, args.logs, args.nodes, args.expiretime)
    except SOSError as e:
        common.format_err_msg_and_raise(
            "set",
            "log level",
            e.err_text,
            e.err_code)
####################################################
#
####################################################
def add_log_args(parser, sendAlertFlag=False):
    parser.add_argument('-severity', '-sv',
                        metavar='<severity>',
                        dest='severity',
                        help='Any value from 0,4,5,7,8,9' +
                        '(FATAL, ERROR, WARN, INFO, DEBUG, TRACE).',
                        choices=['0', '4', '5', '7', '8', '9'],
                        default='7')

    parser.add_argument('-start', '-st',
                        metavar='<start>',
                        dest='start',
                        help='start date in yyyy-mm-dd_hh:mm:ss format' +
                        ' or in milliseconds',
                        default='')

    parser.add_argument('-end', '-en',
                                metavar='<end>',
                                dest='end',
                                help='end date in yyyy-mm-dd_hh:mm:ss format' +
                                ' or in milliseconds',
                                default='')

    parser.add_argument('-node', '-nd',
                        metavar='<node_id>',
                        dest='node',
                        help='Node',
                        default='')

    parser.add_argument('-regular', '-regex',
                        metavar='<msg_regex>',
                        dest='regular',
                        help='Message Regex',
                        default='')

    parser.add_argument('-format', '-fm',
                        dest='format',
                        help='Response: xml, json, text/plain',
                        choices=['xml', 'json', 'text/plain'],
                        default='json')

    parser.add_argument('-maxcount', '-mc',
                        metavar='<maxcount>',
                        dest='maxcount',
                        help='Maximum number of log messages to retrieve',
                        default='')

    mandatory_args = parser.add_argument_group('mandatory arguments')

    if(sendAlertFlag is False):
        mandatory_args.add_argument('-filepath', '-fp',
                                    help='file path',
                                    metavar='<filepath>',
                                    dest='filepath',
                                    required=True)

####################################################
#
####################################################
def add_license_parser(subcommand_parsers, common_parser):

    add_license_parser = subcommand_parsers.add_parser('add-license',
                                                       description='ECS:' +
                                                       ' CLI usage to' +
                                                       ' add license',
                                                       parents=[common_parser],
                                                       conflict_handler='res' +
                                                       'olve',
                                                       help='Add license')

    mandatory_args = add_license_parser.add_argument_group(
        'mandatory arguments')

    mandatory_args.add_argument('-licensetextfile', '-ltf',
                                help='Name of the license file',
                                dest='licensetextfile',
                                required=True)

    add_license_parser.add_argument('-licensefeaturefiles', '-lffs',
                                help='Name of one or more license feature files(comma separated list of files) , each file is a "name":"strval, "name":"strval".. of the features',
                                dest='licensefeaturefiles',
                                required=False)


    add_license_parser.set_defaults(func=add_license)

####################################################
#
####################################################
def add_license(args):
    obj = Logging(args.ip, args.port, "json")
    try:
        obj.add_license(args)
    except SOSError as e:
        common.format_err_msg_and_raise(
            "add",
            "license",
            e.err_text,
            e.err_code)

####################################################
#
####################################################
def get_license_parser(subcommand_parsers, common_parser):
    get_license_parser = subcommand_parsers.add_parser('get-license',
                                                       description='ECS:' +
                                                       ' CLI usage to' +
                                                       ' get license',
                                                       parents=[common_parser],
                                                       conflict_handler='res' +
                                                       'olve',
                                                       help='Get License.')

    get_license_parser.add_argument('-format', '-fm',
                        dest='format',
                        help='Response: xml, json, text/plain',
                        choices=['xml', 'json', 'text/plain'],
                        default='json')

    get_license_parser.set_defaults(func=get_license)

####################################################
#
####################################################
def get_license(args):
    obj = Logging(args.ip, args.port, args.format)
    try:
        return obj.get_license()
    except SOSError as e:
        common.format_err_msg_and_raise(
            "get",
            "license",
            e.err_text,
            e.err_code)

####################################################
#
####################################################
def get_esrsconfig_parser(subcommand_parsers, common_parser):

    get_esrsconfig_parser = subcommand_parsers.add_parser(
        'get-callhome-config',
        description='ECS: CLI usage to get esrs callhome configuration',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Retrieves the connectemc callhome configuration')

    get_esrsconfig_parser.add_argument('-format', '-fm',
                        dest='format',
                        help='Response: xml, json, text/plain',
                        choices=['xml', 'json', 'text/plain'],
                        default='json')

    get_esrsconfig_parser.set_defaults(func=get_esrsconfig)

####################################################
#
####################################################
def get_esrsconfig_deactivate_parser(subcommand_parsers, common_parser):
    get_esrsconfig_deactivate_parser = subcommand_parsers.add_parser(
        'deactivate-callhome',
        description='ECS: CLI usage to get esrs callhome configuration',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Retrieves the connectemc callhome configuration')

    get_esrsconfig_deactivate_parser.set_defaults(func=get_esrsconfig_deactivate)

####################################################
#
####################################################
def get_esrsconfig(args):
    obj = Logging(args.ip, args.port, args.format)

    try:
        return obj.get_esrsconfig()
    except SOSError as e:
        common.format_err_msg_and_raise(
            "get",
            "ESRS Config",
            e.err_text,
            e.err_code)
####################################################
#
####################################################
def get_esrsconfig_deactivate(args):
    obj = Logging(args.ip, args.port, "")

    try:
        return obj.esrsconfig_deactivate()
    except SOSError as e:
        common.format_err_msg_and_raise(
            "get",
            "ESRS Config",
            e.err_text,
            e.err_code)

####################################################
#
####################################################
def send_alert_parser(subcommand_parsers, common_parser):

    send_alert_parser = subcommand_parsers.add_parser(
        'send-alert',
        description='ECS: CLI usage to send alert',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Send alert with logs. Event attachments size' +
        ' cannot exceed more than 16 MB compressed size.' +
        ' Please select time window for logs (with help of start,' +
        ' end parameters) during which issue might have occurred.')

    add_log_args(send_alert_parser, True)

    send_alert_parser.add_argument('-src', '-source',
                                   metavar='<target_version>',
                                   dest='source',
                                   help='Send Alert',
                                   default='')

    send_alert_parser.add_argument('-eventid', '-eid',
                                   metavar='<event_id>',
                                   dest='eventid',
                                   help='Event Id',
                                   default='')

    send_alert_parser.add_argument('-msg', '-message',
                                   metavar='<message>',
                                   dest='message',
                                   help='Message',
                                   default='')

    send_alert_parser.add_argument('-contact', '-ct',
                                   metavar='<contact>',
                                   dest='contact',
                                   help='Contact',
                                   default='')

    send_alert_parser.add_argument('-log', '-lg',
                                   metavar='<logname>',
                                   dest='log',
                                   help='Log Name',
                                   default='')

    send_alert_parser.set_defaults(func=send_alert)

####################################################
#
####################################################
def send_alert(args):
    obj = Logging(args.ip, args.port)
    try:
        return obj.send_alert(args)
    except SOSError as e:
        common.format_err_msg_and_raise(
            "send",
            "alert",
            e.err_text,
            e.err_code)

####################################################
#
####################################################
def connectemc_ftps_parser(subcommand_parsers, common_parser):

    connectemc_ftps_parser = subcommand_parsers.add_parser(
        'connectemc-ftps',
        description='ECS: CLI usage of connect EMC by ftps',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Connect EMC using ftps.')

    mandatory_args = connectemc_ftps_parser.add_argument_group(
        'mandatory arguments')

    mandatory_args.add_argument('-ftpserver', '-fsvr',
                                help='ftpserver',
                                metavar='<ftpserver>',
                                dest='ftpserver',
                                required=True)

    connectemc_ftps_parser.set_defaults(func=connectemc_ftps)

####################################################
#
####################################################
def connectemc_ftps(args):
    obj = Configuration(args.ip, args.port, "")
    try:
        obj.configure_connectemc_ftps(args)
    except SOSError as e:
        common.format_err_msg_and_raise(
            "connect",
            "ftps",
            e.err_text,
            e.err_code)

####################################################
#
####################################################
def connectemc_smtp_parser(subcommand_parsers, common_parser):

    connectemc_smtp_parser = subcommand_parsers.add_parser(
        'connectemc-smtp',
        description='ECS: CLI usage of connect EMC by smtp',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Connect EMC using smtp.')


    connectemc_smtp_parser.add_argument('-format', '-fm',
                        dest='format',
                        help='Response: xml, json, text/plain',
                        choices=['xml', 'json', 'text/plain'],
                        default='json')

    mandatory_args = connectemc_smtp_parser.add_argument_group(
        'mandatory arguments')

    mandatory_args.add_argument('-primaryemail', '-pm',
                                help='primaryemail',
                                metavar='<primaryemail>',
                                dest='primaryemail',
                                required=True)

    mandatory_args.add_argument('-smtpserver', '-sms',
                                help='smtpserver',
                                metavar='<smtpserver>',
                                dest='smtpserver',
                                required=True)

    mandatory_args.add_argument('-senderemail', '-se',
                                help='senderemail',
                                metavar='<senderemail>',
                                dest='senderemail',
                                required=True)

    connectemc_smtp_parser.set_defaults(func=connectemc_smtp)

####################################################
#
####################################################
def connectemc_smtp(args):
    obj = Configuration(args.ip, args.port, args.format)
    try:
        obj.configure_connectemc_smtp(args)
    except SOSError as e:
        common.format_err_msg_and_raise(
            "connect",
            "smtp",
            e.err_text,
            e.err_code)

####################################################
#
####################################################
def get_properties_parser(subcommand_parsers, common_parser):
    get_properties_parser = subcommand_parsers.add_parser(
        'get-properties',
        description='ECS: CLI usage to get properties',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Get Properties.')
    get_properties_parser.add_argument(
        '-type', '-t',
        choices=Configuration.URI_CONFIG_PROPERTY_TYPE,
        help='configuration property type',
        dest='type')


    get_properties_parser.set_defaults(func=get_properties)

####################################################
#
####################################################
def get_properties(args):
    obj = Configuration(args.ip, args.port, "")
    try:
        return common.format_json_object(obj.get_properties(args.type))
    except SOSError as e:
        common.format_err_msg_and_raise(
            "get",
            "properties",
            e.err_text,
            e.err_code)

####################################################
#
####################################################
def get_properties_metadata_parser(subcommand_parsers, common_parser):

    get_properties_metadata_parser = subcommand_parsers.add_parser(
        'get-properties-metadata',
        description='ECS: CLI usage to get properties metadata',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Get Properties Meta Data.')

    get_properties_metadata_parser.set_defaults(func=get_properties_metadata)

####################################################
#
####################################################
def get_properties_metadata(args):
    obj = Configuration(args.ip, args.port, "")
    try:
        return common.format_json_object(obj.get_properties_metadata())
    except SOSError as e:
        common.format_err_msg_and_raise(
            "get",
            "properties metadata",
            e.err_text,
            e.err_code)

####################################################
#
####################################################
def set_properties_parser(subcommand_parsers, common_parser):

    set_properties_parser = subcommand_parsers.add_parser(
        'set-properties',
        description='ECS: CLI usage to set properties',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Set Properties.')

    mandatory_args = set_properties_parser.add_argument_group(
        'mandatory arguments')

    arggroup = set_properties_parser.add_mutually_exclusive_group(
        required=True)

    arggroup.add_argument('-propertyfile', '-pf',
                          help='property file',
                          metavar='<propertyfile>',
                          dest='propertyfile')

    arggroup.add_argument('-propertyname', '-pn',
                          help='property name',
                          metavar='<propertyname>',
                          dest='propertyname')

    set_properties_parser.add_argument('-propertyvaluefile', '-pvf',
                                       help='property value file',
                                       metavar='<propertyvaluefile>',
                                       dest='propertyvaluefile')

    set_properties_parser.set_defaults(func=set_properties)

####################################################
#
####################################################
def set_properties(args):
    obj = Configuration(args.ip, args.port, "")
    try:
        if(args.propertyname):
            if(args.propertyname in Configuration.UPDATE_PROPERTY_IGNORE_LIST):
                raise SOSError(SOSError.CMD_LINE_ERR, "The property " +
                               args.propertyname + " can not be updated " +
                               "through CLI") 

            if(not args.propertyvaluefile):
                raise SOSError(SOSError.CMD_LINE_ERR,
                               "When propertyname is specified," +
                               " the file containing the value of the" +
                               " property should also be specified" +
                               " using the -propertyvaluefile/-pvf option")

        common.format_json_object(
            obj.set_properties(
                args.propertyfile,
                args.propertyname,
                args.propertyvaluefile))
    except SOSError as e:
        common.format_err_msg_and_raise(
            "set",
            "properties",
            e.err_text,
            e.err_code)

####################################################
#
####################################################
def system_parser(parent_subparser, common_parser):

    parser = parent_subparser.add_parser('system',
                                         description='ECS system CLI usage',
                                         parents=[common_parser],
                                         conflict_handler='resolve',
                                         help='Operations on system')
    subcommand_parsers = parser.add_subparsers(help='use one of sub-commands')

    get_logs_parser(subcommand_parsers, common_parser)

    get_alerts_parser(subcommand_parsers, common_parser)

    get_log_level_parser(subcommand_parsers, common_parser)

    set_log_level_parser(subcommand_parsers, common_parser)

    add_license_parser(subcommand_parsers, common_parser)

    get_license_parser(subcommand_parsers, common_parser)

    connectemc_ftps_parser(subcommand_parsers, common_parser)

    connectemc_smtp_parser(subcommand_parsers, common_parser)

    send_alert_parser(subcommand_parsers, common_parser)

    get_esrsconfig_parser(subcommand_parsers, common_parser)

    get_esrsconfig_deactivate_parser(subcommand_parsers, common_parser)

    get_properties_parser(subcommand_parsers, common_parser)

    set_properties_parser(subcommand_parsers, common_parser)

    get_properties_metadata_parser(subcommand_parsers, common_parser)
