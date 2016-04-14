#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import subprocess
import sys

from compose import config
from compose.config import environment

import compose_deploy


def _search_up(filename, stop_at_git=True):
    prefix = ''
    while True:
        path = os.path.join(prefix, filename)

        if os.path.isfile(path):
            return path
        elif prefix == '/' or (os.path.isdir(os.path.join(prefix, '.git')) and
                               stop_at_git):
            # insisting that .git is a dir means we will traverse out of git
            # submodules, a behaviour I desire
            raise IOError('{} not found here or any directory above here'
                          .format(filename))
        prefix = os.path.realpath(os.path.join(prefix, '..'))


def get_config(basedir, files):
    """ Returns the config object for the selected docker-compose.yml

    This is an instance of `compose.config.config.Config`.
    """
    config_details = config.find(
        basedir, files,
        environment.Environment.from_env_file(basedir))

    return config.load(config_details)


def get_images():
    pass


def parse_services_arg(config, arg_services):
    all_services = [service['name'] for service in config.services]

    def get_service_dicts(service_names):
        services_dict_out = {}

        for service_dict in config.services:
            name = service_dict['name']
            if name in service_names:
                services_dict_out[name] = service_dict

        return services_dict_out

    if not arg_services:
        return all_services, get_service_dicts(all_services)

    services_out = []
    added = []
    negated = []

    for service in arg_services:
        if service.startswith(':'):
            negated.append(service)
            service = service[1:]
        else:
            added.append(service)

        if service not in all_services:
            raise ValueError('Service "{}" not defined'.format(service))

    if not added:
        services_out.extend(all_services)

    services_out.extend(added)
    for service in negated:
        services_out.remove(service[1:])

    # Keep `services_out` for ordering
    return (services_out, get_service_dicts(services_out))


def _call(what, *args, **kwargs):
    # If they can modify the docker-compose file then they can already gain
    # root access without particular difficulty. "shell=True" is fine here.
    return subprocess.check_output(what, *args, shell=True, **kwargs)


def _call_output(what, *args, **kwargs):
    return subprocess.call(what, *args, shell=True, stdout=sys.stdout,
                           stderr=subprocess.STDOUT, **kwargs)


def _get_version():
    return _call('git describe --tags HEAD')


def build(config, services):
    """ Builds images and tags them appropriately.

    Where "appropriately" means with the output of:

        git describe --tags HEAD

    and 'latest' as well (so the "latest" image for each will always be the
    most recently built)
    """
    print services
    service_names, service_dicts = services
    _call_output('docker-compose build {}'.format(' '.join(service_names)))

    version = _get_version()

    for service_name in service_names:
        # Tag with proper version, they're already tagged latest from build
        image = service_dicts[service_name]['image']
        _call('docker tag {image}:latest {image}:{version}'.format(
                image=image,
                version=version
            )
        )


def push(config, services):
    """ Upload the defined services to their respective repositories.

    So's we can then tell the remote docker host to then pull and run them.
    """
    service_names, service_dicts = services
    version = _get_version()
    for service_name in service_names:
        image = service_dicts[service_name]['image']
        things = {'image': image, 'version': version}
        _call_output('docker push {image}:latest'.format(**things))
        _call_output('docker push {image}:{version}'.format(**things))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', '-V', action='store_true',
                        help='Print version number and exit')
    parser.add_argument('--file', '-f', nargs='+',
                        default=['docker-compose.yml'],
                        help='Same as the -f argument to docker-compose.')
    parser.add_argument('action', choices=['build', 'push'])
    parser.add_argument('services', nargs='*',
                        help='Which services to work on, all if empty')
    # TODO (KitB): How about we allow some mechanism for negating a service;
    # '-service' would work but would confuse argparse, maybe '!service'?

    args = parser.parse_args()

    if args.version:
        print compose_deploy.__version__
        return

    _base = os.path.abspath(_search_up(args.file[0]))

    basedir = os.path.dirname(_base)

    config = get_config(basedir, args.file)

    actual_services = parse_services_arg(config, args.services)

    # Dispatch to appropriate function
    {'build': build, 'push': push}[args.action](config, actual_services)

if __name__ == '__main__':
    main()
