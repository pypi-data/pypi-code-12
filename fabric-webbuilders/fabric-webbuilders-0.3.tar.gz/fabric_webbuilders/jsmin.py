# -*- coding: utf-8 -*-
#
# This file is part of fabric-webbuilders (https://github.com/mathiasertl/fabric-webbuilders).
#
# fabric-webbuilders is free software: you can redistribute it and/or modify it under the terms of
# the GNU General Public License as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# fabric-webbuilders is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See
# the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with fabric-webbuilders.
# If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from fabric.api import local

from fabric_webbuilders.base import MinifyTask


class MinifyJSTask(MinifyTask):
    default_suffix = 'js'

    def minify(self, files, dest):
        local('uglifyjs %s %s --output %s' % (' '.join(files), self.get_options(), self.dest))
