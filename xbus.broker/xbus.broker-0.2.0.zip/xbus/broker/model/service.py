# -*- encoding: utf-8 -*-

from uuid import uuid4

from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import Unicode
from sqlalchemy import Boolean

from sqlalchemy.types import Text

from xbus.broker.model import metadata
from xbus.broker.model.types import UUID

__author__ = 'jgavrel'

service = Table(
    'service', metadata,
    Column('id', UUID, default=uuid4, primary_key=True),
    Column('name', Unicode(length=64), index=True, unique=True),
    Column('is_consumer', Boolean, server_default='FALSE'),
    Column('description', Text),
)
