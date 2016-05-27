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
  
 