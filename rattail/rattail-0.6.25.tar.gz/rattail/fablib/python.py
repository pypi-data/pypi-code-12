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
Fabric Library for Python
"""

from __future__ import unicode_literals
from __future__ import absolute_import

from contextlib import contextmanager

from fabric.api import sudo, run, prefix, cd, settings, env
from fabric.contrib.files import exists, append

from rattail.fablib import mkdir
from rattail.fablib import apt


def install_pip():
    """
    Install/upgrade the Pip installer for Python.
    """
    with settings(warn_only=True):
        result = sudo('which pip')
    if result.failed:
        apt.install('python-setuptools')
        sudo('easy_install pip')
        sudo('apt-get --assume-yes purge python-setuptools')
    apt.install('libffi-dev')
    pip('setuptools')
    pip('pip', 'wheel', 'ndg-httpsclient')


def pip(*packages):
    """
    Install one or more packages via ``pip install``.
    """
    packages = ["'{0}'".format(p) for p in packages]
    sudo('pip install --upgrade {0}'.format(' '.join(packages)))


def install_virtualenvwrapper(workon_home='/srv/envs', user='root'):
    """
    Install the `virtualenvwrapper`_ system, with the given ``workon`` home,
    owned by the given user.
    """
    mkdir(workon_home, owner=user)
    pip('virtualenvwrapper')

    configure_virtualenvwrapper('root', workon_home)
    if user != 'root':
        configure_virtualenvwrapper(user, workon_home)
    configure_virtualenvwrapper(env.user, workon_home)


def configure_virtualenvwrapper(user, workon_home='/srv/envs'):
    """
    Configure virtualenvwrapper for the given user account.
    """
    home = sudo('echo $HOME', user=user)
    home = home.rstrip('/')

    def update(script):
        script = '{0}/{1}'.format(home, script)
        if not exists(script):
            sudo('touch {0}'.format(script))
            sudo('chown {0}:{0} {1}'.format(user, script))
        append(script, 'export WORKON_HOME={0}'.format(workon_home), use_sudo=True)
        append(script, 'source /usr/local/bin/virtualenvwrapper.sh', use_sudo=True)

    update('.profile')
    update('.bashrc')


def mkvirtualenv(name, user=None, upgrade_pip=True):
    """
    Make a new Python virtual environment.
    """
    sudo('mkvirtualenv {0}'.format(name))
    if upgrade_pip:
        with workon(name):
            pip('pip', 'setuptools', 'wheel', 'ndg-httpsclient')
    if user:
        with cdvirtualenv(name):
            mkdir('app/log', owner='{0}:{0}'.format(user))


@contextmanager
def workon(name):
    """
    Context manager to prefix your command(s) with the ``workon`` command.
    """
    with prefix('workon {0}'.format(name)):
        yield


@contextmanager
def cdvirtualenv(name, subdirs=[], workon_home='/srv/envs'):
    """
    Context manager to prefix your command(s) with the ``cdvirtualenv`` command.
    """
    if isinstance(subdirs, basestring):
        subdirs = [subdirs]
    path = '{0}/{1}'.format(workon_home, name)
    if subdirs:
        path = '{0}/{1}'.format(path, '/'.join(subdirs))
    with workon(name):
        with cd(path):
            yield
