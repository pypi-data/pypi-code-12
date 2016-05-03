__author__ = 'dcortes'

from schematics.models import Model
from schematics.types.compound import ModelType, ListType

from period_properties import PeriodProperty


class PricesConfig(Model):

    period_properties = ListType(ModelType(PeriodProperty))
    single_contracted_load = ModelType(PeriodProperty)