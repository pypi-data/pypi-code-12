# -*- coding: utf-8 -*-
# Time-stamp: < mappings.py (2016-01-20 09:04) >

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

from sqlalchemy.orm import *

from summer import AbstractClassMappings

from .model import FooEntity


class ClassMappings(AbstractClassMappings):

    def __init__(self):
        AbstractClassMappings.__init__(self)
        self.foo_entity = None

    def create_mappings(self, session_factory):
        tables = session_factory.table_definitions
        self.foo_entity = mapper(FooEntity, tables.foo_entity)
