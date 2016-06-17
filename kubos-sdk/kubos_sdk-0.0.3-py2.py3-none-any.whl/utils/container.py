#!/usr/bin/python

import sys
import docker
from docker import Client


def get_cli():
    if sys.platform.startswith('linux'):
        c = Client(base_url='unix://var/run/docker.sock') #use with docker-engine
    elif sys.platform.startswith('darwin'):
        c = docker.from_env(assert_hostname=False) #use with docker-machine

    check_docker_status(c)
    return c


def check_docker_status(client):
    try:
        client.ping()
    except:
        print >>sys.stderr, 'Error: Unable to communicate with the Docker service. Please ensure this service is running and you have permission to access it.'
        sys.exit(1)


def pass_through(*args):
    cwd = os.getcwd()
    cli = container.get_cli()
    python = '/usr/bin/python'
    sdk_script = '/kubos-sdk/kubos-sdk.py'
    arg_list = list(args)
    arg_list.insert(0, python)
    arg_list.insert(1, sdk_script)

    image_name = "%s:%s" % (container_repo, container_tag)
    container_data = cli.create_container(image=image_name, command=arg_list, working_dir=cwd, tty=True)
    container_id = container_data['Id'].encode('utf8')
    if container_data['Warnings']:
        print "Warnings: ", container_data['Warnings']
    status_spinner = start_spinner()

    cli.start(container_id, binds={
        cwd : {
            'bind': cwd,
            'ro': False
        }
    })
    container_output = cli.logs(container=container_id, stream=True)
    for entry in container_output:
        sys.stdout.write(entry)

    cli.stop(container_id)
    cli.remove_container(container_id)

    if sys.platform.startswith('linux'):
        fix_permissions()
    stop_spinner(status_spinner)


def fix_permissions(*args):
    cwd = os.getcwd()
    cli = container.get_cli()
    userstr = "%s:%s" % (os.getuid(), os.getgid())
    arg_list = list()
    arg_list.insert(0, "chown")
    arg_list.insert(1, userstr)
    arg_list.insert(2, cwd)
    arg_list.insert(3, "-R")

    image_name = "%s:%s" % (container_repo, container_tag)
    container_data = cli.create_container(image=image_name, command=arg_list, working_dir=cwd, tty=True)

    container_id = container_data['Id'].encode('utf8')
    if container_data['Warnings']:
        print "Warnings: ", container_data['Warnings']

    cli.start(container_id, binds={
        cwd : {
            'bind': cwd,
            'ro': False
        }
    })
    container_output = cli.logs(container=container_id, stream=True)
    for entry in container_output:
        sys.stdout.write(entry)

    cli.stop(container_id)
    cli.remove_container(container_id)


