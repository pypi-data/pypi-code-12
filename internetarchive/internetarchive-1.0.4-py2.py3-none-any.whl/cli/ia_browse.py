# -*- coding: utf-8 -*-
#
# The internetarchive module is a Python/CLI interface to Archive.org.
#
# Copyright (C) 2012-2016 Internet Archive
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

"""browse!

usage:
    ia browse --help
    ia browse <identifier>

options:
    -h, --help
"""
from __future__ import absolute_import, print_function, unicode_literals

import webbrowser

from docopt import docopt


def main(argv, session):
    args = docopt(__doc__, argv=argv)
    item = session.get_item(args['<identifier>'])
    url = '{0}//archive.org/details/{1}'.format(session.protocol, item.identifier)
    r = webbrowser.open(url)
    print(dir(r))
