from pyramid import security

from xbus.monitor.auth import DATA_CLEARING_GROUP
from xbus.monitor.auth import MANAGER_GROUP
from xbus.monitor.models.data_clearing import EventType
from xbus.monitor.models.data_clearing import Item
from xbus.monitor.models.data_clearing import ItemColumn
from xbus.monitor.models.data_clearing import ItemJoin
from xbus.monitor.models.data_clearing import ItemType
from xbus.monitor.resources.root import RootFactory


_manager_acl = [
    (security.Allow, MANAGER_GROUP, 'create'),
    (security.Allow, MANAGER_GROUP, 'read'),
    (security.Allow, MANAGER_GROUP, 'update'),
    (security.Allow, MANAGER_GROUP, 'delete'),
]


class _GenericCollectionFactory(RootFactory):
    """Factory for collections of records; provides:
    - sqla_model: sqlalchemy class.
    """

    sqla_model = None  # To be overridden by derived classes.

    # Give managers full access to all models by default. The ACL may be
    # specialized in the derived class.
    __acl__ = _manager_acl


class CollectionFactory_cl_event_type(_GenericCollectionFactory):
    sqla_model = EventType


class CollectionFactory_cl_item(_GenericCollectionFactory):
    sqla_model = Item

    __acl__ = _manager_acl + [
        (security.Allow, DATA_CLEARING_GROUP, 'create'),
        (security.Allow, DATA_CLEARING_GROUP, 'read'),
        (security.Allow, DATA_CLEARING_GROUP, 'update'),
        (security.Allow, DATA_CLEARING_GROUP, 'delete'),
    ]


class CollectionFactory_cl_item_column(_GenericCollectionFactory):
    sqla_model = ItemColumn


class CollectionFactory_cl_item_join(_GenericCollectionFactory):
    sqla_model = ItemJoin


class CollectionFactory_cl_item_type(_GenericCollectionFactory):
    sqla_model = ItemType
