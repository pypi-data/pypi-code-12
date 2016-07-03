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

"""Some base cell plugins."""

from pypimonitor.cell import Cell, Jinja2

class Empty(Cell):
    """Empty cell."""

    keyword = "empty"

    def render(self, context, package, cell):
        return ""

class Html(Cell):
    """Render raw HTML code as the cell."""

    keyword = 'html'
    required = ['html']

    def render(self, context, package, cell):
        return cell['html']

class Error(Cell):
    """Render an error."""

    keyword = 'error'

    def render(self, context, package, cell):
        return self.render_error(
            context,
            self.keyword,
            package,
            "Undefined cell '{}'.".format(cell['cell']),
            )

class Link(Jinja2):
    """Render a link."""

    keyword = 'link'
    required = ['href']

    def render(self, context, package, cell):
        if 'content' not in cell:
            cell['content'] = cell['href']
        return super().render(context, package, cell)

class Color(Jinja2):
    """Render a color square."""

    keyword = 'color'
