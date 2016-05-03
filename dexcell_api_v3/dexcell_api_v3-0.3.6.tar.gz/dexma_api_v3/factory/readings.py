__author__ = 'dcortes'

from schematics.models import Model
from schematics.types import StringType
from schematics.types.compound import ModelType, ListType

from readings_factory.value import Value


class Readings(Model):

    units = StringType(required=True)
    timezone = StringType(required=True)
    values = ListType(ModelType(Value))



