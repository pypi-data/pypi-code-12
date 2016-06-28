#!/usr/bin/env python

import argparse, os, inspect, jmespath, json
from colorama import Fore, Style
from yac.lib.service import get_service, get_service_parmeters, get_service_alias
from yac.lib.stack import get_stack_templates, get_stack_name, get_ec2_ips, deploy_stack_files
from yac.lib.naming import set_namer
from yac.lib.container.start import start
from yac.lib.container.api import get_connection_str
from yac.lib.container.config import get_aliases, env_ec2_to_api, get_container_volumes
from yac.lib.container.config import get_container_names
from yac.lib.container.config import find_image_tag, get_container_ports, get_container_envs
from yac.lib.params import get_service_params, NULL_PARAMS, INVALID_PARAMS
from yac.lib.vpc import get_vpc_prefs


def main():

    parser = argparse.ArgumentParser(description='Start a container per the container defintion in the provided Servicefile')

    # required args                                         
    parser.add_argument('servicefile', help='location of the Servicefile (registry key or abspath)')
    parser.add_argument('name',        help='name of container to start') 

    parser.add_argument('-p',
                        '--params',  help='path to a file containing additional, static, service parameters (e.g. vpc params, of service constants)') 

    parser.add_argument('-s', '--source', 
                        help='image source for this container (hub=dockerhub, local=image on host filesystem)', 
                        choices=['hub','local'], 
                        default='local')

    parser.add_argument('-a',
                        '--alias',  help='service alias for the stack currently supporting this service (deault alias is per Servicefile)')                                       
    parser.add_argument('-c', '--cmd', 
                        help='run this cmd instead of the stock container CMD (see associated Dockerfile)')
    parser.add_argument('-d','--dryrun',  help='dry run the container start by printing rendered template to stdout', 
                                          action='store_true')
    parser.add_argument('--public',     help='connect using public IP address', 
                                        action='store_true')     


    args = parser.parse_args()

     # determine service defintion, complete service name, and service alias based on the args
    service_descriptor, service_name, servicefile_path = get_service(args.servicefile) 

    # abort if service_descriptor was not loaded successfully
    if not service_descriptor:
        print("The Servicefile input does not exist locally or in registry. Please try again.")
        exit()

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

    image_tag = find_image_tag(args.name,stack_template)

    if not image_tag:

        container_names = get_container_names(stack_template)

        print("The container requested doesn't exist in the Servicefile. " +
              "Available containers include:\n%s."%pp_list(container_names))
        exit()

    # get stack name
    stack_name = get_stack_name(service_parmeters)

    # get the ip address of the target host
    target_host_ips = get_ec2_ips( stack_name , "", args.public)

    # get the env variables associated with the container
    env_variables = get_container_envs(args.name,stack_template)

    # get the volumes map
    volumes_map, volumes_bindings = get_container_volumes(args.name, stack_template)

    # get the port bindings for this container
    port_bindings = get_container_ports(args.name, stack_template)

    source = 'local' if args.source=='local' else 'remote (hub)'

    if args.dryrun:

        print(Fore.GREEN)

        user_msg = "Starting the %s container on %s using the %s image %s"%(args.name,
                                                                            target_host_ips,
                                                                            source, 
                                                                            image_tag)
        if args.cmd:
            user_msg = user_msg + "\nUsing command: %s"%args.cmd

        # do a dry-run by printing the stack template and stack parameters to stdout
        print "environment variables ... \n%s"%json.dumps(env_variables,indent=2)
        print "volumes map ... \n%s"%json.dumps(volumes_map,indent=2)
        print "volumes bindings ... \n%s"%json.dumps(volumes_bindings,indent=2)
        print "port bindings ... \n%s"%json.dumps(port_bindings,indent=2)
        print user_msg

        print(Style.RESET_ALL)

    else:

        # deploy any files specified by the service
        deploy_stack_files(service_descriptor, service_parmeters, servicefile_path)

        # start the container on each host ...
        for target_host_ip in target_host_ips:

            print(Fore.GREEN)

            user_msg = "Starting the %s container on %s using the %s image %s"%(args.name,
                                                                                target_host_ip,
                                                                                source, 
                                                                                image_tag)

            if args.cmd:
                user_msg = user_msg + "\nUsing command: %s"%args.cmd

            raw_input(user_msg + "\nHit <enter> to continue..." )

            print(Style.RESET_ALL) 

            # get connection string for the docker remote api on the target host
            docker_api_conn_str = get_connection_str( target_host_ip )

            # start the container
            start(
                image_tag=image_tag,
                envs=env_variables,
                alias=args.name,
                volume_mapping=volumes_map,
                volumes_bindings=volumes_bindings,
                port_bindings=port_bindings,
                connection_str=docker_api_conn_str,
                start_cmd=args.cmd,
                image_source=args.source,
                template_vars={},
                files_to_load=[],
                volumes_from=[],
                create_only=False) 

def pp_list(list):
    str = ""
    for item in list:
        str = str + '* %s\n'%item

    return str