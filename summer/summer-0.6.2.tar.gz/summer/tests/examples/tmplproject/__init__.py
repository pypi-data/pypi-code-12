# -*- coding: utf-8 -*-
# Time-stamp: < __init__.py (2016-02-08 06:25) >

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
# Time-stamp: < README.txt (2015-03-29 16:47) >

"""Presents a template of a real *Python* project and shows features of the
summer framework.

Requirements:

* *SQLite* -- uses in memory db available with no special config.
* *LDAP* -- uses simple ldap db holding user accounts.

SQL database is simple and uses just two entities with m:n relationship
between Category <--> Item.

LDAP support can be turned off, if not, you will need to set up your own
ldap server, see :file:`ldap/sample.local.sh` for details.

As well as with :doc:`example-appcontext`, there are some obvious
configuration files:

* standard Python logging config :file:`logging.cfg`
* summer framework config :file:`summer.cfg`
* custom application config :file:`custom.cfg`

Project is now organized with one single package, so please look at:

* :file:`tmplprojecttest.py`
* :file:`tmplproject/main.py`
* :file:`tmplproject/appcontext.py`

"""
