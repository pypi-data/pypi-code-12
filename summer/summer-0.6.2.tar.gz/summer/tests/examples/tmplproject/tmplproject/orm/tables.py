# -*- coding: utf-8 -*-
# Time-stamp: < tables.py (2016-01-20 09:04) >

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

"""
Contains table definitions for SQL Alchemy.
"""

from sqlalchemy import *

from summer import AbstractTableDefinitions

STRING_LONG = 100
STRING_SHORT = 30
STRING_CHAR = 1


class TableDefinitions(AbstractTableDefinitions):

    def __init__(self):
        AbstractTableDefinitions.__init__(self)
        self.category = None
        self.item = None
        self.category_x_item = None

    def define_tables(self, session_factory):
        metadata = session_factory.metadata

        self.category = Table(
            "category", metadata,
            Column("id", Integer, primary_key=True),
            Column("code", Unicode(STRING_SHORT), unique=True),
            Column("orderx", Integer, unique=True)
        )

        self.item = Table(
            "item", metadata,
            Column("id", Integer, primary_key=True),
            Column("code", Unicode(STRING_SHORT), unique=True),
            Column("value", Integer, nullable=False)
        )

        self.category_x_item = Table(
            "category_x_item", metadata,
            Column("category_id", Integer, ForeignKey("category.id")),
            Column("item_id", Integer, ForeignKey("item.id"))
        )
