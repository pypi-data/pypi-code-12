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
Rattail config extension for Tailbone
"""

from __future__ import unicode_literals, absolute_import

from rattail.config import ConfigExtension as BaseExtension
from rattail.db.config import configure_session

from tailbone.db import Session


class ConfigExtension(BaseExtension):
    """
    Rattail config extension for Tailbone.  Does the following:

     * Configures the main Tailbone database session so that it records
       changes, if the config file so dictates.
    """
    key = 'tailbone'

    def configure(self, config):
        configure_session(config, Session)
