#!/usr/bin/env python

import argparse, getpass, jmespath, json

from yac.lib.container.push import push_image
from yac.lib.service import get_service, get_service_parmeters, get_service_alias
from yac.lib.stack import get_stack_templates, get_stack_name, get_ec2_ips, deploy_stack_files
from yac.lib.naming import set_namer
from yac.lib.container.config import env_ec2_to_api, find_image_tag
from yac.lib.container.config import get_port_bindings
from yac.lib.container.api import get_connection_str
from yac.lib.vpc import get_vpc_prefs
from yac.lib.params import get_service_params, NULL_PARAMS, INVALID_PARAMS

def main():
    
    parser = argparse.ArgumentParser(description='Push container images from a remote host to docker hub.')

    # required args           
    parser.add_argument('servicefile', help='location of the Servicefile (registry key or abspath)')
    parser.add_argument('name',        help='name of container to push')
    parser.add_argument('-a',
                        '--alias',  help='service alias for the stack currently supporting this service (deault alias is per Servicefile)')
    parser.add_argument('-d','--dryrun',  help='dry run the container start by printing rendered template to stdout', 
                                          action='store_true')
    parser.add_argument('-p',
                        '--params',  help='path to a file containing additional, static, service parameters (e.g. vpc params, or service constants)') 
    parser.add_argument('--public',     help='connect using public IP address', 
                                        action='store_true') 

    args = parser.parse_args()

     # determine service defintion, complete service name, and service alias based on the args
    service_descriptor, service_name, servicefile_path = get_service(args.servicefile) 

    # get vpc preferences in place
    vpc_prefs = get_vpc_prefs()

    # set the resource namer to use with this service
    set_namer(service_descriptor, servicefile_path, vpc_prefs)

    # get the alias to use with this service
    service_alias = get_service_alias(service_descriptor,args.alias)

    # determine service params based on the params arg
    service_params_input, service_params_name = get_service_params(args.params)

    # abort if service params were not loaded successfully
    if args.params and service_params_name == NULL_PARAMS:
        print("The service params specified do not exist locally or in registry. Please try again.")
        exit()
    elif service_params_name == INVALID_PARAMS:
        print("The service params file specified failed validation checks. Please try again.")
        exit()

    # get the service parameters for use with yac-ref's in service templates
    service_parmeters = get_service_parmeters(service_alias, service_params_input, 
                                              service_name, service_descriptor,
                                              servicefile_path, vpc_prefs)

    # get cloud formation template for the service requested and apply yac intrinsic 
    # functions (yac-ref, etc.) using  the service_parmeters
    stack_template = get_stack_templates(service_descriptor, 
                                         service_parmeters)

    # get the tag for the container requested
    image_tag = find_image_tag(args.name,stack_template)

    # get stack name
    stack_name = get_stack_name(service_parmeters)

    # get the ip address of the target host
    target_host_ips = get_ec2_ips( stack_name ,"", args.public)

    if args.dryrun:

        # sanity check
        print('About to push image %s on %s to docker hub.'%(image_tag, target_host_ips))

    else:

        # get username/pwd/email for docker hub account
        hub_uname=raw_input('Hub username: ')
        hub_pwd=getpass.getpass('Hub password: ')
        hub_email=raw_input('Hub email: ')
    
        # start the container on each host ...
        for target_host_ip in target_host_ips:

            # get connection string for the docker remote api on the target host
            docker_api_conn_str = get_connection_str( target_host_ip )

            # sanity check
            raw_input('About to push image %s on %s to docker hub. Hit <enter> to continue...'%(image_tag, target_host_ip))

            # push the image
            push_image( image_tag,
                        hub_uname,
                        hub_pwd,
                        hub_email,
                        docker_api_conn_str )
