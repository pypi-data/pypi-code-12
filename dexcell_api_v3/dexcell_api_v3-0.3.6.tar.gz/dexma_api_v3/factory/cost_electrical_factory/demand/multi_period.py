__author__ = 'dcortes'

from schematics.models import Model
from schematics.types import StringType, FloatType, IntType
from schematics.types.compound import ListType, ModelType

from dexma_api_v3.factory.cost_electrical_factory.periods.multiperiod_contracted_periods import multiperiodContractedPeriod
from dexma_api_v3.factory.custom_types.dateISO3601Type import DateISO3601Type


class MULTI_PERIOD(Model):

    type = StringType(required=True)
    total = FloatType(required=True)
    units = StringType(required=True)
    days_gap = IntType(required=True)

    from_ = DateISO3601Type(required=True)
    to = DateISO3601Type(required=True)
    periods = ListType(ModelType(multiperiodContractedPeriod, required=True))
