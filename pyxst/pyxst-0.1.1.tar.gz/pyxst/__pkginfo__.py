# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of yams.
#
# yams is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# yams is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with yams. If not, see <http://www.gnu.org/licenses/>.
"""PyXST packaging information."""
__docformat__ = "restructuredtext en"

# pylint: disable-msg=W0622

# package name
modname = 'pyxst'

# release version
numversion = (0, 1, 1)
version = '.'.join(str(num) for num in numversion)

# license and copyright
license = 'LGPL'

# short and long description
description = "XML Schema Tools for Python"

# author name and email
author = "Logilab"
author_email = "devel@logilab.fr"

# home page
web = "https://www.logilab.org/project/%s" % modname

# mailing list
mailinglist = 'mailto://python-projects@lists.logilab.org'

# download place
ftp = "http://download.logilab.org/pub/%s" % modname

# executable
scripts = []

install_requires = [
    'lxml',
]
