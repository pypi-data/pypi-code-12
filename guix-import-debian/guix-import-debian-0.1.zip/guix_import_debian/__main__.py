# -*- coding: utf-8 -*-
# Guix Import Debian --- Import helper for GNU Guix
# Copyright © 2016 Hartmut Goebel <h.goebel@crazy-compilers.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from . import pkginfo2package, __version__

import argparse
import tempfile

def debian():
    parser = argparse.ArgumentParser(
        version='%(prog)s {0}'.format(__version__))
    parser.add_argument('--tempdir', default=tempfile.gettempdir(),
                        help="Directory used to cache temporary files.")
    parser.add_argument('packagename', help="name of the package to import")
                        
    args = parser.parse_args()
    pkginfo2package(args.packagename, args.tempdir)
