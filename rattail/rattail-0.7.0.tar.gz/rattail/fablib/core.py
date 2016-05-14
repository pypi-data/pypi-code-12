# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2014 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Core Fabric Library
"""

from __future__ import unicode_literals

import os
import tempfile

from fabric.api import sudo, run, local, env, settings, put as fab_put
from fabric.contrib.files import append, upload_template as fab_upload_template

from mako.template import Template


def get_debian_version():
    """
    Fetch the version of Debian running on the target system.
    """
    version = unicode(run('cat /etc/debian_version'))
    version = '.'.join(version.split('.')[:2])
    return float(version)


def mkdir(paths, owner='root:root', mode=None):
    """
    Recursively make one or more directories.
    """
    if isinstance(paths, basestring):
        paths = [paths]
    sudo('mkdir --parents {0}'.format(' '.join(paths)))
    sudo('chown {0} {1}'.format(owner, ' '.join(paths)))
    if mode is not None:
        sudo('chmod {0} {1}'.format(mode, ' '.join(paths)))


def make_system_user(name='rattail', home='/srv/rattail', uid=None, shell=None, alias=False):
    """
    Make a new system user account, with the given home folder and shell path.
    Optionally add a mail alias to root as well.
    """
    with settings(warn_only=True):
        result = sudo('getent passwd {0}'.format(name))
    if result.failed:
        uid = '--uid {0}'.format(uid) if uid else ''
        shell = '--shell {0}'.format(shell) if shell else ''
        sudo('adduser --system --home {0} --group {1} {2} {3}'.format(home, name, uid, shell))
    if alias:
        add_mail_alias(name)


def add_mail_alias(local_name, aliased_to='root'):
    append('/etc/aliases', '{}: {}'.format(local_name, aliased_to), use_sudo=True)
    sudo('newaliases')


def put(local_path, remote_path, owner='root:root', **kwargs):
    """
    Put a file on the server, and set its ownership.
    """
    if 'mode' not in kwargs:
        kwargs.setdefault('mirror_local_mode', True)
    kwargs['use_sudo'] = True
    fab_put(local_path, remote_path, **kwargs)
    sudo('chown {0} {1}'.format(owner, remote_path))


def upload_template(local_path, remote_path, owner='root:root', **kwargs):
    """
    Upload a template to the server, and set its ownership.
    """
    if 'mode' not in kwargs:
        kwargs.setdefault('mirror_local_mode', True)
    kwargs['use_sudo'] = True
    fab_upload_template(local_path, remote_path, **kwargs)
    sudo('chown {0} {1}'.format(owner, remote_path))


def upload_mako_template(local_path, remote_path, owner='root:root', **kwargs):
    """
    Render a local file as a Mako template, and upload the result to the server.
    """
    template = Template(filename=local_path)

    temp_dir = tempfile.mkdtemp(prefix='rattail.fablib.')
    temp_path = os.path.join(temp_dir, os.path.basename(local_path))
    with open(temp_path, 'wb') as f:
        f.write(template.render(env=env))
    os.chmod(temp_path, os.stat(local_path).st_mode)

    put(temp_path, remote_path, **kwargs)
    os.remove(temp_path)
    os.rmdir(temp_dir)


class Deployer(object):

    def __init__(self, deploy_path, last_segment='deploy'):
        if not os.path.isdir(deploy_path):
            deploy_path = os.path.abspath(os.path.join(os.path.dirname(deploy_path), last_segment))
        self.deploy_path = deploy_path

    def __call__(self, local_path, remote_path, **kwargs):
        self.deploy(local_path, remote_path, **kwargs)

    def deploy(self, local_path, remote_path, **kwargs):
        local_path = '{0}/{1}'.format(self.deploy_path, local_path)
        if local_path.endswith('.template'):
            upload_template(local_path, remote_path, context=env, **kwargs)
        elif local_path.endswith('.mako'):
            upload_mako_template(local_path, remote_path, **kwargs)
        else:
            put(local_path, remote_path, **kwargs)

    def sudoers(self, local_path, remote_path, mode='0440', **kwargs):
        self.deploy(local_path, '/tmp/sudoers', mode=mode)
        sudo('mv /tmp/sudoers {0}'.format(remote_path))


def make_deploy(deploy_path, last_segment='deploy'):
    """
    Make a ``deploy()`` function, for uploading files to the server.

    During a deployment, one usually needs to upload certain additional files
    to the server.  It's also often necessary to dynamically define certain
    settings etc. within these files.  The :func:`upload_template()` and
    :func:`put()` functions, respectively, handle uploading files which do and
    do not require dynamic variable substitution.

    The return value from ``make_deploy()`` is a function which will call
    ``put()`` or ``upload_template()`` based on whether or not the file path
    ends with ``'.template'``.

    To make the ``deploy()`` function even simpler for the caller, it will
    assume a certain context for local file paths.  This means one only need
    provide a base file name when calling ``deploy()``, and it will be
    interpreted as relative to the function's context path.

    The ``deploy_path`` argument is used to establish the context path for the
    function.  If it is a folder path, it will be used as-is; otherwise it will
    be constructed by joining the parent folder of ``deploy_path`` with the
    value of ``last_segment``.

    Typical usage then is something like::

       from rattail.fablib import make_deploy

       deploy = make_deploy(__file__)

       deploy('rattail/init-filemon', '/etc/init.d/rattail-filemon',
              mode='0755')

       deploy('rattail/rattail.conf.template', '/etc/rattail.conf')

    This shows what is intended to be typical, i.e. where ``__file__`` is the
    only argument required for ``make_deploy()``.  For the above to work will
    require you to have something like this file structure, where
    ``fabfile.py`` is the script which contains the above code::

       myproject/
       |-- fabfile.py
       |-- deploy/
           `-- rattail/
               |-- init-filemon
               |-- rattail.conf.template
    """
    return Deployer(deploy_path, last_segment)


def rsync(host, *paths):
    """
    Runs rsync as root, for the given host and file paths.
    """
    for path in paths:
        assert path.startswith('/')
        path = path.rstrip('/')
        cmd = 'SSH_AUTH_SOCK=$SSH_AUTH_SOCK rsync -aP --del root@{0}:{1}/ {1}'.format(host, path)
        with settings(forward_agent=True):
            sudo(cmd, shell=False)
