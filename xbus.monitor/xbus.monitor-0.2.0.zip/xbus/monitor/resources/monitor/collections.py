from pyramid import security

from xbus.monitor.auth import MANAGER_GROUP
from xbus.monitor.auth import UPLOADER_GROUP
from xbus.monitor.models.monitor import EmissionProfile
from xbus.monitor.models.monitor import Emitter
from xbus.monitor.models.monitor import EmitterProfile
from xbus.monitor.models.monitor import Envelope
from xbus.monitor.models.monitor import Event
from xbus.monitor.models.monitor import EventError
from xbus.monitor.models.monitor import EventErrorTracking
from xbus.monitor.models.monitor import EventNode
from xbus.monitor.models.monitor import EventTracking
from xbus.monitor.models.monitor import EventType
from xbus.monitor.models.monitor import InputDescriptor
from xbus.monitor.models.monitor import Role
from xbus.monitor.models.monitor import Service
from xbus.monitor.models.monitor import User
from xbus.monitor.resources.root import RootFactory


_manager_acl = [
    (security.Allow, MANAGER_GROUP, 'create'),
    (security.Allow, MANAGER_GROUP, 'read'),
    (security.Allow, MANAGER_GROUP, 'update'),
    (security.Allow, MANAGER_GROUP, 'delete'),
]

_manager_and_uploader_acl = _manager_acl + [
    (security.Allow, UPLOADER_GROUP, 'read'),
]


class _GenericCollectionFactory(RootFactory):
    """Factory for collections of records; provides:
    - sqla_model: sqlalchemy class.
    """

    sqla_model = None  # To be overridden by derived classes.

    # Give managers full access to all models by default. The ACL may be
    # specialized in the derived class.
    __acl__ = _manager_acl


class CollectionFactory_emission_profile(_GenericCollectionFactory):
    sqla_model = EmissionProfile

    __acl__ = _manager_and_uploader_acl


class CollectionFactory_emitter(_GenericCollectionFactory):
    sqla_model = Emitter

    __acl__ = _manager_and_uploader_acl


class CollectionFactory_emitter_profile(_GenericCollectionFactory):
    sqla_model = EmitterProfile


class CollectionFactory_envelope(_GenericCollectionFactory):
    sqla_model = Envelope

    __acl__ = _manager_and_uploader_acl


class CollectionFactory_event(_GenericCollectionFactory):
    sqla_model = Event

    __acl__ = _manager_and_uploader_acl


class CollectionFactory_event_error(_GenericCollectionFactory):
    sqla_model = EventError

    __acl__ = _manager_and_uploader_acl


class CollectionFactory_event_error_tracking(_GenericCollectionFactory):
    sqla_model = EventErrorTracking

    __acl__ = _manager_and_uploader_acl


class CollectionFactory_event_node(_GenericCollectionFactory):
    sqla_model = EventNode


class CollectionFactory_event_tracking(_GenericCollectionFactory):
    sqla_model = EventTracking

    __acl__ = _manager_and_uploader_acl


class CollectionFactory_event_type(_GenericCollectionFactory):
    sqla_model = EventType


class CollectionFactory_input_descriptor(_GenericCollectionFactory):
    sqla_model = InputDescriptor

    __acl__ = _manager_and_uploader_acl


class CollectionFactory_role(_GenericCollectionFactory):
    sqla_model = Role


class CollectionFactory_service(_GenericCollectionFactory):
    sqla_model = Service


class CollectionFactory_user(_GenericCollectionFactory):
    sqla_model = User
