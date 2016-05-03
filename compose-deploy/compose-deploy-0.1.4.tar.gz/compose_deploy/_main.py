#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import subprocess
import sys

from compose import config
from compose.config import environment

import compose_deploy
from compose_deploy import remote


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
        return get_service_dicts(all_services)

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
    return get_service_dicts(services_out)


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
    filtered_services = {name: service for name, service in services.iteritems() if 'build' in service}

    _call_output('docker-compose build {}'.format(' '.join(filtered_services.iterkeys())))

    version = _get_version()

    for service_name, service_dict in filtered_services.iteritems():
        # Tag with proper version, they're already tagged latest from build
        image = service_dict['image']
        _call('docker tag {image}:latest {image}:{version}'.format(
                image=image,
                version=version
            )
        )


def push(config, services):
    """ Upload the defined services to their respective repositories.

    So's we can then tell the remote docker host to then pull and run them.
    """
    version = _get_version()
    for service_name, service_dict in services.iteritems():
        image = service_dict['image']
        things = {'image': image, 'version': version}
        _call_output('docker push {image}:latest'.format(**things))
        _call_output('docker push {image}:{version}'.format(**things))


def buildpush_main(command, args):
    _base = os.path.abspath(_search_up(args.file[0]))

    basedir = os.path.dirname(_base)

    config = get_config(basedir, args.file)

    actual_services = parse_services_arg(config, args.services)

    # Dispatch to appropriate function
    {'build': build, 'push': push}[command](config, actual_services)


def remote_main(args):
    remote.remote(args.server, args.command)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--version', '-V', action='version',
        version='%(prog)s {}'.format(compose_deploy.__version__))

    buildpush_parent = argparse.ArgumentParser(add_help=False)
    buildpush_parent.add_argument(
        '--file', '-f', nargs='+',
        default=['docker-compose.yml'],
        help='Same as the -f argument to docker-compose.')
    buildpush_parent.add_argument(
        'services', nargs='*',
        help='Which services to work on, all if empty')

    subparsers = parser.add_subparsers(dest='action')

    build_parser = subparsers.add_parser('build', parents=[buildpush_parent],  # noqa
                                         help='Build and tag the images')

    remote_parser = subparsers.add_parser(
        'remote',
        help='Run a shell with a connection to a remote docker server')
    remote_parser.add_argument(
        'server',
        help='The remote docker server to connect to; '
             'Uses openssh underneath so setup ~/.ssh/config appropriately, '
             'needs passwordless login '
             '(e.g. via ssh-agent or passwordless key)')
    remote_parser.add_argument(
        '--command', '-c', default=None,
        help='Command to run in the opened shell (and then immediately exit)')

    push_parser = subparsers.add_parser(  # noqa
        'push', parents=[buildpush_parent],
        help='Push the images to their repositories')

    args = parser.parse_args()

    if args.action in ['build', 'push']:
        buildpush_main(args.action, args)
    elif args.action in ['remote']:
        remote_main(args)


if __name__ == '__main__':
    main()
