# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2015 Lance Edgar
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
Fabric Library for SSH
"""

from __future__ import unicode_literals
from __future__ import absolute_import

from fabric.api import *
from fabric.contrib.files import exists, sed

from rattail.fablib import mkdir
from rattail.fablib.python import cdvirtualenv


def configure_ssh(restrict_root=True):
    """
    Configure the OpenSSH service.
    """
    if restrict_root:
        sed('/etc/ssh/sshd_config', r'^PermitRootLogin yes$', r'PermitRootLogin no', use_sudo=True)
    sed('/etc/ssh/sshd_config', r'^#PasswordAuthentication yes$', r'PasswordAuthentication no', use_sudo=True)
    sudo('service ssh restart')


def establish_identity(envname, comment, user='rattail', home='/var/lib/rattail'):
    """
    Generate a SSH key pair and configure it for local use.
    """
    home = home.rstrip('/')
    sshdir = '{0}/.ssh'.format(home)
    owner='{0}:{0}'.format(user)
    mkdir(sshdir, owner=owner, mode='0700')
    with cd(sshdir):
        if not exists('authorized_keys'):
            sudo('touch authorized_keys')
        sudo('chown {0} authorized_keys'.format(owner))
        sudo('chmod 0600 authorized_keys')
    with cdvirtualenv(envname, 'app'):
        mkdir('ssh', owner=owner, mode='0700')
    with cdvirtualenv(envname, 'app/ssh'):
        if not exists('id_rsa', use_sudo=True):
            sudo("ssh-keygen -C '{0}' -P '' -f id_rsa".format(comment))
            sudo('cat id_rsa.pub >> {0}/authorized_keys'.format(sshdir))
        sudo('chown {0} id_rsa*'.format(owner))
