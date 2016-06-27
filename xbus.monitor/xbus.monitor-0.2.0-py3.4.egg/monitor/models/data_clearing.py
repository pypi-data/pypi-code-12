"""SQLAlchemy description of the database model used by the data clearing
interface.
"""

import datetime
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import LargeBinary
from sqlalchemy import Sequence
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from uuid import UUID as base_UUID

from xbus.monitor.consumers import get_consumer_clearing_session
from xbus.monitor.models.types import UUID


def get_session(request):
    """Get the SQLAlchemy session object bound to the data clearing database
    specified by a "cl_consumer" request parameter referencing an Xbus consumer
    ID.
    """
    return get_consumer_clearing_session(request.params.get('cl_consumer'))


# CRUD operators to be defined on event types, when they have no lookup.
EVENT_TYPE_CRUD_OPS = ['create', 'update', 'delete']

OPTYPES = [
    'IGNORE', 'SELECT', 'WRITE', 'CREATE', 'S_CREATE', 'W_CREATE', 'DELETE'
]

COLUMN_DATA_TYPES = [
    'ANY', 'M2O'
]

ITEM_STATES = [
    'new', 'old', 'cleared'
]


def serialize(value):
    """Serialize types JSON cannot handle."""

    if isinstance(value, bytes):
        return None

    if isinstance(value, datetime.date):
        return datetime.date.isoformat(value)

    if isinstance(value, datetime.datetime):
        return datetime.datetime.isoformat(value)

    if isinstance(value, base_UUID):
        return str(value)

    return value


def as_dict(obj):
    return {c.name: serialize(getattr(obj, c.name)) for c in obj.__table__.c}

Base = declarative_base()
Base.as_dict = as_dict


class EventType(Base):

    __tablename__ = 'event_type'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=64), nullable=False, index=True, unique=True)

    crud_op = Column(Enum(*EVENT_TYPE_CRUD_OPS, name='event_type_crud_ops'))

    has_clearing = Column(Boolean())
    has_lookup = Column(Boolean())

    target_collection = Column(String())

    test_changes = Column(Boolean(), default=True)

    item_types = relationship(
        'ItemType', lazy='dynamic', secondary='event_type_item_type_rel',
        backref=backref('event_types', lazy='dynamic')
    )


class ItemType(Base):

    __tablename__ = 'item_type'

    optype_enum = Enum(*OPTYPES, name='optype')

    id = Column(Integer, primary_key=True)
    object_name = Column(String(length=128), nullable=False)
    model_name = Column(Text, nullable=False)
    primary_table_name = Column(String(length=128))
    display_name = Column(String(length=256))
    id_column_name = Column(String(length=128), default=False)
    optype = Column(optype_enum, nullable=False)
    priority = Column(Integer)
    description = Column(Text)


class ItemColumn(Base):

    __tablename__ = 'item_column'

    type_fkey = ForeignKey('item_type.id', ondelete='CASCADE')
    related_type_fkey = ForeignKey('item_type.id', ondelete='SET NULL')
    join_fkey = ForeignKey('item_join.id', ondelete='SET NULL')
    data_type_enum = Enum(*COLUMN_DATA_TYPES, name='column_data_type')

    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, type_fkey, nullable=False)
    join_id = Column(Integer, join_fkey)
    attribute_name = Column(String(length=128), nullable=False)
    field_name = Column(Text, nullable=False)
    column_name = Column(String(length=128))
    display_name = Column(String(length=256))
    data_type = Column(data_type_enum, nullable=False, default='ANY')
    related_type_id = Column(Integer, related_type_fkey)
    is_external_key = Column(Boolean, nullable=False, default=False)
    is_clearable = Column(Boolean, nullable=False, default=True)
    is_dest_default = Column(Boolean, nullable=False, default=False)
    is_protected = Column(Boolean, nullable=False, default=False)
    is_required = Column(Boolean, nullable=False, default=False)

    type = relationship(
        'ItemType', foreign_keys=[type_id],
        backref=backref('columns', lazy='dynamic')
    )
    related_type = relationship('ItemType', foreign_keys=[related_type_id])
    join = relationship('ItemJoin', backref=backref('columns', lazy='dynamic'))

    Index('idx_type_field', 'type_id', 'field_name', unique=True)


class ItemJoin(Base):

    __tablename__ = 'item_join'

    type_fkey = ForeignKey('item_type.id', ondelete='CASCADE')
    join_fkey = ForeignKey('item_join.id', ondelete='CASCADE')

    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, type_fkey, nullable=False)
    parent_id = Column(Integer, join_fkey)
    display_name = Column(String(length=256))
    left_column_name = Column(String(length=128))
    right_table_name = Column(String(length=128))
    right_column_name = Column(String(length=128))

    type = relationship('ItemType', backref=backref('joins', lazy='dynamic'))
    parent = relationship(
        'ItemJoin', remote_side=[id],
        backref=backref('children', lazy='dynamic')
    )


class Item(Base):

    __tablename__ = 'item'

    event_type_fkey = ForeignKey('event_type.id', ondelete='RESTRICT')
    type_fkey = ForeignKey('item_type.id', ondelete='RESTRICT')
    item_state_enum = Enum(*ITEM_STATES, name='item_state_data_type')

    id = Column(Integer, primary_key=True)
    event_type_id = Column(Integer, event_type_fkey, nullable=False)
    type_id = Column(Integer, type_fkey, nullable=False)
    event_id = Column(UUID, nullable=False)
    dest_id = Column(Integer)
    state = Column(item_state_enum, nullable=False, default='new')
    batch = Column(Integer, Sequence('item_batch_seq'))
    recv_date = Column(DateTime, nullable=False)
    sent_date = Column(DateTime)
    source_data = Column(LargeBinary, nullable=False)
    dest_data = Column(LargeBinary)
    out_data = Column(LargeBinary)
    unclearable_data = Column(LargeBinary)

    type = relationship('ItemType', backref=backref('items', lazy='dynamic'))

    Index('idx_type_dest_id_batch', 'type_id', 'dest_id', 'batch')


class EventTypeItemTypeRel(Base):

    __tablename__ = 'event_type_item_type_rel'

    event_type_fkey = ForeignKey('event_type.id', ondelete='CASCADE')
    item_type_fkey = ForeignKey('item_type.id', ondelete='CASCADE')

    event_type_id = Column(Integer, event_type_fkey, primary_key=True)
    item_type_id = Column(Integer, item_type_fkey, primary_key=True)
