# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2016 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Data models for employee work shifts
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy as sa
from sqlalchemy import orm

from .core import Base, uuid_column


class WorkedShift(Base):
    """
    Represents a shift actually *worked* by an employee.  (Either ``punch_in``
    or ``punch_out`` is generally assumed to be non-null.)
    """
    __tablename__ = 'employee_shift_worked'
    __table_args__ = (
        sa.ForeignKeyConstraint(['employee_uuid'], ['employee.uuid'], name='employee_shift_worked_fk_employee'),
        sa.ForeignKeyConstraint(['store_uuid'], ['store.uuid'], name='employee_shift_worked_fk_store'),
    )

    uuid = uuid_column()

    employee_uuid = sa.Column(sa.String(length=32), nullable=False)

    employee = orm.relationship(
        'Employee',
        doc="""
        Reference to the :class:`rattail.db.model.Employee` instance whose
        shift this is.
        """,
        backref=orm.backref('worked_shifts', doc="""
        Sequence of :class:`rattail.db.model.WorkedShift` instances for the
        employee.
        """))

    store_uuid = sa.Column(sa.String(length=32), nullable=True)

    store = orm.relationship(
        'Store',
        doc="""
        Reference to the :class:`rattail.db.model.Store` instance, representing
        the location at which the shift was worked, if applicable/known.
        """)

    punch_in = sa.Column(sa.DateTime(), nullable=True, doc="""
    UTC timestamp representing the punch-in time for the shift.
    """)

    punch_out = sa.Column(sa.DateTime(), nullable=True, doc="""
    UTC timestamp representing the punch-out time for the shift.
    """)
