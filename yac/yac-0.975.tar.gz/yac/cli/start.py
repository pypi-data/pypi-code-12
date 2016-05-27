#!/usr/bin/env python

import argparse, os, inspect, jmespath, json
from colorama import Fore, Style
from yac.lib.service import get_service, get_service_parmeters, get_service_alias
from yac.lib.stack import get_stack_templates, get_stack_name, get_ec2_ips, deploy_stack_files
from yac.lib.naming import set_namer
from yac.lib.container.start import start
from yac.lib.container.config import get_aliases, env_ec2_to_api, get_volumes_map
from yac.lib.container.config import get_port_bindings
from yac.lib.container.api import get_connection_str
from yac.lib.params import get_service_params
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

    # get the service parameters for use with yac-ref's in service templates
    service_parmeters = get_service_parmeters(service_alias, service_params_input, 
                                              service_name, service_descriptor,
                                              servicefile_path, vpc_prefs)

    # get cloud formation template for the service requested and apply yac intrinsic 
    # functions (yac-ref, etc.) using  the service_parmeters
    stack_template = get_stack_templates(service_descriptor,  
                                         service_parmeters)

    app_taskdefs = stack_template['Resources']['TaskDefs']['Properties']

    image_tags = jmespath.search("ContainerDefinitions[?Name=='%s'].Image"%args.name,app_taskdefs)
    if len(image_tags)!=1: 
        print("The container requested doesn't exist in the Servicefile. " +
              "Available containers include: %s."%jmespath.search("ContainerDefinitions[*].Name",app_taskdefs))
        exit()
    else:
        image_tag = image_tags[0]

    # get stack name
    stack_name = get_stack_name(service_parmeters)

    # get the ip address of the target host
    target_host_ips = get_ec2_ips( stack_name )

    if jmespath.search("ContainerDefinitions[?Name=='%s'].Environment"%args.name,app_taskdefs):
        ecs_env = jmespath.search("ContainerDefinitions[?Name=='%s'].Environment"%args.name,app_taskdefs)[0]
        env_variables = env_ec2_to_api(ecs_env)
    else:
        env_variables = {}

    # get the volumes map
    all_volumes = jmespath.search("Volumes",app_taskdefs)
    mount_points = jmespath.search("ContainerDefinitions[?Name=='%s'].MountPoints"%args.name,app_taskdefs)[0]
    volumes_map, volumes_bindings = get_volumes_map(all_volumes,mount_points)

    # get the volumes
    # volumes_bindings = jmespath.search("volumes[*].host.sourcePath",app_taskdefs)

    # get the port bindings for this container
    port_mappings = jmespath.search("ContainerDefinitions[?Name=='%s'].PortMappings"%args.name,app_taskdefs)[0]
    port_bindings = get_port_bindings(port_mappings)

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
