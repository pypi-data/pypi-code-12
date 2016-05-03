__author__ = 'dcortes'

from schematics.models import Model
from schematics.types import StringType, BooleanType, IntType


class PeriodProperty(Model):

    name = StringType(required=True)
    contracted_load = IntType(required=True)
    period_key = StringType(required=True)
    reactive_penalty = BooleanType(required=True)
