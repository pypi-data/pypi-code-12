#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import argparse
import os
import subprocess
import sys
import tempfile

import compose_deploy


DOCKER_HOST_PATH = os.path.join(os.environ['HOME'], '.docker-remote.{}.sock')

LISTEN_STRING = 'UNIX-LISTEN:{},reuseaddr,fork'.format(DOCKER_HOST_PATH)

SSH_COMMAND = '\'ssh {} "socat STDIO UNIX-CONNECT:/var/run/docker.sock"\''
REMOTE_STRING = 'EXEC:{}'.format(SSH_COMMAND)

BASH_RC = """
PS1="docker remote shell on '{server}' $ "
"""


def remote(server, command=None):
    os.environ['DOCKER_HOST'] = 'unix://{}'.format(DOCKER_HOST_PATH.format(server))
    os.environ['VIRTUALENVWRAPPER_PYTHON'] = '/usr/bin/python'

    if command is None:
        print('Starting a new shell with remote docker environment variable,\n'
              'exit this shell (usually ^D) as normal when you\'re done\n',
              file=sys.stderr)

    shell_string = ' '.join(['socat',
                             LISTEN_STRING.format(server),
                             REMOTE_STRING.format(server)
                             ])

    socket_forward_process = subprocess.Popen(shell_string, shell=True)

    to_run = [os.getenv('SHELL', '/bin/bash')]

    if command is not None:
        if isinstance(command, basestring):
            to_run.extend(['-c', command])
        else:
            to_run.extend(command)
    elif to_run[0].endswith('bash'):
        bashrc = tempfile.NamedTemporaryFile()
        bashrc.write(BASH_RC.format(server=server))
        bashrc.flush()
        to_run.extend(['--rcfile', bashrc.name])
    elif to_run[0].endswith('zsh'):
        os.environ['PS1'] = 'docker remote shell on "{}" $ '.format(server)
        to_run.extend(['-f', '-d'])

    shell_process = subprocess.Popen(
        to_run,
        stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)

    shell_process.wait()

    print("\nExited docker remote shell, cleaning up...", file=sys.stderr)

    socket_forward_process.terminate()
    socket_forward_process.wait()

    try:
        os.remove(DOCKER_HOST_PATH.format(server))
    except OSError:
        pass

    print("Done cleaning up", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', '-V', action='store_true',
                        help='Print version number and exit')
    parser.add_argument('server',
                        help='Server to point docker at')
    args = parser.parse_args()

    if args.version:
        print(compose_deploy.__version__)
        return

    return remote(args.server)

if __name__ == '__main__':
    main()
