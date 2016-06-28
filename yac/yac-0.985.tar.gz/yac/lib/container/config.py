#!/usr/bin/env python

import os, json
import jmespath
from jinja2 import Template

# xform env variables in taskdef format into a format compatible
# with docker api
def env_ec2_to_api(taskdef_envs):

    env_map = {}

    for env in taskdef_envs:
        env_map[env['Name']] = env['Value']

    return env_map

# xform volumes and mountpoints in taskdef format into a format compatible
# with docker api volume maps
def get_volumes_map(taskdef_volumes, taskdef_mountPoints):

    volume_map = {}
    volume_bindings = []
    for volume in taskdef_volumes:

        # example jmespath for 'home' volume is
        # [?sourceVolume=='home'].containerPath
        cp_search_str = "[?SourceVolume=='%s'].ContainerPath"%volume['Name']
        ro_search_str = "[?SourceVolume=='%s'].ReadOnly"%volume['Name']

        bind_path = jmespath.search(cp_search_str,taskdef_mountPoints)
        read_only = jmespath.search(ro_search_str,taskdef_mountPoints)

        # if we found a hit in the mount points, then add this volume to the 
        # volume map
        if (len(bind_path)==1 and len(read_only)==1):

            volume_bindings.append(volume['Host']['SourcePath'])
            
            volume_map[ volume['Host']['SourcePath'] ] = { 
                                    "bind": jmespath.search(cp_search_str,taskdef_mountPoints)[0],
                                    "ro":  jmespath.search(ro_search_str,taskdef_mountPoints)[0]
                                }


    return volume_map, volume_bindings

# xform port mapping in taskdef format into the port binding format compatible
# with docker api 
def get_port_bindings(taskdef_port_mappings):

    port_binding = {}

    for port_mapping in taskdef_port_mappings:
        port_binding[str(port_mapping['ContainerPort'])] = str(port_mapping['HostPort'])

    return port_binding

# render template variable in the container environment variables.
# template_vars contains key/value pairs of template variables
# that may appear in container_envs values
def _render_env_variables(container_envs, template_vars):
    
    for key in container_envs:
        container_envs[key] = _render_string_variables(container_envs[key],
                                                       template_vars)
    return container_envs

def _render_string_variables(string_w_variables, template_vars):

    template = Template(string_w_variables)
    return template.render(template_vars)

# load the config file which defines the container parameters
def load_container_configs(container_alias, 
                           config_file, 
                           env_dynamic = None):

    container_configs = load_configs(config_file)

    if container_alias in container_configs:
        configs = container_configs[container_alias]

    # render dynamic variables
    if env_dynamic:
        configs['envs'] = _render_env_variables(configs['envs'], env_dynamic)
    
    return configs


# taskdef_configs per ECS standard
def get_aliases(taskdef_configs):

    return jmespath.search('ContainerDefinitions[*].name', taskdef_configs)
  
def find_image_tag(name_tag, stack_template):

    image_tag = ""
    container_defs = get_container_defs(stack_template)

    image_tags = jmespath.search("[?Name=='%s'].Image"%name_tag,container_defs)

    # only one should be returned
    if len(image_tags)==1: 
        image_tag = image_tags[0]

    return image_tag

def get_container_envs(name_tag, stack_template):

    env_variables = []
    container_defs = get_container_defs(stack_template)

    ecs_env = jmespath.search("[?Name=='%s'].Environment"%name_tag,container_defs)

    if len(ecs_env) == 1:
        env_variables = env_ec2_to_api(ecs_env[0])

    return env_variables

def get_container_names(stack_template):

    container_names = []
    container_defs = get_container_defs(stack_template)

    container_names = jmespath.search("[*].Name",container_defs)

    return container_names

def get_container_volumes(name_tag, stack_template):

    app_taskdefs = get_task_defs(name_tag, stack_template)

    # print "%s"%json.dumps(app_taskdefs,indent=2)

    all_volumes = jmespath.search("Properties.Volumes",app_taskdefs)
    mount_points = jmespath.search("Properties.ContainerDefinitions[?Name=='%s'].MountPoints"%name_tag,app_taskdefs)[0]
    volumes_map, volumes_bindings = get_volumes_map(all_volumes,mount_points)

    return volumes_map, volumes_bindings

def get_container_ports(name_tag, stack_template):

    port_bindings = []
    container_defs = get_container_defs(stack_template)

    # get the port bindings for this container
    port_mappings = jmespath.search("[?Name=='%s'].PortMappings"%name_tag,container_defs)[0]
    port_bindings = get_port_bindings(port_mappings)

    return port_bindings

# get the task definitions for specific container
def get_task_defs(name_tag, stack_template):

    task_defs = {}

    if "Resources" in stack_template:

        resources = stack_template['Resources']

        resource_keys = resources.keys()

        for resource_key in resource_keys:

            if resources[resource_key]['Type'] == "AWS::ECS::TaskDefinition":

                container_defs = resources[resource_key]['Properties']['ContainerDefinitions']
                
                image_tags = jmespath.search("[?Name=='%s'].Image"%name_tag,container_defs)

                if len(image_tags)==1:

                    # this is the task definition of interest
                    task_defs = resources[resource_key]

    return task_defs 

def get_container_defs(stack_template):

    container_defs = []
    if "Resources" in stack_template:

        resources = stack_template['Resources']

        resource_keys = resources.keys()

        for resource_key in resource_keys:

            if resources[resource_key]['Type'] == "AWS::ECS::TaskDefinition":

                container_defs = container_defs + resources[resource_key]['Properties']['ContainerDefinitions']

    return container_defs 