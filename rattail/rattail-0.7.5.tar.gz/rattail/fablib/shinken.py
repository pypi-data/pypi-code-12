# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2016 Lance Edgar
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
Fabric tools for Shinken
"""

from __future__ import unicode_literals, absolute_import

from fabric.api import cd

from rattail.fablib import make_deploy, mkdir


deploy = make_deploy(__file__)


def install_shinken_pack(dest='/etc/shinken/packs'):
    """
    Install the 'rattail' pack for use with a Shinken system.
    """
    with cd(dest):
        mkdir('software/rattail')
        deploy('shinken/rattail.pack', 'software/rattail/rattail.pack')
        deploy('shinken/templates.cfg', 'software/rattail/templates.cfg')
        deploy('shinken/commands.cfg', 'software/rattail/commands.cfg')
        # mkdir('software/rattail/services')
        # deploy('shinken/services/datasync.cfg', 'software/rattail/services/datasync.cfg')
