#!/usr/bin/python

# Copyright (c) 2012-14 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.


# importing python system modules

import argparse
import os
from common import SOSError
import sys

# importing ECS modules

import authentication
import common
import tenant
import metering
import monitoring
import virtualarray
import sysmanager
import datastore
import objectuser
import mgmtuserinfo
import failedzones
import objectvpool
import secretkeyuser
import keystore
import socket
import datafabric
import cashead
import bucket
import baseurl
import virtualdatacenter
import virtualdatacenterdata
import nodes
#import reporting
import billing
import passwordgroup
import nfs

import dashboard
import transformation
import vdckeystore
import config
from config import Config

import warnings


warnings.filterwarnings(
    'ignore',
    message='BaseException.message has been deprecated as of Python 2.6',
    category=DeprecationWarning,
    module='argparse')

# Fetch ECS environment variables defined (if any)

#ecs_ip = common.getenv('ECS_HOSTNAME')
#ecs_port = common.getenv('ECS_PORT')
#ecs_ui_port = common.getenv('ECS_UI_PORT')
#ecs_cli_dir = common.getenv('ECS_CLI_INSTALL_DIR')
cfg = config.loadCurrentConfig()
ecs_ip = '127.0.0.1'
ecs_port = '4443'
ecs_user = 'root'
ecs_cookiedir = '.'
ecs_cookieFile = None
ecs_cookieFilePath = None

if cfg is not None:
    ecs_user = cfg[Config.USER]
    ecs_ip = cfg[Config.HOSTNAME]
    ecs_port = cfg[Config.PORT]
    ecs_cookiedir = cfg[Config.COOKIEDIR]
    ecs_cookieFile = cfg[Config.USER] + 'cookie'
    ecs_cookieFilePath = cfg[Config.COOKIEDIR] + '/' + cfg[Config.USER] + 'cookie'
    print("Running with config profile: " + config.getActiveConfigName())
    print("user: " + ecs_user + "\thost:port: " + ecs_ip + ":" + ecs_port)
else:
    print("Running without an acive config profile")


# parser having common arguments across all modules

common_parser = argparse.ArgumentParser()
common_parser.add_argument('-hostname', '-hn',
                           metavar='<hostname>',
                           default=ecs_ip,
                           dest='ip',
                           help='Hostname (fully qualifiled domain name) ' +
                                'or IPv4 address (i.e. 192.0.2.0) or IPv6 address' +
                                ' inside quotes and brackets ' +
                                '(i.e. "[2001:db8::1]") of ECS')
common_parser.add_argument('-port', '-po',
                           type=int,
                           metavar='<port_number>',
                           default=ecs_port,
                           dest='port',
                           help='port number of ECS')
'''
common_parser.add_argument('-portui', '-pu',
                           type=int,
                           metavar='<ui_port_number>',
                           default=ecs_ui_port,
                           dest='uiPort',
                           help='https port number of ECS Portal UI')
'''
common_parser.add_argument('-cf', '-cookiefile',
                           help='Full name of cookiefile',
                           default = ecs_cookieFilePath,
                           metavar='<cookiefile>',
                           dest='cookiefile')

# main commandline parser

main_parser = argparse.ArgumentParser(
    description='ECS CLI usage',
    parents=[common_parser],
    conflict_handler='resolve')
main_parser.add_argument('-v', '--version', '-version',
                         action='version',
                         version='%(prog)s 1.0',
                         help='show version number of program and exit')

def display_version():
    print common.get_ecscli_version()


# register module specific parsers with the common_parser
module_parsers = main_parser.add_subparsers(help='Use One Of Commands')

config.cli_config_parser(module_parsers)
authentication.authenticate_parser(module_parsers, ecs_user, ecs_cookieFile, ecs_cookiedir, ecs_ip, ecs_port)
authentication.authentication_parser(module_parsers, common_parser)
baseurl.baseurl_parser(module_parsers, common_parser)
billing.billing_parser(module_parsers, common_parser)
bucket.bucket_parser(module_parsers, common_parser)
cashead.cashead_parser(module_parsers, common_parser)
datafabric.datafabric_commodity_datastore_parser(module_parsers, common_parser)
#datafabric.datafabric_service_parser(module_parsers, common_parser)
#datafabric.datafabric_node_parser(module_parsers, common_parser)
failedzones.failedzone_parser(module_parsers, common_parser)
keystore.keystore_parser(module_parsers, common_parser)
metering.meter_parser(module_parsers, common_parser)
mgmtuserinfo.mgmtuserinfo_parser(module_parsers, common_parser)
monitoring.monitor_parser(module_parsers, common_parser)
nodes.nodes_parser(module_parsers, common_parser)
objectuser.objectuser_parser(module_parsers, common_parser)
objectvpool.objectvpool_parser(module_parsers, common_parser)
nfs.nfs_parser(module_parsers, common_parser)
#reporting.report_parser(module_parsers, common_parser)
secretkeyuser.secretkeyuser_parser(module_parsers, common_parser)
sysmanager.system_parser(module_parsers, common_parser)
tenant.namespace_parser(module_parsers, common_parser)
virtualarray.varray_parser(module_parsers, common_parser)
virtualdatacenterdata.vdc_data_parser(module_parsers, common_parser)
virtualdatacenter.vdc_parser(module_parsers, common_parser)
passwordgroup.passwordgroup_parser(module_parsers, common_parser)

dashboard.dashboard_parser(module_parsers, common_parser)
transformation.transformation_parser(module_parsers, common_parser)
vdckeystore.vdc_keystore_parser(module_parsers, common_parser)

def printitOld(result):
    if(result):
        if isinstance(result, list):
            for record in result:
                print record
        else:
            print result


def printit(result, silent=False):
    if(result):
        if silent == True:
            return
        print(common.format_json_object(result))

def runCmd(silent = True):
    result = None
    # Parse Command line Arguments and execute the corresponding routines
    try:
        if(len(sys.argv) > 1 and (sys.argv[1] == '-v' or
                                          sys.argv[1] == '-version' or
                                          sys.argv[1] == '--version')):
            display_version()

        else:
            args = main_parser.parse_args()
            common.COOKIE = args.cookiefile
            result = args.func(args)
            if silent == False:
                printit(result)

    except SOSError as e:
        sys.stderr.write(e.err_text + "\n")
        sys.exit(e.err_code)
    except (EOFError, KeyboardInterrupt):
        sys.stderr.write("\nUser terminated request\n")
        sys.exit(SOSError.CMD_LINE_ERR)

    return result

if __name__ == '__main__':
    runCmd(False)
