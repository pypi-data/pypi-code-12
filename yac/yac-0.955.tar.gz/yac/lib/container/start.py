#!/usr/bin/env python

import sys
from docker import Client
from jinja2 import Template
import docker.utils, os, json, subprocess, urlparse
from api import get_docker_client, get_connection_str, find_container_by_name

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

# cp a file to an s3 buckert
# raises an Error if source file does not exists
# raises an subprocess.CalledProcessError if cp fails
def cp_to_s3(source_file, destination_s3_url):

    # make sure source file exists
    if os.path.exists(source_file):            

        # form aws cp command for this file
        aws_cmd = "aws s3 cp %s %s"%( source_file, destination_s3_url)

        subprocess.check_output( aws_cmd , stderr=subprocess.STDOUT, shell=True )

    else:
        raise Exception("Source file does not exist")

def load_image(image_source, image_name, docker_client):

    # if image source is docker hub, pull down image for this container
    # o.w. assume image is local
    if image_source == "hub":
        docker_client.pull( image_name )

# Load files specified in start configs
# Only s3 destinations are currently supported.
def load_files(files, template_vars):

    for file_key in files:

        this_file = files[file_key]

        # if destination is s3 bucket
        if is_s3_destination(this_file['dest']):

            # replace any template variables in the file before storing to S3
            with open(this_file['src'], 'r') as source_file:
                template = Template(source_file.read())

            # create a 'tmp' directory to hold the rendered source file
            if not os.path.exists('tmp'):
                os.makedirs('tmp')

            rendered_file = os.path.join('tmp','rendered_file')

            print 'rendered file: %s'%rendered_file
            with open(rendered_file, 'w') as outfile:
                outfile.write(template.render(template_vars))                

            # replace any template variables in the destination
            destination =  _render_string_variables(this_file['dest'],template_vars)

            cp_to_s3( rendered_file, destination)

        else:

            print '%s load was not performed. Only s3 destinations are currently supported.'%this_file['src']

# returns true if file to be loaded is configured for an s3 destination
def is_s3_destination( destination ):

    s3_destination = False

    # S3 destinations are URL's with s3 as the scheme
    # Use this to detect an S3 destination

    # attempt to parse the destination as a URL
    url_parts = urlparse.urlparse(destination)

    if (url_parts and url_parts.scheme and url_parts.scheme == 's3'):

        s3_destination = True

    return s3_destination


# converts a volumes_from list of container aliases to a list with container id's
def volumnes_from_with_ids(volumes_from, connection_str):

    volumes_from_ids = []

    for container_alias in volumes_from:

        # get the container
        container = find_container_by_name(container_alias, connection_str)

        volumes_from_ids.append(container.get('Id'))

    return volumes_from_ids


# start a container from an image
def start(
        image_tag,
        envs,
        alias,
        volumes_bindings,
        volume_mapping,
        volumes_from,
        port_bindings,
        connection_str,
        start_cmd,
        files_to_load,        
        template_vars,
        image_source='local',
        create_only=False):

    docker_client = get_docker_client( connection_str )

    # create the volumne host config from the volume_mapping
    volume_host_config = docker_client.create_host_config(binds=volume_mapping)

    # make sure container doesn't already exist
    existing_container = find_container_by_name( alias, connection_str )

    if existing_container:

        # stop container gracefully (giving it a full 30 secs)
        docker_client.stop(container=existing_container.get('Id'),
                           timeout=30)

        # remove container
        docker_client.remove_container( existing_container, force=True)

    # load the image on the host
    load_image(image_source, image_tag, docker_client)

    # load any files specified
    if files_to_load:

        load_files(files_to_load, template_vars)

    # render templates in environment variables
    rendered_envs = _render_env_variables(envs, template_vars)

    # create new container

    # if starting with a command other than the stock CMD in the dockerfile ...
    if start_cmd:

        container = docker_client.create_container(image=image_tag, 
                                                   name=alias, 
                                                   environment=rendered_envs,
                                                   volumes=volumes_bindings,                                               
                                                   host_config=volume_host_config,
                                                   command=start_cmd,
                                                   stdin_open=True,
                                                   tty=True)

    else:
        container = docker_client.create_container(image=image_tag, 
                                                   name=alias, 
                                                   environment=rendered_envs,
                                                   volumes=volumes_bindings,                                               
                                                   host_config=volume_host_config,
                                                   stdin_open=True,
                                                   tty=True)
    # start container
    if (container and container.get("Id") and not create_only):

        response = docker_client.start(container=container.get('Id'), 
                            port_bindings=port_bindings,
                            volumes_from = volumnes_from_with_ids(volumes_from,connection_str)  )

        if response:
            print "%s container created and started. Response from Docker: %s"%(alias,response)
        else:
            print "%s container created and started."%(alias)

    else:
        print "%s container was not started successfully"%alias
