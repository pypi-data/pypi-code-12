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
Fabric library for Rattail itself
"""

from __future__ import unicode_literals
from __future__ import absolute_import

from fabric.api import sudo, env

from rattail.fablib import make_deploy, make_system_user, mkdir


deploy = make_deploy(__file__)


def bootstrap_rattail(home='/var/lib/rattail', uid=None, shell='/bin/bash', alias=True):
    """
    Bootstrap a basic Rattail software environment.
    """
    make_system_user('rattail', home=home, uid=uid, shell=shell, alias=alias)
    sudo('adduser {0} rattail'.format(env.user))

    mkdir('/etc/rattail')
    mkdir('/srv/rattail')
    mkdir('/var/log/rattail', owner='rattail:rattail', mode='0775')

    mkdir('/srv/rattail/init')
    deploy('filemon', '/srv/rattail/init/filemon')
    deploy('datasync', '/srv/rattail/init/datasync')
    deploy('bouncer', '/srv/rattail/init/bouncer')
