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

"""Cell plugins related to http://readthedocs.org"""

from pypimonitor.cell import Jinja2

class Readthedocs(Jinja2):
    """Readthedocs.org build badge."""

    keyword = 'readthedocs'
    title = 'Doc'
    default = {
        'lang': 'en',
        }
