#!/usr/bin/env python

import argparse, jmespath
from yac.lib.naming import get_stack_name, set_namer
from yac.lib.service import get_service, get_service_parmeters, get_service_alias
from yac.lib.stack import get_stack_templates, get_stack_name, get_ec2_ips, deploy_stack_files
from yac.lib.vpc import get_vpc_prefs
from yac.lib.container.api import get_connection_str
from yac.lib.container.build import build_image, get_image_name
from yac.lib.container.config import load_container_configs, get_aliases
from yac.lib.params import get_service_params

def main():
    
    parser = argparse.ArgumentParser(description='Build image for a service container unto a stack host.')     

    # required args   
    parser.add_argument('servicefile', help='location of the Servicefile (registry key or abspath)')
    parser.add_argument('name',        help='name of container to build')

    parser.add_argument('buildpath',   help='path to the dockerfile') 
        
    parser.add_argument('-d','--dryrun',  help='dry run the container start by printing rendered template to stdout', 
                                          action='store_true')
    parser.add_argument('-a',
                        '--alias',  help='service alias for the stack currently supporting this service (deault alias is per Servicefile)')     
    parser.add_argument('-p',
                        '--params',  help='path to a file containing additional, static, service parameters (e.g. vpc params, of service constants)') 
    # pull out args
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

    # get the service parameters for use with yac-ref's in service templates
    service_parmeters = get_service_parmeters(service_alias, service_params_input, 
                                              service_name, service_descriptor,
                                              servicefile_path, vpc_prefs)

    # get cloud formation template for the service requested and apply yac intrinsic 
    # functions (yac-ref, etc.) using  the service_parmeters
    stack_template = get_stack_templates(service_descriptor,
                                         service_parmeters)

    app_taskdefs = stack_template['Resources']['TaskDefs']['Properties']

    image_tag = jmespath.search("ContainerDefinitions[?Name=='%s'].Image"%args.name,app_taskdefs)[0]

    # get stack name
    stack_name = get_stack_name(service_parmeters)

    # get the ip address of the target host
    target_host_ips = get_ec2_ips( stack_name )

    if args.dryrun:

        user_msg = "%s(dry-run) Building the %s container image on %s using dockerfile at %s%s"%('\033[92m',
                                                        image_tag,
                                                        target_host_ips,
                                                        args.buildpath,                                                    
                                                        '\033[0m')
        print user_msg


    else:

        # build the container image on each host ...
        for target_host_ip in target_host_ips:

            user_msg = "%sBuilding the %s container image on %s using dockerfile at %s%s"%('\033[92m',
                                                        image_tag,
                                                        target_host_ip,
                                                        args.buildpath,                                                    
                                                        '\033[0m')

            raw_input(user_msg + "\nHit <enter> to continue..." )

            # get connection string for the docker remote api on the target host
            docker_api_conn_str = get_connection_str( target_host_ip )

            # get connection string for the docker remote api on the target host
            docker_api_conn_str = get_connection_str( target_host_ip )

            # build the image
            build_image( image_tag, args.buildpath, docker_api_conn_str )
