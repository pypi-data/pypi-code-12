#!/usr/bin/env python

import os, argparse
from yac.lib.stack import get_stack_name, get_ec2_ips
from yac.lib.vpc import get_vpc_prefs

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

def main():

    parser = argparse.ArgumentParser('ssh into a stack ec2 instance')

    parser.add_argument('app',  help='the app alias')
    parser.add_argument('env',  help='the env', choices=['dev', 'stage', 'prod', 'archive'])
    parser.add_argument('path', help='path to the private key file for this app',
                                type=lambda x: is_valid_file(parser, x))
    parser.add_argument('-s','--search',  help='search string, to support multiple EC2 instances in the same auto-scaling group')

    # pull out args
    args = parser.parse_args()

    # get any vpc preferences in place
    vpc_prefs = get_vpc_prefs()

    vpc_params = {}
    if 'vpc-params' in vpc_prefs:
        vpc_params = vpc_prefs['vpc-params']

    vpc_params.update({"service-alias": {"value": args.app}, "env": {"value": args.env}} )

    # get the name of the stack that corresponds to this app and env
    stack_name = get_stack_name(vpc_params)

    # get the IP address of the ec2 instance for this stack
    ec2_ips = get_ec2_ips(stack_name, args.search)

    # get the user to ssh in as
    if args.app != 'hipchat':
        ssh_user='core'
    else:
        ssh_user='admin'

    if (ec2_ips and len(ec2_ips)==1):
        ec2_ip = ec2_ips[0]

        # prepare ssh command
        ssh_cmd = "ssh -i %s %s@%s"%(args.path,ssh_user,ec2_ip)

        # ssh in
        os.system(ssh_cmd)

        print "future versions will remove 22 ingress here..."

    elif (ec2_ips and len(ec2_ips)>1):

        print 'Found multiple EC2 address for the %s app in the %s env. Consider adding a search string.'%(args.app, args,env)

    else:

        print 'Could not find address for the %s app in the %s env'%(args.app, args,env)

