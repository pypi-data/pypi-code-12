# -*- coding: utf-8 -*-
# Time-stamp: < __init__.py (2016-02-14 12:26) >

# Copyright (C) 2009-2016 Martin Slouf <martin.slouf@sourceforge.net>
#
# This file is a part of Summer.
#
# Summer is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

"""Presents very simple context usage.

Uses simple in memory SQLite database and demonstrates basic configuration,
context creation, and proxying manager objects with
:py:func:`summer.txaop.transactional` annotation.

There are several notable config files worth mentioning:

* standard Python logging config :file:`logging.cfg`
* summer framework config :file:`summer.cfg`
* custom application config :file:`custom.cfg`

Please look at those config files and read through heavily commented
example source files (actually unit tests from *summer* source code).

"""
