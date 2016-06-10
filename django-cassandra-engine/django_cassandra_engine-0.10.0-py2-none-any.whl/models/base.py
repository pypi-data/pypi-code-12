import inspect

import six

from django.apps import apps
from cassandra.cqlengine.models import (
    ModelMetaClass as BaseModelMetaClass,
    BaseModel
)

from django_cassandra_engine.models.options import Options


class ModelMetaClass(BaseModelMetaClass):

    def __new__(mcs, name, bases, attrs):
        module = attrs.get('__module__')
        meta = attrs.pop('Meta', None)
        klass = super(ModelMetaClass, mcs).__new__(mcs, name, bases, attrs)
        abstract = getattr(meta, 'abstract', klass.__abstract__)
        # Look for an application configuration to attach the model to.
        app_config = apps.get_containing_app_config(module)
        if app_config:
            app_label = app_config.label
            klass.add_to_class('_meta', Options(meta, app_label))
            if not abstract:
                klass._meta.apps.register_model(klass._meta.app_label, klass)
                klass._meta.concrete_model = klass

        return klass

    def add_to_class(cls, name, value):
        # We should call the contribute_to_class method only if it's bound
        if not inspect.isclass(value) and hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


@six.add_metaclass(ModelMetaClass)
class Model(BaseModel):
    _deferred = False

    __abstract__ = True
    """
    *Optional.* Indicates that this model is only intended to be used as a base class for other models.
    You can't create tables for abstract models, but checks around schema validity are skipped during class construction.
    """

    __table_name__ = None
    """
    *Optional.* Sets the name of the CQL table for this model. If left blank, the table name will be the name of the model, with it's module name as it's prefix. Manually defined table names are not inherited.
    """

    __keyspace__ = None
    """
    Sets the name of the keyspace used by this model.
    """

    __options__ = None
    """
    *Optional* Table options applied with this model

    (e.g. compaction, default ttl, cache settings, tec.)
    """

    __discriminator_value__ = None
    """
    *Optional* Specifies a value for the discriminator column when using model inheritance.
    """
