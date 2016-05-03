__author__ = 'dcortes'

from schematics.models import Model
from schematics.types import StringType, IntType
from schematics.types.compound import ModelType


class Country(Model):

    name = StringType()
    code = StringType(default="")