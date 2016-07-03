# pypimonitor — An HTML dashboard to monitor your python packages
# Copyright (C) 2016 Louis Paternault
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Cell plugins related to http://gitlab.com"""
import os

from pypimonitor.cell import Jinja2

class Gitlab(Jinja2):
    """Abstract cell plugin related to http://gitlab.com"""

    @property
    def template(self):
        return os.path.join("cells", "gitlab", "{}.html".format(self.keyword))

class CI(Gitlab):
    """Gitlab-ci badge."""

    keyword = "gitlabci"
    title = "GitlabCI"
    default = {
        'server': 'http://gitlab.com',
        }
    required = ['user']

